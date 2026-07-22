import SectionHeading from "../ui/SectionHeading";
import featureSkilledTeam from "../../assets/landing/feature-skilled-team.webp";
import featureHygiene from "../../assets/landing/feature-hygiene.webp";
import featureProducts from "../../assets/landing/feature-products.webp";
import featureRelax from "../../assets/landing/icon-spa-relax.webp";

const reasons = [
  {
    number: "01",
    title: "Highly Skilled Team",
    description: "Our stylists train continuously to bring out your best look.",
    icon: featureSkilledTeam,
  },
  {
    number: "02",
    title: "Hygiene & Safety",
    description: "Strict sanitation protocols at every station, every visit.",
    icon: featureHygiene,
  },
  {
    number: "03",
    title: "Premium Products",
    description: "Only high-quality, skin- and hair-safe products, always.",
    icon: featureProducts,
  },
  {
    number: "04",
    title: "Relax & Enjoy",
    description: "A calm, comfortable ambience made for your relaxation.",
    icon: featureRelax,
  },
];

export default function WhyChooseUs() {
  return (
    <section className="py-20 bg-cream" aria-labelledby="why-choose-us-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <SectionHeading
            align="left"
            eyebrow="Why Choose Us"
            id="why-choose-us-heading"
            title="Beauty that feels personal."
            description="We blend expert care with premium products to bring out your natural glow — inside and out."
          />

          <div className="grid gap-4 sm:grid-cols-2">
            {reasons.map((reason) => (
              <div
                key={reason.number}
                className="flex gap-4 rounded-2xl border border-champagne/20 bg-white p-5 shadow-sm transition-all hover:shadow-md"
              >
                <span className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-2xl shadow-[0_8px_18px_-6px_rgba(168,87,75,0.3)]">
                  <img src={reason.icon} alt="" width={56} height={56} className="h-full w-full object-cover" loading="lazy" />
                </span>
                <div>
                  <span className="text-xs font-bold text-coral-dark">{reason.number}</span>
                  <h3 className="font-display text-base font-semibold text-charcoal">
                    {reason.title}
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-charcoal-light">
                    {reason.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
