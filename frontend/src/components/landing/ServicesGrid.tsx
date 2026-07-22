import { Link } from "react-router-dom";
import GradientIcon from "../icons/GradientIcon";
import { ScissorsIcon, SparklesIcon, HandIcon, LotusIcon } from "../icons/ServiceIcons";

const services = [
  {
    title: "Hair Styling & Coloring",
    description: "From precision cuts to vibrant color transformations, our master stylists bring your vision to life.",
    icon: ScissorsIcon,
    link: "/services",
  },
  {
    title: "Facial & Skincare",
    description: "Rejuvenate your complexion with our organic facials, peels, and personalized skincare routines.",
    icon: SparklesIcon,
    link: "/services",
  },
  {
    title: "Nail Art & Manicure",
    description: "Express yourself with stunning nail art, classic manicures, and luxurious pedicure treatments.",
    icon: HandIcon,
    link: "/services",
  },
  {
    title: "Massage & Relaxation",
    description: "Melt away stress with our therapeutic massages, aromatherapy, and holistic wellness rituals.",
    icon: LotusIcon,
    link: "/services",
  },
];

export default function ServicesGrid() {
  return (
    <section className="py-20 bg-cream" aria-labelledby="services-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <span className="inline-flex items-center rounded-full border border-champagne/30 bg-champagne/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-champagne-dark">
            What We Offer
          </span>
          <h2
            id="services-heading"
            className="mt-4 font-display text-3xl font-bold text-charcoal sm:text-4xl"
          >
            Our Signature Services
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-charcoal-light">
            Discover our curated collection of premium beauty and wellness treatments,
            each designed to leave you feeling radiant and refreshed.
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {services.map((service) => (
            <Link
              key={service.title}
              to={service.link}
              className="group relative rounded-xl border border-champagne/20 bg-white p-8 shadow-sm transition-all hover:shadow-md hover:border-champagne/40 hover:scale-[1.02]"
            >
              <GradientIcon size="lg">
                <service.icon className="h-8 w-8" />
              </GradientIcon>
              <h3 className="mt-6 font-display text-lg font-semibold text-charcoal group-hover:text-champagne-dark transition-colors">
                {service.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-charcoal-light">
                {service.description}
              </p>
              <div className="mt-6 inline-flex items-center gap-1 text-sm font-semibold text-champagne-dark opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more
                <svg className="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
