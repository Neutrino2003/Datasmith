import React, { forwardRef } from 'react';
import './Input.css';

export const Input = ({ label, className = '', ...props }) => {
    return (
        <div className="input-wrapper">
            {label && <label className="input-label">{label}</label>}
            <input className={`input-field ${className}`} {...props} />
        </div>
    );
};

export const Textarea = forwardRef(({ label, className = '', ...props }, ref) => {
    return (
        <div className="input-wrapper">
            {label && <label className="input-label">{label}</label>}
            <textarea ref={ref} className={`input-field ${className}`} {...props} />
        </div>
    );
});

Textarea.displayName = 'Textarea';
