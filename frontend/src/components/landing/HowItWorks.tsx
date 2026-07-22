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
    <section className="py-20 bg-cream" aria-labelledby="how-it-works-heading">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 rounded-3xl bg-blush p-8 sm:p-12 lg:grid-cols-2 lg:items-center">
          {/* Steps */}
          <div>
            <SectionHeading
              align="left"
              eyebrow="How It Works"
              id="how-it-works-heading"
              title="Book in 3 Simple Steps"
            />

            <div className="relative mt-10 space-y-8">
              <div
                className="absolute left-6 top-2 bottom-2 hidden w-px bg-gradient-to-b from-coral/40 via-coral/20 to-transparent sm:block"
                aria-hidden="true"
              />
              {steps.map((step, i) => (
                <div key={step.title} className="relative flex items-start gap-4">
                  <div className="relative shrink-0">
                    <GradientIcon size="md">
                      <step.icon />
                    </GradientIcon>
                    <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-charcoal text-[10px] font-bold text-white">
                      {i + 1}
                    </span>
                  </div>
                  <div className="pt-1">
                    <h3 className="font-display text-base font-semibold text-charcoal">
                      {step.title}
                    </h3>
                    <p className="mt-1 text-sm leading-relaxed text-charcoal-light">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Phone mockup */}
          <div className="flex justify-center" aria-hidden="true">
            <div className="w-56 rounded-[2rem] border-[6px] border-charcoal bg-charcoal p-1.5 shadow-xl">
              <div className="rounded-[1.5rem] bg-cream px-4 py-5">
                <div className="flex items-center justify-between text-[10px] font-semibold text-charcoal-light">
                  <span>9:41</span>
                  <span>Book Appointment</span>
                </div>
                <div className="mt-4 rounded-xl bg-white p-3 shadow-sm">
                  <p className="text-xs font-semibold text-charcoal">Hair Styling &amp; Coloring</p>
                  <p className="mt-1 text-[11px] text-charcoal-light">Today &middot; 2:00 PM</p>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[11px] text-charcoal-light">Total</span>
                    <span className="text-sm font-bold text-coral-dark">$79.00</span>
                  </div>
                </div>
                <div className="mt-4 rounded-full bg-coral py-2 text-center text-xs font-semibold text-white">
                  Confirm Booking
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
