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
    <section id="services" className="scroll-mt-8 bg-[#fffaf7] py-20 sm:py-24" aria-labelledby="services-heading">
      <div className="mx-auto max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="Our Services"
          id="services-heading"
          title="Services You’ll Love"
          description="Signature treatments selected for visible results and a little more time for you."
        />

        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {services === null &&
            Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="beauty-skeleton h-[390px] rounded-[26px]"
                aria-hidden="true"
              >
              </div>
            ))}

          {services?.map((service) => {
            const image = imageForService(service.name);
            return (
              <div
                key={service.id}
                className="beauty-card group flex min-h-[430px] flex-col overflow-hidden transition duration-300 hover:-translate-y-1 hover:shadow-raised"
              >
                <Link to={`/services/${service.id}`} className="block aspect-[4/3] overflow-hidden">
                  <img
                    src={image}
                    alt=""
                    width={350}
                    height={144}
                    loading="lazy"
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.025]"
                  />
                </Link>
                <div className="flex flex-1 flex-col p-5">
                  <h3 className="font-display text-lg font-semibold text-heading">
                    <Link to={`/services/${service.id}`}>{service.name}</Link>
                  </h3>
                  <p className="mt-2 line-clamp-2 flex-1 text-xs leading-5 text-secondary">
                    {service.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-[.14em] text-muted">
                      {service.duration_minutes} min
                    </span>
                    <span className="font-display text-xl font-bold text-coral">
                      ${Number(service.price).toFixed(0)}
                    </span>
                  </div>
                  <Link
                    to={`/book?service=${service.id}`}
                    className="beauty-button mt-4 w-full"
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

        <div className="mt-8 text-center">
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
