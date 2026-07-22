interface BrandLogoProps {
  className?: string;
  size?: number;
}

export default function BrandLogo({ className = "", size = 40 }: BrandLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="BloomFlow AI logo"
    >
      <defs>
        <linearGradient id="roseGoldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#E8C39E" />
          <stop offset="50%" stopColor="#D4AF37" />
          <stop offset="100%" stopColor="#B8860B" />
        </linearGradient>
      </defs>
      {/* Graceful face profile */}
      <path
        d="M24 6C18 6 14 10 14 16C14 20 16 24 18 26C19 27 19 28 19 30V34"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      {/* Lotus petals */}
      <path
        d="M24 34C24 34 20 30 20 26C20 24 22 22 24 22C26 22 28 24 28 26C28 30 24 34 24 34Z"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M18 28C16 26 16 22 18 20"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M30 28C32 26 32 22 30 20"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      {/* Hair wave */}
      <path
        d="M14 14C12 12 12 8 14 6C16 4 20 4 24 4C28 4 32 4 34 6C36 8 36 12 34 14"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      {/* Leaf accent */}
      <path
        d="M24 38C24 38 22 42 24 44C26 42 24 38 24 38Z"
        stroke="url(#roseGoldGradient)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}
