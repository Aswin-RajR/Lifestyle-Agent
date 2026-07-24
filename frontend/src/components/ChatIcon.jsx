import React from 'react';
import logoImg from '../assets/ar_advisor_logo.png';

export function ChatIcon({ size = 32, className, style }) {
  return (
    <img
      src={logoImg}
      alt="AR Advisor Logo"
      width={size}
      height={size}
      className={className}
      style={{
        display: 'inline-block',
        verticalAlign: 'middle',
        borderRadius: '24%', /* matches the modern rounded square style of the logo */
        objectFit: 'cover',
        ...style
      }}
    />
  );
}
