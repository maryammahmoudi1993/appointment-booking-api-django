import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { servicesApi, type Service } from "../../api/client";
import GradientIcon from "../icons/GradientIcon";
import SectionHeading from "../ui/SectionHeading";
import { iconForService } from "../../utils/serviceIcon";

const TINTS = ["bg-blush-light", "bg-champagne/10", "bg-blush", "bg-cream"];

export default function ServicesGrid() {
  const [services, setServices] = useState<Service[] | null>(null);

  useEffect(() => {
    servicesApi
      .list()
      .then((res) => setServices(res.data.results.slice(0, 4)))
      .catch(() => setServices([]));
  }, []);

  return (
    <section className="py-20 bg-cream" aria-labelledby="services-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="Our Services"
          id="services-heading"
          title="Services You'll Love"
          description="Discover our curated collection of premium beauty and wellness treatments, each designed to leave you feeling radiant and refreshed."
        />

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {services === null &&
            Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="animate-pulse rounded-xl border border-champagne/20 bg-white p-8"
                aria-hidden="true"
              >
                <div className="h-16 w-16 rounded-2xl bg-blush" />
                <div className="mt-6 h-4 w-2/3 rounded bg-blush" />
                <div className="mt-3 h-3 w-full rounded bg-blush" />
                <div className="mt-2 h-3 w-4/5 rounded bg-blush" />
              </div>
            ))}

          {services?.map((service, i) => {
            const Icon = iconForService(service.name);
            return (
              <Link
                key={service.id}
                to={`/book?service=${service.id}`}
                className={`group relative flex flex-col rounded-xl border border-champagne/20 ${TINTS[i % TINTS.length]} p-8 shadow-sm transition-all hover:shadow-md hover:border-champagne/40 hover:scale-[1.02]`}
              >
                <GradientIcon size="lg">
                  <Icon />
                </GradientIcon>
                <h3 className="mt-6 font-display text-lg font-semibold text-charcoal group-hover:text-champagne-dark transition-colors">
                  {service.name}
                </h3>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-charcoal-light line-clamp-3">
                  {service.description}
                </p>
                <div className="mt-6 flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wide text-charcoal-light/70">
                    {service.duration_minutes} min
                  </span>
                  <span className="font-display text-lg font-bold text-champagne-dark">
                    ${service.price}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>

        {services && services.length === 0 && (
          <p className="mt-8 text-center text-sm text-charcoal-light">
            Services will appear here soon.
          </p>
        )}

        <div className="mt-12 text-center">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 rounded-full border border-charcoal/15 bg-white px-6 py-2.5 text-sm font-semibold text-charcoal transition-all hover:border-champagne hover:text-champagne-dark"
          >
            View All Services
          </Link>
        </div>
      </div>
    </section>
  );
}
