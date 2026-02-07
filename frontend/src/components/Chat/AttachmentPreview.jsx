import React from 'react';
import { X, FileText, Image, Music, Video, File } from 'lucide-react';
import './AttachmentPreview.css';

const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return Image;
    if (type.startsWith('audio/')) return Music;
    if (type.startsWith('video/')) return Video;
    if (type === 'application/pdf') return FileText;
    return File;
};

const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

export const AttachmentPreview = ({ files, onRemove }) => {
    if (!files || files.length === 0) return null;

    return (
        <div className="attachment-preview">
            {files.map((file, index) => {
                const Icon = getFileIcon(file);
                const isImage = file.type.startsWith('image/');

                return (
                    <div key={index} className="attachment-chip">
                        {isImage && file.preview ? (
                            <img
                                src={file.preview}
                                alt={file.name}
                                className="attachment-thumbnail"
                            />
                        ) : (
                            <div className="attachment-icon">
                                <Icon size={20} />
                            </div>
                        )}
                        <div className="attachment-info">
                            <span className="attachment-name">{file.name}</span>
                            <span className="attachment-size">{formatFileSize(file.size)}</span>
                        </div>
                        <button
                            className="attachment-remove"
                            onClick={() => onRemove(index)}
                            type="button"
                        >
                            <X size={14} />
                        </button>
                    </div>
                );
            })}
        </div>
    );
};
