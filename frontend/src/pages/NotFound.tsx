import { Link } from "react-router-dom";
import BrandLogo from "../components/icons/BrandLogo";

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col items-center justify-center bg-blush-gradient px-4 py-24 text-center">
      <BrandLogo size={48} className="opacity-70" />
      <h1 className="mt-6 font-display text-6xl font-bold text-champagne/50">404</h1>
      <p className="mt-4 text-lg text-charcoal-light">
        We couldn&apos;t find that page.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex items-center justify-center rounded-full bg-rosegold-gradient px-6 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
      >
        Go Home
      </Link>
    </div>
  );
}
