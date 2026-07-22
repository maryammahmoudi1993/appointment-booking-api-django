import { cloneElement, isValidElement, type ReactElement } from "react";

interface GradientIconProps {
  children: ReactElement<{ className?: string; stroke?: string }>;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const tileSizeClasses = {
  sm: "h-12 w-12 rounded-xl",
  md: "h-16 w-16 rounded-2xl",
  lg: "h-20 w-20 rounded-2xl",
} as const;

const iconSizeClasses = {
  sm: "h-5 w-5",
  md: "h-7 w-7",
  lg: "h-9 w-9",
} as const;

export default function GradientIcon({
  children,
  className = "",
  size = "md",
}: GradientIconProps) {
  const icon = isValidElement(children)
    ? cloneElement(children, {
        stroke: "url(#icon-gradient)",
        className: `${iconSizeClasses[size]} ${children.props.className ?? ""}`.trim(),
      })
    : children;

  return (
    <div
      className={`relative inline-flex shrink-0 items-center justify-center overflow-hidden bg-gradient-to-br from-blush-light via-blush to-coral/15 shadow-[0_10px_24px_-8px_rgba(168,87,75,0.4)] ${tileSizeClasses[size]} ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/70 via-white/10 to-transparent" />
      <div className="pointer-events-none absolute -left-2 -top-2 h-8 w-8 rounded-full bg-white/50 blur-md" />
      <div className="relative">{icon}</div>
    </div>
  );
}
