import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, Code2, FileText, Sparkles, Paperclip, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Button } from '../ui/Button';
import { Textarea } from '../ui/Input';
import { API } from '../../services/api';
import { AttachmentPreview } from './AttachmentPreview';
import { VoiceInput } from './VoiceInput';
import { AudioPlayer } from './AudioPlayer';
import './ChatInterface.css';

// Available slash commands
const COMMANDS = [
    { command: '/code_analysis', label: 'Code Analysis', description: 'Analyze code for bugs and complexity', icon: Code2 },
    { command: '/summarize', label: 'Summarize', description: 'Create a structured summary', icon: FileText },
    { command: '/tldr', label: 'TL;DR', description: 'Quick summary in bullet points', icon: Sparkles },
];

const Message = ({ role, content }) => (
    <div className={`message-bubble ${role === 'user' ? 'message-user' : 'message-ai'}`}>
        {role === 'ai' && <AudioPlayer text={content} />}
        {role === 'user' ? (
            <div style={{ whiteSpace: 'pre-wrap' }}>{content}</div>
        ) : (
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                            <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                                {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                        ) : (
                            <code className={className} {...props}>{children}</code>
                        );
                    }
                }}
            >
                {content}
            </ReactMarkdown>
        )}
    </div>
);

const CommandDropdown = ({ visible, commands, selectedIndex, onSelect }) => {
    if (!visible || commands.length === 0) return null;
    return (
        <div className="command-dropdown">
            {commands.map((cmd, index) => {
                const Icon = cmd.icon;
                return (
                    <div key={cmd.command} className={`command-item ${index === selectedIndex ? 'selected' : ''}`} onClick={() => onSelect(cmd)}>
                        <Icon size={16} className="command-icon" />
                        <div className="command-content">
                            <span className="command-label">{cmd.command}</span>
                            <span className="command-description">{cmd.description}</span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showCommands, setShowCommands] = useState(false);
    const [filteredCommands, setFilteredCommands] = useState(COMMANDS);
    const [selectedCommandIndex, setSelectedCommandIndex] = useState(0);
    const [attachments, setAttachments] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    useEffect(scrollToBottom, [messages]);

    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);
        if (value.startsWith('/')) {
            const filtered = COMMANDS.filter(cmd => cmd.command.toLowerCase().startsWith(value.toLowerCase()));
            setFilteredCommands(filtered);
            setShowCommands(true);
            setSelectedCommandIndex(0);
        } else {
            setShowCommands(false);
        }
    };

    const selectCommand = (cmd) => {
        setInput(cmd.command + ' ');
        setShowCommands(false);
        textareaRef.current?.focus();
    };

    const handleVoiceTranscript = (transcript) => {
        setInput(prev => prev + transcript + ' ');
    };

    // File handling
    const addFiles = useCallback((files) => {
        const newFiles = Array.from(files).map(file => {
            const preview = file.type.startsWith('image/') ? URL.createObjectURL(file) : null;
            return Object.assign(file, { preview });
        });
        setAttachments(prev => [...prev, ...newFiles]);
    }, []);

    const removeAttachment = (index) => {
        setAttachments(prev => {
            const file = prev[index];
            if (file.preview) URL.revokeObjectURL(file.preview);
            return prev.filter((_, i) => i !== index);
        });
    };

    const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
    const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if ((!input.trim() && attachments.length === 0) || loading) return;

        setShowCommands(false);
        const userContent = input + (attachments.length ? ` [${attachments.length} file(s) attached]` : '');
        const userMsg = { role: 'user', content: userContent };
        setMessages(prev => [...prev, userMsg]);

        const textToSend = input;
        const filesToSend = [...attachments];
        setInput('');
        setAttachments([]);
        setLoading(true);

        try {
            let response;
            if (filesToSend.length > 0) {
                // Use multipart upload
                response = await API.uploadWithMessage(textToSend, filesToSend, 'default-session');
            } else {
                response = await API.post('/analyze', { text: textToSend, session_id: 'default-session' });
            }
            setMessages(prev => [...prev, { role: 'ai', content: response.response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'ai', content: `Error: ${error.message}` }]);
        } finally {
            setLoading(false);
            filesToSend.forEach(f => f.preview && URL.revokeObjectURL(f.preview));
        }
    };

    const handleKeyDown = (e) => {
        if (showCommands && filteredCommands.length > 0) {
            if (e.key === 'ArrowDown') { e.preventDefault(); setSelectedCommandIndex(i => i < filteredCommands.length - 1 ? i + 1 : 0); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setSelectedCommandIndex(i => i > 0 ? i - 1 : filteredCommands.length - 1); }
            else if (e.key === 'Tab' || e.key === 'Enter') { e.preventDefault(); selectCommand(filteredCommands[selectedCommandIndex]); }
            else if (e.key === 'Escape') { setShowCommands(false); }
        } else if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className={`chat-container ${isDragging ? 'dragging' : ''}`} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
            <div className="chat-messages">
                {messages.length === 0 && (
                    <div className="welcome-message">
                        <h3>Welcome to Datasmith AI</h3>
                        <p>Chat, attach files, or use voice input</p>
                        <div className="command-hints">
                            {COMMANDS.map(cmd => {
                                const Icon = cmd.icon;
                                return (
                                    <div key={cmd.command} className="command-hint" onClick={() => { setInput(cmd.command + ' '); textareaRef.current?.focus(); }}>
                                        <Icon size={14} /><span>{cmd.command}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
                {messages.map((msg, idx) => <Message key={idx} {...msg} />)}
                {loading && (
                    <div className="message-bubble message-ai" style={{ width: 'fit-content', display: 'flex', alignItems: 'center' }}>
                        <Loader2 size={20} className="animate-spin" />
                        <span style={{ marginLeft: '8px' }}>Thinking...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-wrapper">
                <CommandDropdown visible={showCommands} commands={filteredCommands} selectedIndex={selectedCommandIndex} onSelect={selectCommand} />
                <AttachmentPreview files={attachments} onRemove={removeAttachment} />
                <form onSubmit={handleSubmit} className="chat-input-area">
                    <input type="file" ref={fileInputRef} style={{ display: 'none' }} multiple onChange={(e) => addFiles(e.target.files)} />
                    <button type="button" className="attach-button" onClick={() => fileInputRef.current?.click()} title="Attach files">
                        <Paperclip size={18} />
                    </button>
                    <div style={{ flex: 1 }}>
                        <Textarea
                            ref={textareaRef}
                            placeholder="Type a message, / for commands, or attach files..."
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            style={{ resize: 'none', minHeight: '44px' }}
                        />
                    </div>
                    <VoiceInput onTranscript={handleVoiceTranscript} disabled={loading} />
                    <Button type="submit" disabled={loading || (!input.trim() && attachments.length === 0)}>
                        <Send size={18} />
                    </Button>
                </form>
            </div>

            {isDragging && (
                <div className="drop-overlay">
                    <div className="drop-content">
                        <Paperclip size={48} />
                        <p>Drop files here</p>
                    </div>
                </div>
            )}
        </div>
    );
};
