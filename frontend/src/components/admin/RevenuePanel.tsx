import { useEffect, useState } from "react";
import {
  analyticsApi,
  type RevenueAnalytics,
  type ServiceAnalyticsEntry,
  type StaffAnalyticsEntry,
} from "../../api/client";

export default function RevenuePanel() {
  const [revenue, setRevenue] = useState<RevenueAnalytics | null>(null);
  const [services, setServices] = useState<ServiceAnalyticsEntry[]>([]);
  const [staff, setStaff] = useState<StaffAnalyticsEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    Promise.all([
      analyticsApi.revenue(),
      analyticsApi.service(),
      analyticsApi.staff(),
    ])
      .then(([revenueResponse, serviceResponse, staffResponse]) => {
        setRevenue(revenueResponse.data);
        setServices(serviceResponse.data.results);
        setStaff(staffResponse.data.results);
      })
      .catch(() => {
        setError("Revenue analytics could not be loaded. Please try again.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) {
    return (
      <div className="flex justify-center py-10" aria-label="Loading revenue analytics">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !revenue) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center" role="alert">
        <p className="text-rose-800">{error || "Revenue analytics are unavailable."}</p>
        <button onClick={load} className="beauty-button mt-4">Try again</button>
      </div>
    );
  }

  const maxServiceRevenue = Math.max(
    1,
    ...services.map((service) => Number(service.total_revenue)),
  );

  return (
    <div>
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl bg-brand-50 p-5 text-brand-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Completed revenue
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            ${Number(revenue.total_revenue).toFixed(0)}
          </p>
        </div>
        <div className="rounded-2xl bg-champagne/10 p-5 text-blue-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Completed visits
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            {revenue.total_bookings}
          </p>
        </div>
        <div className="rounded-2xl bg-rose-50 p-5 text-rose-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Average ticket
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            ${Number(revenue.average_ticket).toFixed(0)}
          </p>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-charcoal-light">
            Revenue by service
          </h3>
          <div className="mt-4 space-y-3">
            {services.length === 0 && (
              <p className="text-sm text-charcoal-light/70">No completed visits yet.</p>
            )}
            {services.map((service) => {
              const total = Number(service.total_revenue);
              return (
                <div key={service.service_id}>
                  <div className="flex justify-between text-sm">
                    <span className="text-charcoal">{service.service_name}</span>
                    <span className="font-medium text-charcoal">${total.toFixed(0)}</span>
                  </div>
                  <div className="mt-1 h-1.5 rounded-full bg-blush-light">
                    <div
                      className="h-1.5 rounded-full bg-brand-600"
                      style={{ width: `${(total / maxServiceRevenue) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-charcoal-light">
            Revenue by staff
          </h3>
          <div className="mt-4 space-y-3">
            {staff.length === 0 && (
              <p className="text-sm text-charcoal-light/70">No completed visits yet.</p>
            )}
            {staff.map((entry) => (
              <div key={entry.staff_id} className="flex items-center justify-between text-sm">
                <div>
                  <p className="text-charcoal">{entry.staff_name}</p>
                  <p className="text-xs text-charcoal-light/70">
                    {entry.completed_bookings} completed
                  </p>
                </div>
                <span className="font-medium text-charcoal">
                  ${Number(entry.total_revenue).toFixed(0)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
