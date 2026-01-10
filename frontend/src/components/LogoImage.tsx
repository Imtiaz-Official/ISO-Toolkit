/**
 * Logo Image Component
 * Displays Linux distribution logos with fallback to emoji
 */

import { useState, useEffect, useMemo } from 'react';
import { getDistroLogo, getDistroFallback } from '../assets/logos';

interface LogoImageProps {
  distroName: string;
  alt?: string;
  className?: string;
  size?: number;
}

export function LogoImage({ distroName, alt, className = '', size = 32 }: LogoImageProps) {
  const logoUrl = getDistroLogo(distroName);
  const fallbackEmoji = getDistroFallback(distroName);
  const [imageError, setImageError] = useState(false);

  // Reset error state when logo URL changes
  useEffect(() => {
    setImageError(false);
  }, [logoUrl]);

  // If no logo URL or image failed to load, show emoji
  if (!logoUrl || imageError) {
    return (
      <span
        className={className}
        style={{ fontSize: `${size}px`, lineHeight: 1 }}
        role="img"
        aria-label={alt || distroName}
      >
        {fallbackEmoji}
      </span>
    );
  }

  return (
    <img
      key={logoUrl}
      src={logoUrl}
      alt={alt || distroName}
      className={className}
      width={size}
      height={size}
      style={{ objectFit: 'contain' }}
      onError={() => setImageError(true)}
      loading="lazy"
    />
  );
}

interface DistroLogoProps {
  distroName: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizes = {
  sm: 20,
  md: 32,
  lg: 48,
};

export function DistroLogo({ distroName, size = 'md', className = '' }: DistroLogoProps) {
  const logoUrl = useMemo(() => getDistroLogo(distroName), [distroName]);
  const fallbackEmoji = getDistroFallback(distroName);
  const [imageError, setImageError] = useState(false);
  const actualSize = sizes[size];

  // Reset error state when logo URL changes
  useEffect(() => {
    setImageError(false);
  }, [logoUrl]);

  if (!logoUrl || imageError) {
    return (
      <span
        className={`inline-flex items-center justify-center ${className}`}
        style={{ fontSize: `${actualSize * 0.8}px`, width: actualSize, height: actualSize }}
        role="img"
        aria-label={distroName}
      >
        {fallbackEmoji}
      </span>
    );
  }

  return (
    <div
      className={`inline-flex items-center justify-center ${className}`}
      style={{ width: actualSize, height: actualSize }}
    >
      <img
        key={logoUrl}
        src={logoUrl}
        alt={distroName}
        width={actualSize}
        height={actualSize}
        style={{ objectFit: 'contain', maxWidth: '100%', maxHeight: '100%' }}
        onError={() => setImageError(true)}
        loading="lazy"
      />
    </div>
  );
}
