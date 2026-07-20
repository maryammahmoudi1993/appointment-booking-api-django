import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { servicesApi, type Service } from "../api/client";

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
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 lg:px-8">
      <div className="text-center">
        <h2 className="font-display text-3xl font-bold text-brand-900">
          Our Services
        </h2>
        <p className="mt-2 text-gray-600">
          Deep-cleansing facials to full-body massages — pick what suits you.
        </p>
      </div>
      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        {services.map((s) => (
          <div
            key={s.id}
            className="flex flex-col rounded-2xl border border-brand-100 bg-white p-6 shadow-sm transition hover:shadow-md"
          >
            <div className="flex items-start justify-between gap-4">
              <h3 className="font-display text-lg font-semibold text-brand-900">
                {s.name}
              </h3>
              <span className="whitespace-nowrap font-display text-lg font-bold text-brand-600">
                ${s.price}
              </span>
            </div>
            <span className="mt-1 text-xs font-medium uppercase tracking-wide text-gray-400">
              {s.duration_minutes} min
            </span>
            <p className="mt-3 flex-1 text-sm text-gray-600">
              {s.description}
            </p>
            <Link
              to={`/book?service=${s.id}`}
              className="mt-5 inline-flex w-fit items-center justify-center rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
            >
              Book
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
