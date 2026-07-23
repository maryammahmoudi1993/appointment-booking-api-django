import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import BrandLogo from "../icons/BrandLogo";

const links = [
  { href: "#home", label: "Home" },
  { href: "#services", label: "Services" },
  { href: "#about", label: "About" },
  { href: "#services", label: "Prices" },
  { href: "#reviews", label: "Reviews" },
];

export default function LandingHeader() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const bookingTarget = user?.role === "customer" ? "/book" : "/register";

  useEffect(() => {
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);

  return (
    <header className="absolute inset-x-0 top-0 z-40">
      <nav className="mx-auto flex max-w-[1240px] items-center justify-between px-4 py-4 sm:px-6 lg:px-8" aria-label="Landing navigation">
        <a href="#home" className="flex items-center gap-2.5 text-heading" aria-label="Beauty Studio home">
          <BrandLogo size={32} />
          <span className="font-display text-lg font-semibold">Beauty Studio</span>
        </a>
        <div className="hidden items-center gap-8 text-[13px] font-medium text-secondary md:flex">
          {links.map((item) => (
            <a key={item.label} href={item.href} className="transition-colors hover:text-coral focus-visible:text-coral">
              {item.label}
            </a>
          ))}
        </div>
        <Link to={bookingTarget} className="beauty-button hidden px-6 md:inline-flex">Book now</Link>
        <button
          type="button"
          className="flex h-11 w-11 items-center justify-center rounded-full border border-rose/20 bg-surface/85 text-heading md:hidden"
          aria-label="Toggle navigation menu"
          aria-expanded={open}
          aria-controls="landing-mobile-menu"
          onClick={() => setOpen((current) => !current)}
        >
          <span className="space-y-1.5" aria-hidden="true">
            <span className="block h-0.5 w-5 bg-current" />
            <span className="block h-0.5 w-5 bg-current" />
            <span className="block h-0.5 w-5 bg-current" />
          </span>
        </button>
      </nav>
      {open && (
        <div id="landing-mobile-menu" className="mx-4 rounded-[24px] border border-rose/15 bg-surface/95 p-4 shadow-raised backdrop-blur md:hidden">
          <div className="flex flex-col">
            {links.map((item) => (
              <a key={item.label} href={item.href} onClick={() => setOpen(false)} className="flex min-h-11 items-center rounded-xl px-3 text-sm font-semibold text-secondary hover:bg-soft">
                {item.label}
              </a>
            ))}
            <Link to={bookingTarget} onClick={() => setOpen(false)} className="beauty-button mt-3">Book now</Link>
          </div>
        </div>
      )}
    </header>
  );
}
