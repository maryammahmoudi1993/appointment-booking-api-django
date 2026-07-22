import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { staffApi, servicesApi, type StaffProfile, type Service } from "../api/client";
import SectionHeading from "../components/ui/SectionHeading";

export default function Staff() {
  const [staff, setStaff] = useState<StaffProfile[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([staffApi.list(), servicesApi.list()])
      .then(([staffRes, servicesRes]) => {
        setStaff(staffRes.data.results);
        setServices(servicesRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const serviceName = (id: number) =>
    services.find((s) => s.id === id)?.name ?? `Service #${id}`;

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
          eyebrow="Meet the Team"
          title="Our Specialists"
          description="Experienced specialists, ready to help you look and feel your best."
        />

        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          {staff.map((s) => (
            <div
              key={s.id}
              className="rounded-2xl border border-champagne/20 bg-white p-7 shadow-sm transition-all hover:shadow-md hover:scale-[1.01]"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-rosegold-gradient font-display text-sm font-bold text-white shadow-sm">
                  {s.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase()}
                </span>
                <div>
                  <h3 className="font-display text-lg font-semibold text-charcoal">
                    {s.full_name}
                  </h3>
                  {s.average_rating !== null && (
                    <p className="text-xs text-champagne-dark">
                      ★ {s.average_rating.toFixed(1)} ({s.review_count} review
                      {s.review_count === 1 ? "" : "s"})
                    </p>
                  )}
                </div>
              </div>
              {s.bio && <p className="mt-4 text-sm leading-relaxed text-charcoal-light">{s.bio}</p>}
              {s.services_offered.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {s.services_offered.map((id) => (
                    <span
                      key={id}
                      className="rounded-full bg-champagne/10 px-2.5 py-0.5 text-xs font-medium text-champagne-dark"
                    >
                      {serviceName(id)}
                    </span>
                  ))}
                </div>
              )}
              <Link
                to={`/book?staff=${s.id}`}
                className="mt-5 inline-flex items-center justify-center rounded-full bg-rosegold-gradient px-5 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:scale-[1.02] active:scale-[0.98]"
              >
                Book
              </Link>
            </div>
          ))}
        </div>

        {staff.length === 0 && (
          <p className="mt-10 text-center text-charcoal-light">
            Our team will be listed here soon.
          </p>
        )}
      </div>
    </div>
  );
}
