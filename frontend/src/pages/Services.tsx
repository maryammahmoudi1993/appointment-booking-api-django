import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { servicesApi, type Service } from "../api/client";
import { imageForService } from "../utils/serviceImage";
import PageHero from "../components/ui/PageHero";
import facialIcon from "../assets/landing/icon-facial-care-clean.webp";
import hairIcon from "../assets/landing/icon-hair-styling-clean.webp";
import nailIcon from "../assets/landing/icon-nail-polish-clean.webp";
import spaIcon from "../assets/landing/icon-spa-relax-clean.webp";
import allServicesIcon from "../assets/landing/icon-all-services-clean.webp";

const filters = [
  { key: "all", label: "All services", icon: allServicesIcon, terms: [] },
  { key: "hair", label: "Hair", icon: hairIcon, terms: ["hair", "cut", "style", "color", "beard"] },
  { key: "facial", label: "Facials", icon: facialIcon, terms: ["facial", "skin", "brow"] },
  { key: "nails", label: "Nails", icon: nailIcon, terms: ["nail", "manicure", "pedicure"] },
  { key: "spa", label: "Spa", icon: spaIcon, terms: ["massage", "spa", "body"] },
];

export default function Services() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const requestedCategory = searchParams.get("category") ?? "all";
  const [filter, setFilter] = useState(
    filters.some((item) => item.key === requestedCategory)
      ? requestedCategory
      : "all",
  );

  const load = () => {
    setLoading(true);
    setError("");
    servicesApi.list()
      .then((res) => setServices(res.data.results))
      .catch(() => setError("We couldn’t load our service menu. Please try again."))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);
  useEffect(() => {
    setFilter(
      filters.some((item) => item.key === requestedCategory)
        ? requestedCategory
        : "all",
    );
  }, [requestedCategory]);

  const visible = useMemo(() => {
    const active = filters.find((item) => item.key === filter) ?? filters[0];
    return services.filter((service) => {
      const haystack = `${service.name} ${service.description}`.toLowerCase();
      const categoryMatch = !active.terms.length || active.terms.some((term) => haystack.includes(term));
      const queryMatch = !query || haystack.includes(query.toLowerCase());
      return categoryMatch && queryMatch;
    });
  }, [filter, query, services]);

  return (
    <>
      <PageHero
        eyebrow="Our treatments"
        title="Services made for your kind of glow."
        description="Explore expert hair, skin, nail, and body treatments—each tailored around you and your time."
      />
      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <div className="beauty-card p-4 sm:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex gap-3 overflow-x-auto pb-2 lg:pb-0" role="group" aria-label="Filter services by category">
              {filters.map((item) => (
                <button
                  key={item.key}
                  onClick={() => {
                    setFilter(item.key);
                    setSearchParams(item.key === "all" ? {} : { category: item.key });
                  }}
                  aria-pressed={filter === item.key}
                  className={`flex min-w-fit items-center gap-2 rounded-[18px] border px-4 py-2.5 text-sm font-semibold transition ${
                    filter === item.key ? "border-coral bg-blush text-coral shadow-raised" : "border-transparent bg-soft text-secondary hover:border-rose/25"
                  }`}
                >
                  <img src={item.icon} alt="" width="256" height="256" className="h-8 w-8 rounded-xl object-cover" />
                  {item.label}
                </button>
              ))}
            </div>
            <label className="relative min-w-[260px]">
              <span className="sr-only">Search services</span>
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true">⌕</span>
              <input className="beauty-input mt-0 pl-10" type="search" placeholder="Search treatments…" value={query} onChange={(event) => setQuery(event.target.value)} />
            </label>
          </div>
        </div>

        {loading && (
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true">
            {[1, 2, 3, 4, 5, 6].map((n) => <div key={n} className="beauty-skeleton h-96 rounded-[28px]" />)}
          </div>
        )}
        {error && (
          <div role="alert" className="beauty-card mx-auto mt-10 max-w-xl p-10 text-center">
            <p className="text-error">{error}</p>
            <button onClick={load} className="beauty-button mt-5">Try again</button>
          </div>
        )}
        {!loading && !error && (
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {visible.map((service) => (
              <article key={service.id} className="beauty-card group overflow-hidden">
                <Link to={`/services/${service.id}`} className="block h-56 overflow-hidden">
                  <img src={imageForService(service.name)} alt={`${service.name} service`} width="700" height="700" loading="lazy" className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]" />
                </Link>
                <div className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <h2 className="text-2xl text-heading"><Link to={`/services/${service.id}`}>{service.name}</Link></h2>
                    <span className="font-display text-xl font-bold text-coral">${Number(service.price).toFixed(0)}</span>
                  </div>
                  <p className="mt-2 text-xs font-bold uppercase tracking-[.16em] text-muted">{service.duration_minutes} minutes</p>
                  <p className="mt-3 line-clamp-3 text-sm leading-6 text-secondary">{service.description}</p>
                  <div className="mt-6 grid grid-cols-2 gap-3">
                    <Link to={`/services/${service.id}`} className="beauty-button-secondary text-center">Details</Link>
                    <Link to={`/book?service=${service.id}`} className="beauty-button text-center">Book now</Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
        {!loading && !error && !visible.length && (
          <div className="beauty-card mx-auto mt-10 max-w-xl p-10 text-center">
            <span className="text-5xl" aria-hidden="true">✦</span>
            <h2 className="mt-4 text-2xl text-heading">No matching services</h2>
            <p className="mt-2 text-secondary">Try another category or a broader search.</p>
            <button onClick={() => { setQuery(""); setFilter("all"); setSearchParams({}); }} className="beauty-button-secondary mt-5">Clear filters</button>
          </div>
        )}
      </section>
    </>
  );
}
