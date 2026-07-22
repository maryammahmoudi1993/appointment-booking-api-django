import GradientIcon from "../icons/GradientIcon";
import SectionHeading from "../ui/SectionHeading";
import { ScissorsIcon, CalendarIcon, ShieldCheckIcon } from "../icons/ServiceIcons";

const steps = [
  {
    icon: ScissorsIcon,
    title: "Choose a Service",
    description: "Browse our signature treatments and pick what suits you.",
  },
  {
    icon: CalendarIcon,
    title: "Pick Date & Time",
    description: "Select your preferred specialist and an open slot.",
  },
  {
    icon: ShieldCheckIcon,
    title: "Confirm & Relax",
    description: "Get instant confirmation — we'll take care of the rest.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 bg-blush" aria-labelledby="how-it-works-heading">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="How It Works"
          id="how-it-works-heading"
          title="Book in 3 Simple Steps"
        />

        <div className="relative mt-16 grid gap-10 sm:grid-cols-3">
          <div
            className="absolute left-0 right-0 top-10 hidden h-px bg-gradient-to-r from-transparent via-champagne/50 to-transparent sm:block"
            aria-hidden="true"
          />
          {steps.map((step, i) => (
            <div key={step.title} className="relative flex flex-col items-center text-center">
              <div className="relative">
                <GradientIcon size="lg">
                  <step.icon />
                </GradientIcon>
                <span className="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-charcoal text-xs font-bold text-white">
                  {i + 1}
                </span>
              </div>
              <h3 className="mt-6 font-display text-lg font-semibold text-charcoal">
                {step.title}
              </h3>
              <p className="mt-2 max-w-[220px] text-sm leading-relaxed text-charcoal-light">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
