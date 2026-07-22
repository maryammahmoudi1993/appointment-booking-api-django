interface BrandLogoProps {
  className?: string;
  size?: number;
}

const PETAL_ANGLES = [0, 72, 144, 216, 288];

export default function BrandLogo({ className = "", size = 40 }: BrandLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="BloomFlow AI logo"
    >
      <defs>
        <linearGradient id="brandPetalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F3D9B8" />
          <stop offset="55%" stopColor="#D4AF37" />
          <stop offset="100%" stopColor="#B8860B" />
        </linearGradient>
        <radialGradient id="brandCenterGradient" cx="35%" cy="35%" r="70%">
          <stop offset="0%" stopColor="#FFF6E5" />
          <stop offset="100%" stopColor="#D4AF37" />
        </radialGradient>
      </defs>

      <g>
        {PETAL_ANGLES.map((angle) => (
          <ellipse
            key={angle}
            cx="24"
            cy="13.5"
            rx="5.5"
            ry="9.5"
            fill="url(#brandPetalGradient)"
            transform={`rotate(${angle} 24 24)`}
          />
        ))}
      </g>

      <circle cx="24" cy="24" r="4.5" fill="url(#brandCenterGradient)" />
      <ellipse
        cx="21"
        cy="21"
        rx="2.4"
        ry="1.3"
        fill="white"
        opacity="0.55"
        transform="rotate(-30 21 21)"
      />
    </svg>
  );
}
