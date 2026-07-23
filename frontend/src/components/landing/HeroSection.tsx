import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { reviewsApi } from "../../api/client";
import heroCharacter from "../../assets/landing/hero-character.webp";
import botanicalBranch from "../../assets/landing/botanical-branch-clean.png";
import avatar1 from "../../assets/landing/avatar-1.webp";
import avatar2 from "../../assets/landing/avatar-2.webp";
import avatar3 from "../../assets/landing/avatar-3.webp";
import avatar4 from "../../assets/landing/avatar-4.webp";

const avatars = [avatar1, avatar2, avatar3, avatar4];

export default function HeroSection() {
  const { user } = useAuth();
  const [rating, setRating] = useState({ average: 4.9, count: 1000 });
  const bookingTarget = user?.role === "customer" ? "/book" : "/register";

  useEffect(() => {
    reviewsApi.list().then((res) => {
      if (!res.data.results.length) return;
      const average = res.data.results.reduce((sum, review) => sum + review.rating, 0) / res.data.results.length;
      setRating({ average, count: res.data.count });
    }).catch(() => {});
  }, []);

  return (
    <section id="home" className="relative overflow-hidden bg-[radial-gradient(circle_at_76%_35%,rgba(239,179,164,.34),transparent_31%),linear-gradient(135deg,#fff8f4_0%,#feeee7_100%)] pt-24" aria-labelledby="hero-title">
      <div className="mx-auto grid max-w-[1240px] items-center gap-8 px-4 pb-24 pt-8 sm:px-6 sm:pt-12 lg:grid-cols-[.9fr_1.1fr] lg:px-8 lg:pb-28 lg:pt-8">
        <div className="relative z-10 text-center lg:text-left">
          <p className="beauty-eyebrow">Beauty, care, confidence.</p>
          <h1 id="hero-title" className="mt-4 text-[clamp(3.25rem,6.3vw,5.75rem)] font-medium leading-[.98] tracking-[-.045em] text-heading">
            Your Beauty,<br />Our Passion.
          </h1>
          <p className="mx-auto mt-5 max-w-md text-base leading-7 text-secondary lg:mx-0 lg:text-lg">
            Beauty is not just how you look—it’s how you feel every day.
          </p>
          <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start">
            <Link to={bookingTarget} className="beauty-button px-7">Book an Appointment <span className="ml-2" aria-hidden="true">→</span></Link>
            <a href="#services" className="beauty-button-secondary px-7">Explore Services</a>
          </div>
          <div className="mt-7 flex items-center justify-center gap-4 lg:justify-start">
            <div className="flex -space-x-2" aria-hidden="true">
              {avatars.map((src) => <img key={src} src={src} alt="" width="200" height="200" className="h-9 w-9 rounded-full border-2 border-main object-cover" />)}
            </div>
            <div className="text-left">
              <div className="text-base tracking-[.16em] text-[#e6a54a]" aria-label={`${rating.average.toFixed(1)} out of 5 stars`}>★★★★★</div>
              <p className="text-xs font-medium text-secondary">{rating.average.toFixed(1)}/5 from {rating.count.toLocaleString()}+ happy clients</p>
            </div>
          </div>
        </div>

        <div className="relative mx-auto h-[410px] w-full max-w-[610px] sm:h-[520px] lg:h-[610px]">
          <div className="absolute bottom-0 left-1/2 h-[94%] w-[84%] -translate-x-1/2 rounded-t-[48%] bg-gradient-to-br from-[#f8d8d0] to-[#eebcb2] shadow-[inset_0_2px_0_rgba(255,255,255,.75)]" />
          <div className="absolute bottom-[3%] left-[8%] h-[60%] w-[35%] rounded-full bg-[#f8cdc3]/70" />
          <img
            src={heroCharacter}
            alt="Woman enjoying a calm premium beauty treatment"
            width="760"
            height="943"
            fetchPriority="high"
            className="absolute inset-0 h-full w-full object-contain object-bottom [filter:drop-shadow(0_20px_24px_rgba(113,64,54,.12))]"
          />
          <img src={botanicalBranch} alt="" width="600" height="327" className="pointer-events-none absolute -right-12 top-[20%] w-56 rotate-[76deg] opacity-90 sm:w-64" />
          <div className="absolute right-[1%] top-[14%] hidden rounded-2xl border border-white/70 bg-surface/90 px-4 py-3 text-xs font-bold text-heading shadow-raised sm:block">★ 5-Star Rated</div>
          <div className="absolute bottom-[16%] left-[2%] hidden rounded-2xl border border-white/70 bg-surface/90 px-4 py-3 text-xs font-bold text-coral shadow-raised sm:block">✦ Expert Stylists</div>
        </div>
      </div>
    </section>
  );
}
