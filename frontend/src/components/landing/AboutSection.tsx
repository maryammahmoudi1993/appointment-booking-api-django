import { useEffect, useState } from "react";
import promoProducts from "../../assets/landing/promo-products.webp";
import decorativeFlower from "../../assets/landing/decorative-flower-clean.png";
import botanicalBranch from "../../assets/landing/botanical-branch-clean.png";
import makeupIcon from "../../assets/landing/icon-makeup-clean.webp";
import skinIcon from "../../assets/landing/icon-skin-care-clean.webp";
import { reviewsApi, servicesApi, staffApi } from "../../api/client";

interface Stat {
  value: string;
  label: string;
}

export default function AboutSection() {
  // These stats used to be hardcoded ("500+ clients", "4.9 rating", etc.)
  // and shown as if they were real business metrics. They're now computed
  // from the same public endpoints already used elsewhere on the landing
  // page, so the numbers shown are always genuine, live counts.
  const [stats, setStats] = useState<Stat[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([staffApi.list(), servicesApi.list(), reviewsApi.list()])
      .then(([staffRes, servicesRes, reviewsRes]) => {
        if (cancelled) return;
        const reviews = reviewsRes.data.results;
        const averageRating = reviews.length
          ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
          : null;
        setStats([
          { value: `${reviewsRes.data.count}+`, label: "Client reviews" },
          { value: `${staffRes.data.count}+`, label: "Expert stylists" },
          { value: `${servicesRes.data.count}+`, label: "Treatments" },
          {
            value: averageRating ? averageRating.toFixed(1) : "New",
            label: "Average rating",
          },
        ]);
      })
      .catch(() => {
        if (!cancelled) setStats([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section id="about" className="scroll-mt-8 bg-main py-20 sm:py-24" aria-labelledby="about-heading">
      <div className="mx-auto grid max-w-[1240px] gap-10 px-4 sm:px-6 lg:grid-cols-[1.02fr_.98fr] lg:items-center lg:px-8">
        <div className="relative mx-auto min-h-[430px] w-full max-w-[570px] overflow-hidden rounded-[34px] border border-rose/15 bg-gradient-to-br from-[#f8ddd5] to-[#f2c8bd] shadow-soft">
          <img src={promoProducts} alt="Premium salon products and a gift box" width="600" height="502" loading="lazy" className="absolute inset-x-0 bottom-0 h-[78%] w-full object-cover object-center mix-blend-multiply" />
          <img src={decorativeFlower} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -right-20 -top-8 w-64 rotate-12" />
          <img src={botanicalBranch} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -bottom-12 -left-24 w-72 -rotate-12" />
          <img src={makeupIcon} alt="" width="384" height="384" loading="lazy" className="absolute left-7 top-7 h-20 w-20 rounded-[22px] object-cover shadow-raised" />
          <img src={skinIcon} alt="" width="384" height="384" loading="lazy" className="absolute right-10 top-24 h-16 w-16 rounded-[18px] object-cover shadow-raised" />
        </div>

        <div>
          <p className="beauty-eyebrow">About Beauty Studio</p>
          <h2 id="about-heading" className="mt-3 text-[clamp(2.4rem,4vw,3.7rem)] font-medium leading-[1.05] text-heading">Care that looks beautiful—and feels even better.</h2>
          <p className="mt-6 text-base leading-7 text-secondary">Our artists combine thoughtful consultation, refined technique, and premium products to shape a treatment around you.</p>
          <p className="mt-4 text-base leading-7 text-secondary">From your first hello to the final mirror moment, every detail is calm, personal, and intentionally polished.</p>
          <dl className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {(stats ?? Array.from({ length: 4 })).map((stat, i) => (
              <div key={stat ? (stat as Stat).label : i} className="rounded-[20px] border border-rose/15 bg-surface p-4 text-center shadow-raised">
                {stat ? (
                  <>
                    <dt className="text-[10px] font-bold uppercase tracking-[.12em] text-muted">{(stat as Stat).label}</dt>
                    <dd className="mt-2 font-display text-2xl font-semibold text-coral">{(stat as Stat).value}</dd>
                  </>
                ) : (
                  <div className="h-10 animate-pulse rounded-lg bg-rose/10" aria-hidden="true" />
                )}
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
