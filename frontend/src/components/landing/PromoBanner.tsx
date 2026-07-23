import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { promotionsApi, type PromoCode } from "../../api/client";
import promoProducts from "../../assets/landing/promo-products.webp";
import makeupIcon from "../../assets/landing/icon-makeup-clean.webp";

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
    <section className="bg-main py-8" aria-label="Promotion">
      <div className="mx-auto max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <div className="relative flex flex-col items-center gap-4 overflow-hidden rounded-[30px] border border-rose/20 bg-gradient-to-r from-surface to-[#f8ddd5] shadow-soft sm:flex-row sm:justify-between">
          <div className="flex items-center gap-5">
            <img
              src={promoProducts}
              alt=""
              width={160}
              height={160}
              loading="lazy"
              className="h-36 w-40 shrink-0 object-cover object-right mix-blend-multiply sm:h-40 sm:w-56"
            />
            <div className="py-6 pr-4 sm:py-8">
              <span className="text-xs font-semibold uppercase tracking-widest text-coral-dark">
                Special Offer
              </span>
              {promo ? (
                <>
                  <h3 className="mt-1 font-display text-2xl font-medium text-heading sm:text-3xl">
                    {formatDiscount(promo)} off with code {promo.code}
                  </h3>
                  <p className="mt-1 text-sm text-charcoal-light">
                    {promo.description || "Limited-time offer — book before it ends."}
                  </p>
                </>
              ) : (
                <>
                  <h3 className="mt-1 font-display text-2xl font-medium text-heading sm:text-3xl">
                    New here? Enjoy 15% OFF
                  </h3>
                  <p className="mt-1 text-sm text-charcoal-light">
                    On your first booking with us.
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-5 px-5 pb-7 sm:px-0 sm:py-8 sm:pr-8">
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
            {!promo && <img src={makeupIcon} alt="" width="384" height="384" loading="lazy" className="hidden h-20 w-20 rounded-[22px] object-cover shadow-raised lg:block" />}
            <Link
              to="/book"
              className="beauty-button px-7"
            >
              {promo ? "Book Your First Visit" : "Book an Appointment"}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
