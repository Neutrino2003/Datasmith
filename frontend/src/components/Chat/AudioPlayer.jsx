import React, { useState, useRef } from 'react';
import { Volume2, VolumeX, Loader2 } from 'lucide-react';
import './AudioPlayer.css';

export const AudioPlayer = ({ text }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const utteranceRef = useRef(null);

    const speak = () => {
        if (!('speechSynthesis' in window)) {
            console.error('TTS not supported');
            return;
        }

        // Stop if already playing
        if (isPlaying) {
            window.speechSynthesis.cancel();
            setIsPlaying(false);
            return;
        }

        setIsLoading(true);

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Get a good voice
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'));
        if (englishVoice) {
            utterance.voice = englishVoice;
        }

        utterance.onstart = () => {
            setIsLoading(false);
            setIsPlaying(true);
        };

        utterance.onend = () => {
            setIsPlaying(false);
        };

        utterance.onerror = () => {
            setIsLoading(false);
            setIsPlaying(false);
        };

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    if (!text || text.startsWith('Error')) return null;

    return (
        <button
            className={`audio-player-button ${isPlaying ? 'playing' : ''}`}
            onClick={speak}
            title={isPlaying ? 'Stop' : 'Read aloud'}
            type="button"
        >
            {isLoading ? (
                <Loader2 size={14} className="animate-spin" />
            ) : isPlaying ? (
                <VolumeX size={14} />
            ) : (
                <Volume2 size={14} />
            )}
        </button>
    );
};
