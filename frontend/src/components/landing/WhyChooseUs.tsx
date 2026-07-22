import GradientIcon from "../icons/GradientIcon";
import SectionHeading from "../ui/SectionHeading";
import { UsersIcon, ShieldCheckIcon, SparklesIcon, LotusIcon } from "../icons/ServiceIcons";

const reasons = [
  {
    number: "01",
    title: "Highly Skilled Team",
    description: "Our stylists train continuously to bring out your best look.",
    icon: UsersIcon,
  },
  {
    number: "02",
    title: "Hygiene & Safety",
    description: "Strict sanitation protocols at every station, every visit.",
    icon: ShieldCheckIcon,
  },
  {
    number: "03",
    title: "Premium Products",
    description: "Only high-quality, skin- and hair-safe products, always.",
    icon: SparklesIcon,
  },
  {
    number: "04",
    title: "Relax & Enjoy",
    description: "A calm, comfortable ambience made for your relaxation.",
    icon: LotusIcon,
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
                <GradientIcon size="sm" className="shrink-0">
                  <reason.icon />
                </GradientIcon>
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
