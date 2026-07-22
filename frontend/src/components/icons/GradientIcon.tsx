import { type ReactNode } from "react";

interface GradientIconProps {
  children: ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "h-10 w-10",
  md: "h-14 w-14",
  lg: "h-18 w-18",
} as const;

const iconSizes = {
  sm: 20,
  md: 28,
  lg: 36,
} as const;

export default function GradientIcon({
  children,
  className = "",
  size = "md",
}: GradientIconProps) {
  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-xl bg-gradient-to-br from-[#E8C39E] via-[#D4AF37] to-[#B8860B] p-[1px] ${className}`}
    >
      <div className="flex items-center justify-center rounded-[11px] bg-cream/80 backdrop-blur-sm">
        <div className={sizeClasses[size]}>
          <svg
            width={iconSizes[size]}
            height={iconSizes[size]}
            viewBox="0 0 24 24"
            fill="none"
            stroke="url(#iconGradient)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto my-auto"
          >
            <defs>
              <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#E8C39E" />
                <stop offset="50%" stopColor="#D4AF37" />
                <stop offset="100%" stopColor="#B8860B" />
              </linearGradient>
            </defs>
            {children}
          </svg>
        </div>
      </div>
    </div>
  );
}
