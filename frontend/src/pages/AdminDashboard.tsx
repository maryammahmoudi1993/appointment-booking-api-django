import { useEffect, useState } from "react";
import {
  appointmentsApi,
  servicesApi,
  staffApi,
  type Appointment,
  type Service,
  type StaffProfile,
} from "../api/client";
import AdminCopilotPanel from "../components/admin/AdminCopilotPanel";
import InboxPanel from "../components/admin/InboxPanel";
import PromotionsPanel from "../components/admin/PromotionsPanel";
import RevenuePanel from "../components/admin/RevenuePanel";
import StaffManager from "../components/admin/StaffManager";

type Tab = "appointments" | "services" | "staff" | "marketing" | "revenue" | "inbox" | "analytics";

const TABS: { key: Tab; label: string }[] = [
  { key: "appointments", label: "Appointments" },
  { key: "services", label: "Services" },
  { key: "staff", label: "Staff" },
  { key: "marketing", label: "Marketing" },
  { key: "revenue", label: "Revenue" },
  { key: "inbox", label: "Inbox" },
  { key: "analytics", label: "Analytics AI" },
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
                : "text-charcoal-light hover:text-brand-700"
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
        {tab === "marketing" && <PromotionsPanel />}
        {tab === "revenue" && <RevenuePanel />}
        {tab === "inbox" && <InboxPanel />}
        {tab === "analytics" && <AnalyticsPanel />}
      </div>
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-champagne/20 text-champagne-dark",
  confirmed: "bg-brand-100 text-brand-800",
  completed: "bg-champagne/20 text-blue-800",
  cancelled: "bg-rose-100 text-rose-800",
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
    amber: "bg-champagne/10 text-champagne-dark",
    gray: "bg-cream text-charcoal",
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

const POLL_INTERVAL_MS = 20000;

function AppointmentsPanel() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [staffList, setStaffList] = useState<StaffProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [staffFilter, setStaffFilter] = useState("");

  const fetchAll = (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    appointmentsApi
      .list({
        status: statusFilter || undefined,
        staff: staffFilter ? Number(staffFilter) : undefined,
        page_size: 100,
      })
      .then((res) => setAppointments(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    staffApi.list().then((res) => setStaffList(res.data.results));
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(() => fetchAll(false), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, staffFilter]);

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

      <div className="mb-4 flex flex-wrap gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select
          value={staffFilter}
          onChange={(e) => setStaffFilter(e.target.value)}
          className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All staff</option>
          {staffList.map((s) => (
            <option key={s.id} value={s.user}>
              {s.full_name}
            </option>
          ))}
        </select>
      </div>

      {appointments.length === 0 ? (
        <p className="text-sm text-charcoal-light">No appointments match these filters.</p>
      ) : (
      <div className="space-y-4">
        {appointments.map((a) => (
          <div
            key={a.id}
            className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold text-charcoal">
                  #{a.id} &middot; {a.service_name}
                </p>
                <p className="mt-1 text-sm text-charcoal-light">
                  {a.customer_name} with {a.staff_name}
                </p>
                <p className="text-sm text-charcoal-light">
                  {new Date(a.start_datetime).toLocaleString()} -{" "}
                  {new Date(a.end_datetime).toLocaleTimeString()}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
                  STATUS_COLORS[a.status] || "bg-blush-light text-charcoal"
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
                  className="rounded-full border border-rose-200 px-4 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50"
                >
                  Cancel
                </button>
              </div>
            )}
            {a.status === "confirmed" && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => handleAction(a.id, "complete")}
                  className="rounded-full bg-champagne-dark px-4 py-1.5 text-xs font-semibold text-white hover:bg-champagne-dark/90"
                >
                  Complete
                </button>
                <button
                  onClick={() => handleAction(a.id, "cancel")}
                  className="rounded-full border border-rose-200 px-4 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      )}
    </div>
  );
}

const EMPTY_SERVICE_FORM = {
  name: "",
  description: "",
  duration_minutes: 60,
  price: "0.00",
};

function ServicesPanel() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_SERVICE_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);

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
      setForm(EMPTY_SERVICE_FORM);
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
              className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Price"
              type="number"
              step="0.01"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              required
              className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Duration (minutes)"
              type="number"
              value={form.duration_minutes}
              onChange={(e) =>
                setForm({ ...form, duration_minutes: Number(e.target.value) })
              }
              required
              className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Description"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
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
        {services.map((s) =>
          editingId === s.id ? (
            <EditServiceForm
              key={s.id}
              service={s}
              onDone={() => {
                setEditingId(null);
                fetchServices();
              }}
              onCancel={() => setEditingId(null)}
            />
          ) : (
            <div
              key={s.id}
              className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-charcoal">{s.name}</h3>
                  <p className="mt-1 text-sm text-charcoal-light">{s.description}</p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => setEditingId(s.id)}
                    className="text-sm text-brand-700 hover:text-brand-800"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="text-sm text-rose-600 hover:text-rose-800"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-4 text-sm">
                <span className="font-display font-semibold text-brand-600">
                  ${s.price}
                </span>
                <span className="text-charcoal-light">{s.duration_minutes} min</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    s.is_active
                      ? "bg-brand-100 text-brand-800"
                      : "bg-blush-light text-charcoal"
                  }`}
                >
                  {s.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}

function EditServiceForm({
  service,
  onDone,
  onCancel,
}: {
  service: Service;
  onDone: () => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    name: service.name,
    description: service.description,
    duration_minutes: service.duration_minutes,
    price: service.price,
    is_active: service.is_active,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await servicesApi.update(service.id, {
        ...form,
        duration_minutes: Number(form.duration_minutes),
      });
      onDone();
    } catch {
      setError("Failed to save changes.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-brand-300 bg-white p-6 shadow-sm"
    >
      {error && (
        <p className="mb-3 rounded-lg bg-rose-50 p-2 text-xs text-rose-700">
          {error}
        </p>
      )}
      <div className="grid gap-3">
        <input
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
          className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <textarea
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          rows={2}
          className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <div className="grid grid-cols-2 gap-3">
          <input
            type="number"
            step="0.01"
            value={form.price}
            onChange={(e) => setForm({ ...form, price: e.target.value })}
            required
            className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          <input
            type="number"
            value={form.duration_minutes}
            onChange={(e) =>
              setForm({ ...form, duration_minutes: Number(e.target.value) })
            }
            required
            className="rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-charcoal">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
            className="h-4 w-4 rounded border-champagne/30 text-brand-600 focus:ring-brand-500"
          />
          Active (visible to customers)
        </label>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save changes"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-full border border-champagne/30 px-4 py-1.5 text-xs font-medium text-charcoal-light hover:bg-cream"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

function AnalyticsPanel() {
  const [bookingStats, setBookingStats] = useState<{
    total: number;
    completion_rate: number;
    cancellation_rate: number;
  } | null>(null);

  useEffect(() => {
    import("../api/client").then(({ analyticsApi }) =>
      analyticsApi.bookings().then((res) => setBookingStats(res.data))
    );
  }, []);

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <h3 className="mb-4 font-display text-lg font-bold text-charcoal">
          Business Overview
        </h3>
        {bookingStats ? (
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <StatCard label="Total Bookings" value={bookingStats.total} tone="brand" />
            <StatCard label="Completion Rate" value={Math.round(bookingStats.completion_rate)} tone="gray" />
            <StatCard label="Cancellation Rate" value={Math.round(bookingStats.cancellation_rate)} tone="amber" />
          </div>
        ) : (
          <div className="flex justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
          </div>
        )}
        <AdminCopilotPanel />
      </div>
      <div>
        <h3 className="mb-4 font-display text-lg font-bold text-charcoal">
          AI Assistant
        </h3>
        <p className="mb-4 text-sm text-charcoal-light">
          Ask the AI copilot about your business performance. Try:
        </p>
        <ul className="space-y-2 text-sm text-charcoal-light">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            &ldquo;Show me this month&apos;s revenue breakdown&rdquo;
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            &ldquo;Who is our top-performing staff member?&rdquo;
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            &ldquo;What are our most popular services?&rdquo;
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            &ldquo;Forecast revenue for the next 30 days&rdquo;
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            &ldquo;What is our appointment completion rate?&rdquo;
          </li>
        </ul>
      </div>
    </div>
  );
}

