import { cloneElement, isValidElement, type ReactElement } from "react";

interface GradientIconProps {
  children: ReactElement<{ className?: string; stroke?: string }>;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "h-10 w-10",
  md: "h-14 w-14",
  lg: "h-18 w-18",
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
      className={`relative inline-flex items-center justify-center rounded-full bg-gradient-to-br from-[#E8C39E] via-[#D4AF37] to-[#B8860B] p-[2px] ${className}`}
    >
      <div
        className={`flex items-center justify-center rounded-full bg-cream/80 backdrop-blur-sm ${sizeClasses[size]}`}
      >
        {icon}
      </div>
    </div>
  );
}
