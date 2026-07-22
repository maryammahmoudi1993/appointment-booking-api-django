import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { servicesApi, type Service } from "../api/client";
import SectionHeading from "../components/ui/SectionHeading";
import { imageForService } from "../utils/serviceImage";

export default function Services() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    servicesApi
      .list()
      .then((res) => setServices(res.data.results))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-champagne border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="bg-cream py-16">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="What We Offer"
          title="Our Services"
          description="Deep-cleansing facials to full-body massages — pick what suits you."
        />

        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          {services.map((s) => {
            const image = imageForService(s.name);
            return (
              <div
                key={s.id}
                className="flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm transition-all hover:shadow-md hover:scale-[1.01]"
              >
                <div className="flex">
                  <img
                    src={image}
                    alt=""
                    width={160}
                    height={160}
                    loading="lazy"
                    className="h-40 w-40 shrink-0 object-cover"
                  />
                  <div className="flex flex-1 flex-col p-5">
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-display text-lg font-semibold text-charcoal">
                        {s.name}
                      </h3>
                      <span className="whitespace-nowrap font-display text-lg font-bold text-coral-dark">
                        ${s.price}
                      </span>
                    </div>
                    <span className="mt-1 text-xs font-medium uppercase tracking-wide text-charcoal-light/70">
                      {s.duration_minutes} min
                    </span>
                    <p className="mt-2 flex-1 text-sm leading-relaxed text-charcoal-light line-clamp-3">
                      {s.description}
                    </p>
                    <Link
                      to={`/book?service=${s.id}`}
                      className="mt-3 inline-flex w-fit items-center justify-center rounded-full bg-coral px-5 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-coral-dark hover:shadow-md"
                    >
                      Book
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {services.length === 0 && (
          <p className="mt-10 text-center text-charcoal-light">
            No services available yet.
          </p>
        )}
      </div>
    </div>
  );
}
