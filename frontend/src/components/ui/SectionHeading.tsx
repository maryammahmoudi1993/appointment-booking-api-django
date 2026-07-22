interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "center" | "left";
  id?: string;
  className?: string;
}

export default function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
  id,
  className = "",
}: SectionHeadingProps) {
  const alignment = align === "center" ? "text-center mx-auto" : "text-left";

  return (
    <div className={`${alignment} ${className}`}>
      {eyebrow && (
        <span className="inline-flex items-center rounded-full border border-champagne/30 bg-champagne/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-champagne-dark">
          {eyebrow}
        </span>
      )}
      <h2
        id={id}
        className="mt-4 font-display text-3xl font-bold text-charcoal sm:text-4xl"
      >
        {title}
      </h2>
      {description && (
        <p
          className={`mt-4 text-charcoal-light ${align === "center" ? "mx-auto max-w-2xl" : "max-w-2xl"}`}
        >
          {description}
        </p>
      )}
    </div>
  );
}
