import { useEffect, useState } from "react";
import { appointmentsApi, servicesApi, type Appointment } from "../../api/client";

function startOfWeek(): Date {
  const now = new Date();
  const day = now.getDay();
  const diff = (day === 0 ? -6 : 1) - day;
  const monday = new Date(now);
  monday.setDate(now.getDate() + diff);
  monday.setHours(0, 0, 0, 0);
  return monday;
}

export default function RevenuePanel() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [servicePrices, setServicePrices] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([appointmentsApi.list({ page_size: 100 }), servicesApi.list()]).then(
      ([apptRes, servicesRes]) => {
        const prices: Record<string, number> = {};
        servicesRes.data.results.forEach((s) => {
          prices[s.name] = Number(s.price);
        });
        setServicePrices(prices);
        setAppointments(apptRes.data.results);
        setLoading(false);
      }
    );
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-10">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const weekStart = startOfWeek();
  const completed = appointments.filter((a) => a.status === "completed");
  const booked = appointments.filter((a) =>
    ["pending", "confirmed", "completed"].includes(a.status)
  );

  const priceFor = (a: Appointment) => servicePrices[a.service_name] ?? 0;

  const weekRevenue = completed
    .filter((a) => new Date(a.start_datetime) >= weekStart)
    .reduce((sum, a) => sum + priceFor(a), 0);
  const bookedRevenue = booked.reduce((sum, a) => sum + priceFor(a), 0);
  const avgTicket = completed.length
    ? completed.reduce((sum, a) => sum + priceFor(a), 0) / completed.length
    : 0;

  const byService: Record<string, number> = {};
  const byStaff: Record<string, { total: number; count: number }> = {};
  completed.forEach((a) => {
    byService[a.service_name] = (byService[a.service_name] ?? 0) + priceFor(a);
    if (!byStaff[a.staff_name]) byStaff[a.staff_name] = { total: 0, count: 0 };
    byStaff[a.staff_name].total += priceFor(a);
    byStaff[a.staff_name].count += 1;
  });

  const serviceEntries = Object.entries(byService).sort((a, b) => b[1] - a[1]);
  const staffEntries = Object.entries(byStaff).sort((a, b) => b[1].total - a[1].total);
  const maxServiceRevenue = Math.max(1, ...serviceEntries.map(([, v]) => v));

  return (
    <div>
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <div className="rounded-2xl bg-brand-50 p-5 text-brand-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            This week's revenue
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            ${weekRevenue.toFixed(0)}
          </p>
        </div>
        <div className="rounded-2xl bg-gray-50 p-5 text-gray-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Booked revenue (all)
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            ${bookedRevenue.toFixed(0)}
          </p>
        </div>
        <div className="rounded-2xl bg-blue-50 p-5 text-blue-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Completed visits
          </p>
          <p className="mt-1 font-display text-2xl font-bold">{completed.length}</p>
        </div>
        <div className="rounded-2xl bg-red-50 p-5 text-red-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Avg. ticket price
          </p>
          <p className="mt-1 font-display text-2xl font-bold">
            ${avgTicket.toFixed(0)}
          </p>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Revenue by service
          </h3>
          <div className="mt-4 space-y-3">
            {serviceEntries.length === 0 && (
              <p className="text-sm text-gray-400">No completed visits yet.</p>
            )}
            {serviceEntries.map(([name, total]) => (
              <div key={name}>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-700">{name}</span>
                  <span className="font-medium text-gray-900">
                    ${total.toFixed(0)}
                  </span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-gray-100">
                  <div
                    className="h-1.5 rounded-full bg-brand-600"
                    style={{ width: `${(total / maxServiceRevenue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Revenue by staff
          </h3>
          <div className="mt-4 space-y-3">
            {staffEntries.length === 0 && (
              <p className="text-sm text-gray-400">No completed visits yet.</p>
            )}
            {staffEntries.map(([name, { total, count }]) => (
              <div key={name} className="flex items-center justify-between text-sm">
                <div>
                  <p className="text-gray-700">{name}</p>
                  <p className="text-xs text-gray-400">{count} bookings</p>
                </div>
                <span className="font-medium text-gray-900">${total.toFixed(0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
