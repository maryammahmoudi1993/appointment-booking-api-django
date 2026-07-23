import SectionHeading from "../ui/SectionHeading";
import featureSkilledTeam from "../../assets/landing/feature-skilled-team-clean.webp";
import featureHygiene from "../../assets/landing/feature-hygiene-clean.webp";
import featureProducts from "../../assets/landing/feature-products-clean.webp";
import featureRelax from "../../assets/landing/icon-spa-relax-clean.webp";
import botanicalBranch from "../../assets/landing/botanical-branch-clean.png";

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
    <section className="relative bg-main py-20 sm:py-24" aria-labelledby="why-choose-us-heading">
      <img src={botanicalBranch} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -left-20 bottom-0 hidden w-64 -rotate-12 opacity-75 lg:block" />
      <div className="mx-auto max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[.78fr_1.22fr] lg:items-center">
          <div className="relative z-10">
            <SectionHeading
              align="left"
              eyebrow="Why Choose Us"
              id="why-choose-us-heading"
              title="Beauty that feels personal."
              description="We blend expert care with premium products to bring out your natural glow — inside and out."
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {reasons.map((reason) => (
              <div
                key={reason.number}
                className="beauty-card flex min-h-[142px] gap-4 p-5 transition duration-300 hover:-translate-y-1 hover:shadow-raised"
              >
                <span className="flex h-[62px] w-[62px] shrink-0 items-center justify-center overflow-hidden rounded-[18px] border border-rose/15 bg-blush shadow-raised">
                  <img src={reason.icon} alt="" width={384} height={384} className="h-full w-full object-cover" loading="lazy" />
                </span>
                <div>
                  <span className="text-xs font-bold text-coral">{reason.number}</span>
                  <h3 className="font-display text-lg font-semibold text-heading">
                    {reason.title}
                  </h3>
                  <p className="mt-1 text-xs leading-5 text-secondary">
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
