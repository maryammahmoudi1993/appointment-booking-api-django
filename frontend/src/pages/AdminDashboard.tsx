import { useEffect, useState } from "react";
import {
  appointmentsApi,
  servicesApi,
  type Appointment,
  type Service,
} from "../api/client";
import StaffManager from "../components/admin/StaffManager";

type Tab = "appointments" | "services" | "staff";

const TABS: { key: Tab; label: string }[] = [
  { key: "appointments", label: "Appointments" },
  { key: "services", label: "Services" },
  { key: "staff", label: "Staff" },
];

export default function AdminDashboard() {
  const [tab, setTab] = useState<Tab>("appointments");

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <h2 className="font-display text-2xl font-bold text-brand-900">
        Admin Dashboard
      </h2>
      <div className="mt-6 flex gap-2 border-b border-brand-100">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`rounded-t-lg px-4 py-2.5 text-sm font-medium transition ${
              tab === t.key
                ? "border-b-2 border-brand-600 text-brand-700"
                : "text-gray-500 hover:text-brand-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="mt-6">
        {tab === "appointments" && <AppointmentsPanel />}
        {tab === "services" && <ServicesPanel />}
        {tab === "staff" && <StaffManager />}
      </div>
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-amber-100 text-amber-800",
  confirmed: "bg-brand-100 text-brand-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

function isSameDay(iso: string, ref: Date) {
  const d = new Date(iso);
  return (
    d.getFullYear() === ref.getFullYear() &&
    d.getMonth() === ref.getMonth() &&
    d.getDate() === ref.getDate()
  );
}

function isWithinNextDays(iso: string, days: number) {
  const d = new Date(iso).getTime();
  const now = Date.now();
  return d >= now - 86400000 && d <= now + days * 86400000;
}

function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "brand" | "amber" | "gray";
}) {
  const toneClasses = {
    brand: "bg-brand-50 text-brand-800",
    amber: "bg-amber-50 text-amber-800",
    gray: "bg-gray-50 text-gray-800",
  }[tone];
  return (
    <div className={`rounded-2xl p-5 ${toneClasses}`}>
      <p className="text-xs font-medium uppercase tracking-wide opacity-70">
        {label}
      </p>
      <p className="mt-1 font-display text-3xl font-bold">{value}</p>
    </div>
  );
}

function AppointmentsPanel() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAll = () => {
    setLoading(true);
    appointmentsApi
      .list()
      .then((res) => setAppointments(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleAction = async (
    id: number,
    action: "confirm" | "complete" | "cancel"
  ) => {
    try {
      if (action === "confirm") await appointmentsApi.confirm(id);
      else if (action === "complete") await appointmentsApi.complete(id);
      else await appointmentsApi.cancel(id);
      fetchAll();
    } catch {
      alert(`Failed to ${action} appointment #${id}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-10">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const today = new Date();
  const todayCount = appointments.filter((a) =>
    isSameDay(a.start_datetime, today)
  ).length;
  const pendingCount = appointments.filter((a) => a.status === "pending").length;
  const weekCount = appointments.filter((a) =>
    isWithinNextDays(a.start_datetime, 7)
  ).length;

  return (
    <div>
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <StatCard label="Today's appointments" value={todayCount} tone="brand" />
        <StatCard label="Pending confirmations" value={pendingCount} tone="amber" />
        <StatCard label="This week's bookings" value={weekCount} tone="gray" />
      </div>
      <div className="space-y-4">
        {appointments.map((a) => (
          <div
            key={a.id}
            className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold text-gray-900">
                  #{a.id} &middot; {a.service_name}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  {a.customer_name} with {a.staff_name}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(a.start_datetime).toLocaleString()} -{" "}
                  {new Date(a.end_datetime).toLocaleTimeString()}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
                  STATUS_COLORS[a.status] || "bg-gray-100 text-gray-800"
                }`}
              >
                {a.status}
              </span>
            </div>
            {a.status === "pending" && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => handleAction(a.id, "confirm")}
                  className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700"
                >
                  Confirm
                </button>
                <button
                  onClick={() => handleAction(a.id, "cancel")}
                  className="rounded-full border border-red-200 px-4 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50"
                >
                  Cancel
                </button>
              </div>
            )}
            {a.status === "confirmed" && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => handleAction(a.id, "complete")}
                  className="rounded-full bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  Complete
                </button>
                <button
                  onClick={() => handleAction(a.id, "cancel")}
                  className="rounded-full border border-red-200 px-4 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ServicesPanel() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    duration_minutes: 60,
    price: "0.00",
  });

  const fetchServices = () => {
    setLoading(true);
    servicesApi
      .list()
      .then((res) => setServices(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await servicesApi.create({
        ...form,
        duration_minutes: Number(form.duration_minutes),
      });
      setShowForm(false);
      setForm({ name: "", description: "", duration_minutes: 60, price: "0.00" });
      fetchServices();
    } catch {
      alert("Failed to create service.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this service?")) return;
    try {
      await servicesApi.delete(id);
      fetchServices();
    } catch {
      alert("Failed to delete service.");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-10">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => setShowForm(!showForm)}
        className="mb-4 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
      >
        {showForm ? "Cancel" : "+ Add service"}
      </button>
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <input
              placeholder="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Price"
              type="number"
              step="0.01"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              required
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Duration (minutes)"
              type="number"
              value={form.duration_minutes}
              onChange={(e) =>
                setForm({ ...form, duration_minutes: Number(e.target.value) })
              }
              required
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Description"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <button
            type="submit"
            className="mt-4 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white hover:bg-brand-700"
          >
            Create
          </button>
        </form>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        {services.map((s) => (
          <div
            key={s.id}
            className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{s.name}</h3>
                <p className="mt-1 text-sm text-gray-600">{s.description}</p>
              </div>
              <button
                onClick={() => handleDelete(s.id)}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Delete
              </button>
            </div>
            <div className="mt-3 flex items-center gap-4 text-sm">
              <span className="font-display font-semibold text-brand-600">
                ${s.price}
              </span>
              <span className="text-gray-500">{s.duration_minutes} min</span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  s.is_active
                    ? "bg-brand-100 text-brand-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {s.is_active ? "Active" : "Inactive"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

