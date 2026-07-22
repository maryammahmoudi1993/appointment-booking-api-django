import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { reviewsApi } from "../../api/client";
import BrandLogo from "../icons/BrandLogo";

function StarRow({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5" aria-hidden="true">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          className={`h-4 w-4 ${i < Math.round(rating) ? "text-coral" : "text-coral/25"}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

export default function HeroSection() {
  const { user } = useAuth();
  const [ratingSummary, setRatingSummary] = useState<{
    average: number;
    count: number;
    initials: string[];
  } | null>(null);

  useEffect(() => {
    reviewsApi
      .list()
      .then((res) => {
        const { count, results } = res.data;
        if (count === 0 || results.length === 0) return;
        const average = results.reduce((sum, r) => sum + r.rating, 0) / results.length;
        const initials = results
          .slice(0, 4)
          .map((r) => (r.customer_name || "?").charAt(0).toUpperCase());
        setRatingSummary({ average, count, initials });
      })
      .catch(() => setRatingSummary(null));
  }, []);

  return (
    <section className="relative overflow-hidden bg-blush-gradient" aria-label="Hero">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          {/* Text content */}
          <div className="text-center lg:text-left">
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-coral-dark">
              Beauty, Care, Confidence.
            </span>
            <h1 className="mt-4 font-display text-4xl font-bold leading-tight tracking-tight text-charcoal sm:text-5xl lg:text-6xl">
              Your Beauty,
              <br />
              Our Passion.
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-charcoal-light max-w-lg mx-auto lg:mx-0">
              Premium hair, skin, and spa treatments tailored just for you.
              Experience luxury care with our expert stylists and organic products.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center lg:justify-start">
              {user ? (
                <Link
                  to="/book"
                  className="inline-flex items-center gap-2 rounded-full bg-coral px-8 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:bg-coral-dark hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] motion-reduce:hover:scale-100"
                >
                  Book an Appointment
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="inline-flex items-center gap-2 rounded-full bg-coral px-8 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:bg-coral-dark hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] motion-reduce:hover:scale-100"
                  >
                    Book an Appointment
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </Link>
                  <Link
                    to="/services"
                    className="inline-flex items-center gap-2 rounded-full border border-charcoal/15 bg-blush-light px-8 py-3.5 text-sm font-semibold text-charcoal transition-all hover:border-coral hover:text-coral-dark"
                  >
                    Explore Services
                  </Link>
                </>
              )}
            </div>

            {ratingSummary && (
              <div className="mt-8 flex items-center justify-center gap-3 lg:justify-start">
                <div className="flex -space-x-2" aria-hidden="true">
                  {ratingSummary.initials.map((initial, i) => (
                    <span
                      key={i}
                      className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-cream bg-coral/20 text-xs font-semibold text-coral-dark"
                    >
                      {initial}
                    </span>
                  ))}
                </div>
                <div>
                  <StarRow rating={ratingSummary.average} />
                  <span className="text-sm font-medium text-charcoal-light">
                    {ratingSummary.average.toFixed(1)}/5 from {ratingSummary.count} review
                    {ratingSummary.count === 1 ? "" : "s"}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Visual side */}
          <div className="relative flex items-center justify-center">
            <div className="relative h-80 w-80 sm:h-96 sm:w-96 lg:h-[480px] lg:w-[480px]">
              {/* Decorative circles */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-coral/15 to-blush/50" />
              <div className="absolute inset-4 rounded-full bg-gradient-to-br from-coral/10 to-blush/30" />

              {/* Botanical accent */}
              <svg
                className="absolute -right-4 top-4 h-20 w-20 text-coral/30"
                viewBox="0 0 64 64"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                aria-hidden="true"
              >
                <path d="M32 6C20 14 16 28 24 42c4-10 14-16 20-14-2 12-12 20-24 20" />
                <path d="M32 6v50" />
              </svg>

              {/* Center logo */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <BrandLogo size={160} className="opacity-90" />
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 rounded-full bg-white/80 px-4 py-1.5 shadow-sm backdrop-blur-sm">
                    <span className="text-xs font-semibold text-coral-dark">Est. 2024</span>
                  </div>
                </div>
              </div>

              {/* Floating badges */}
              <div className="absolute top-8 right-0 rounded-xl bg-white/80 px-3 py-2 shadow-sm backdrop-blur-sm">
                <span className="text-xs font-semibold text-charcoal">5-Star Rated</span>
              </div>
              <div className="absolute bottom-16 left-0 rounded-xl bg-white/80 px-3 py-2 shadow-sm backdrop-blur-sm">
                <span className="text-xs font-semibold text-coral-dark">Expert Stylists</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
          <path d="M0 60L48 55C96 50 192 40 288 35C384 30 480 30 576 33.3C672 36.7 768 43.3 864 45C960 46.7 1056 43.3 1152 40C1248 36.7 1344 33.3 1392 31.7L1440 30V60H1392C1344 60 1248 60 1152 60C1056 60 960 60 864 60C768 60 672 60 576 60C480 60 384 60 288 60C192 60 96 60 48 60H0Z" fill="#FAF9F6" />
        </svg>
      </div>
    </section>
  );
}
