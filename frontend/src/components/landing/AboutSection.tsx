import BrandLogo from "../icons/BrandLogo";
import GradientIcon from "../icons/GradientIcon";
import { UsersIcon, FaceIcon, FlameIcon, StarIcon } from "../icons/ServiceIcons";

const stats = [
  { value: "500+", label: "Happy Clients", icon: UsersIcon },
  { value: "15+", label: "Expert Stylists", icon: FaceIcon },
  { value: "50+", label: "Signature Treatments", icon: FlameIcon },
  { value: "4.9", label: "Average Rating", icon: StarIcon },
];

export default function AboutSection() {
  return (
    <section className="relative py-20 bg-blush" aria-labelledby="about-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          {/* Image side */}
          <div className="relative">
            <div className="relative rounded-2xl bg-white p-2 shadow-lg">
              <div className="rounded-xl bg-gradient-to-br from-champagne/10 to-blush/30 p-12">
                <BrandLogo size={120} className="mx-auto opacity-80" />
              </div>
            </div>
            {/* Decorative element */}
            <div className="absolute -bottom-4 -right-4 h-24 w-24 rounded-2xl bg-rosegold-gradient opacity-20" />
            <div className="absolute -top-4 -left-4 h-16 w-16 rounded-full bg-champagne/20" />
          </div>

          {/* Content */}
          <div>
            <span className="inline-flex items-center rounded-full border border-champagne/30 bg-white/60 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-coral-dark">
              About BloomFlow
            </span>
            <h2
              id="about-heading"
              className="mt-4 font-display text-3xl font-bold text-charcoal sm:text-4xl"
            >
              Experience Luxury Care
            </h2>
            <p className="mt-6 text-lg leading-relaxed text-charcoal-light">
              At BloomFlow, we believe beauty is an art form. Our master stylists combine
              years of expertise with the finest organic products to create personalized
              experiences that transcend ordinary salon visits.
            </p>
            <p className="mt-4 text-charcoal-light">
              From the moment you step through our doors, you&apos;re enveloped in an
              atmosphere of calm sophistication — where every detail is curated for
              your comfort and every treatment is crafted for excellence.
            </p>

            {/* Stats band */}
            <div className="mt-10 grid grid-cols-2 gap-4 rounded-2xl bg-charcoal p-6 sm:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.label} className="flex flex-col items-center text-center">
                  <GradientIcon size="sm" className="mb-3">
                    <stat.icon />
                  </GradientIcon>
                  <p className="font-display text-xl font-bold text-white">{stat.value}</p>
                  <p className="mt-1 text-[11px] font-medium text-champagne-light uppercase tracking-wide">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
