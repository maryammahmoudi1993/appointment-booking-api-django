import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import BrandLogo from "../icons/BrandLogo";

export default function FinalCta() {
  const { user } = useAuth();

  return (
    <section className="relative overflow-hidden bg-charcoal py-20" aria-labelledby="final-cta-heading">
      <div className="pointer-events-none absolute inset-0 opacity-20">
        <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-champagne blur-3xl" />
        <div className="absolute -bottom-16 -right-16 h-64 w-64 rounded-full bg-blush blur-3xl" />
      </div>
      <div className="relative mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <BrandLogo size={56} className="mx-auto opacity-90" />
        <h2 id="final-cta-heading" className="mt-6 font-display text-3xl font-bold text-white sm:text-4xl">
          Ready to feel your best?
        </h2>
        <p className="mt-4 text-champagne-light">
          Reserve your spot with one of our specialists — it only takes a minute.
        </p>
        <Link
          to={user ? "/book" : "/register"}
          className="mt-8 inline-flex items-center gap-2 rounded-full bg-rosegold-gradient px-8 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
        >
          {user ? "Book an Appointment" : "Create Your Account"}
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
      </div>
    </section>
  );
}
