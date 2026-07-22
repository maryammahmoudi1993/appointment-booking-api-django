import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import BrandLogo from "../icons/BrandLogo";

export default function HeroSection() {
  const { user } = useAuth();

  return (
    <section className="relative overflow-hidden bg-blush-gradient" aria-label="Hero">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          {/* Text content */}
          <div className="text-center lg:text-left">
            <span className="inline-flex items-center gap-2 rounded-full border border-champagne/30 bg-champagne/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-champagne-dark">
              <BrandLogo size={16} />
              Premium Beauty &amp; Wellness
            </span>
            <h1 className="mt-6 font-display text-4xl font-bold leading-tight tracking-tight text-charcoal sm:text-5xl lg:text-6xl">
              Redefine Your{" "}
              <span className="gradient-text">Beauty &amp; Glow</span>
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-charcoal-light max-w-lg mx-auto lg:mx-0">
              Premium hair, skin, and spa treatments tailored just for you.
              Experience luxury care with our expert stylists and organic products.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center lg:justify-start">
              {user ? (
                <Link
                  to="/book"
                  className="inline-flex items-center gap-2 rounded-full bg-rosegold-gradient px-8 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
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
                    className="inline-flex items-center gap-2 rounded-full bg-rosegold-gradient px-8 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Book an Appointment
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </Link>
                  <Link
                    to="/services"
                    className="inline-flex items-center gap-2 rounded-full border border-charcoal/20 bg-white px-8 py-3.5 text-sm font-semibold text-charcoal transition-all hover:border-champagne hover:text-champagne-dark"
                  >
                    Explore Services
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Visual side */}
          <div className="relative flex items-center justify-center">
            <div className="relative h-80 w-80 sm:h-96 sm:w-96 lg:h-[480px] lg:w-[480px]">
              {/* Decorative circles */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-champagne/20 to-blush/40" />
              <div className="absolute inset-4 rounded-full bg-gradient-to-br from-champagne/10 to-blush/20" />

              {/* Center logo */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <BrandLogo size={160} className="opacity-90" />
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 rounded-full bg-white/80 px-4 py-1.5 shadow-sm backdrop-blur-sm">
                    <span className="text-xs font-semibold text-champagne-dark">Est. 2024</span>
                  </div>
                </div>
              </div>

              {/* Floating badges */}
              <div className="absolute top-8 right-0 rounded-xl bg-white/80 px-3 py-2 shadow-sm backdrop-blur-sm">
                <span className="text-xs font-semibold text-charcoal">5-Star Rated</span>
              </div>
              <div className="absolute bottom-16 left-0 rounded-xl bg-white/80 px-3 py-2 shadow-sm backdrop-blur-sm">
                <span className="text-xs font-semibold text-champagne-dark">Expert Stylists</span>
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
