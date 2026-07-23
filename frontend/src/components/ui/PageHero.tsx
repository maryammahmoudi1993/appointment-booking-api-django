import type { ReactNode } from "react";
import botanicalBranch from "../../assets/landing/botanical-branch.webp";

interface PageHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}

export default function PageHero({ eyebrow, title, description, actions }: PageHeroProps) {
  return (
    <section className="relative overflow-hidden border-b border-rose/10 bg-[radial-gradient(circle_at_82%_12%,rgba(239,179,164,.34),transparent_28%),linear-gradient(135deg,#fff8f4,#feefe8)]">
      <img
        src={botanicalBranch}
        alt=""
        width="600"
        height="327"
        className="pointer-events-none absolute -right-20 -top-16 w-72 opacity-35 sm:w-96"
      />
      <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
        <p className="beauty-eyebrow">{eyebrow}</p>
        <h1 className="mt-3 max-w-3xl text-4xl font-medium leading-tight text-heading sm:text-5xl lg:text-6xl">
          {title}
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-secondary sm:text-lg">{description}</p>
        {actions && <div className="mt-8 flex flex-wrap gap-3">{actions}</div>}
      </div>
    </section>
  );
}
