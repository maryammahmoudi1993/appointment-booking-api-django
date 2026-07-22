import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { promotionsApi, type PromoCode } from "../../api/client";
import { GiftIcon } from "../icons/ServiceIcons";
import GradientIcon from "../icons/GradientIcon";

function formatDiscount(promo: PromoCode): string {
  return promo.discount_type === "percent"
    ? `${promo.discount_value}%`
    : `$${promo.discount_value}`;
}

export default function PromoBanner() {
  const [promo, setPromo] = useState<PromoCode | null>(null);

  useEffect(() => {
    promotionsApi
      .list()
      .then((res) => {
        const active = res.data.results.find((p) => p.is_active);
        setPromo(active ?? null);
      })
      .catch(() => setPromo(null));
  }, []);

  return (
    <section className="py-10" aria-label="Promotion">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-6 rounded-3xl border border-champagne/25 bg-gradient-to-br from-blush-light via-blush to-coral/10 p-8 shadow-sm sm:flex-row sm:justify-between">
          <div className="flex items-center gap-5">
            <GradientIcon size="lg">
              <GiftIcon />
            </GradientIcon>
            <div>
              <span className="text-xs font-semibold uppercase tracking-widest text-coral-dark">
                Special Offer
              </span>
              {promo ? (
                <>
                  <h3 className="mt-1 font-display text-xl font-bold text-charcoal sm:text-2xl">
                    {formatDiscount(promo)} off with code {promo.code}
                  </h3>
                  <p className="mt-1 text-sm text-charcoal-light">
                    {promo.description || "Limited-time offer — book before it ends."}
                  </p>
                </>
              ) : (
                <>
                  <h3 className="mt-1 font-display text-xl font-bold text-charcoal sm:text-2xl">
                    New here? We&apos;d love to welcome you.
                  </h3>
                  <p className="mt-1 text-sm text-charcoal-light">
                    Book your first appointment and experience the BloomFlow difference.
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-5">
            {promo && (
              <div
                className="flex h-20 w-20 shrink-0 rotate-6 items-center justify-center rounded-full bg-coral text-center shadow-md"
                aria-hidden="true"
              >
                <span className="-rotate-6 text-sm font-bold leading-tight text-white">
                  {formatDiscount(promo)}
                  <br />
                  OFF
                </span>
              </div>
            )}
            <Link
              to="/book"
              className="inline-flex items-center justify-center rounded-full bg-coral px-8 py-3 text-sm font-semibold text-white shadow-md transition-all hover:bg-coral-dark hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] motion-reduce:hover:scale-100"
            >
              {promo ? "Book Your First Visit" : "Book an Appointment"}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
