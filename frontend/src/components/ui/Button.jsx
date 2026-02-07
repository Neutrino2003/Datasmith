import React from 'react';
import './Button.css';

export const Button = ({
    children,
    variant = 'primary',
    className = '',
    fullWidth = false,
    ...props
}) => {
    return (
        <button
            className={`btn btn-${variant} ${fullWidth ? 'btn-full' : ''} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};
