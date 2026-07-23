import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { servicesApi, type Service } from "../../api/client";
import SectionHeading from "../ui/SectionHeading";
import { imageForService } from "../../utils/serviceImage";

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

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {services === null &&
            Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="animate-pulse overflow-hidden rounded-2xl bg-white shadow-sm"
                aria-hidden="true"
              >
                <div className="h-36 bg-blush" />
                <div className="p-5">
                  <div className="h-4 w-2/3 rounded bg-blush" />
                  <div className="mt-3 h-3 w-full rounded bg-blush" />
                  <div className="mt-4 h-8 w-full rounded-full bg-blush" />
                </div>
              </div>
            ))}

          {services?.map((service) => {
            const image = imageForService(service.name);
            return (
              <div
                key={service.id}
                className="group overflow-hidden rounded-2xl bg-white shadow-sm transition-all hover:shadow-md hover:scale-[1.01]"
              >
                <Link to={`/services/${service.id}`} className="block h-36 overflow-hidden">
                  <img
                    src={image}
                    alt=""
                    width={350}
                    height={144}
                    loading="lazy"
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                </Link>
                <div className="p-5">
                  <h3 className="font-display text-base font-semibold text-charcoal">
                    <Link to={`/services/${service.id}`}>{service.name}</Link>
                  </h3>
                  <p className="mt-1.5 text-xs leading-relaxed text-charcoal-light line-clamp-2">
                    {service.description}
                  </p>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[11px] font-medium uppercase tracking-wide text-charcoal-light/70">
                      {service.duration_minutes} min
                    </span>
                    <span className="font-display text-base font-bold text-coral-dark">
                      ${service.price}
                    </span>
                  </div>
                  <Link
                    to={`/book?service=${service.id}`}
                    className="mt-4 block w-full rounded-full bg-coral py-2 text-center text-sm font-semibold text-white transition-colors hover:bg-coral-dark"
                  >
                    Book Now
                  </Link>
                </div>
              </div>
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
            className="inline-flex items-center gap-2 rounded-full border border-charcoal/15 bg-white px-6 py-2.5 text-sm font-semibold text-charcoal transition-all hover:border-coral hover:text-coral-dark"
          >
            View All Services
          </Link>
        </div>
      </div>
    </section>
  );
}
