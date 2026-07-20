import { useEffect, useState } from "react";
import {
  staffApi,
  servicesApi,
  workingHoursApi,
  type StaffProfile,
  type Service,
} from "../../api/client";

const WEEKDAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

function extractErrorMessage(err: any, fallback: string): string {
  const data = err.response?.data;
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  const firstFieldError = Object.values(data).flat()[0];
  return typeof firstFieldError === "string" ? firstFieldError : fallback;
}

const EMPTY_NEW_STAFF = {
  username: "",
  password: "",
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
  bio: "",
};

export default function StaffManager() {
  const [staff, setStaff] = useState<StaffProfile[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchAll = () => {
    setLoading(true);
    Promise.all([staffApi.list(), servicesApi.list()])
      .then(([staffRes, servicesRes]) => {
        setStaff(staffRes.data.results);
        setServices(servicesRes.data.results);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

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
        onClick={() => setShowAddForm((v) => !v)}
        className="mb-4 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
      >
        {showAddForm ? "Cancel" : "+ Add staff"}
      </button>

      {showAddForm && (
        <AddStaffForm
          services={services}
          onCreated={() => {
            setShowAddForm(false);
            fetchAll();
          }}
        />
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {staff.map((s) => (
          <StaffCard
            key={s.id}
            staff={s}
            services={services}
            onChanged={fetchAll}
          />
        ))}
      </div>
    </div>
  );
}

function AddStaffForm({
  services,
  onCreated,
}: {
  services: Service[];
  onCreated: () => void;
}) {
  const [form, setForm] = useState(EMPTY_NEW_STAFF);
  const [serviceIds, setServiceIds] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const toggleService = (id: number) => {
    setServiceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await staffApi.onboard({ ...form, services_offered: serviceIds });
      setForm(EMPTY_NEW_STAFF);
      setServiceIds([]);
      onCreated();
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to add staff member."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
    >
      <h3 className="font-display font-semibold text-brand-900">
        New staff member
      </h3>
      {error && (
        <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <input
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <input
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
          minLength={8}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <input
          placeholder="First name"
          value={form.first_name}
          onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <input
          placeholder="Last name"
          value={form.last_name}
          onChange={(e) => setForm({ ...form, last_name: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <input
          placeholder="Phone"
          value={form.phone_number}
          onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
        <textarea
          placeholder="Bio"
          value={form.bio}
          onChange={(e) => setForm({ ...form, bio: e.target.value })}
          rows={2}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 sm:col-span-2"
        />
      </div>

      <div className="mt-4">
        <p className="text-sm font-medium text-gray-700">Abilities</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {services.map((sv) => (
            <label
              key={sv.id}
              className={`cursor-pointer rounded-full border px-3 py-1 text-xs font-medium transition ${
                serviceIds.includes(sv.id)
                  ? "border-brand-600 bg-brand-50 text-brand-700"
                  : "border-gray-200 text-gray-600 hover:border-brand-300"
              }`}
            >
              <input
                type="checkbox"
                checked={serviceIds.includes(sv.id)}
                onChange={() => toggleService(sv.id)}
                className="mr-1.5 hidden"
              />
              {sv.name}
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="mt-5 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
      >
        {submitting ? "Adding..." : "Add staff member"}
      </button>
    </form>
  );
}

type DayState = {
  enabled: boolean;
  start: string;
  end: string;
  id: number | null;
};

function defaultDays(): DayState[] {
  return Array.from({ length: 7 }, () => ({
    enabled: false,
    start: "09:00",
    end: "17:00",
    id: null,
  }));
}

function StaffCard({
  staff,
  services,
  onChanged,
}: {
  staff: StaffProfile;
  services: Service[];
  onChanged: () => void;
}) {
  const [bio, setBio] = useState(staff.bio);
  const [serviceIds, setServiceIds] = useState<number[]>(
    staff.services_offered
  );
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  const [hoursOpen, setHoursOpen] = useState(false);
  const [hoursLoading, setHoursLoading] = useState(false);
  const [days, setDays] = useState<DayState[]>(defaultDays());
  const [savingHours, setSavingHours] = useState(false);
  const [hoursError, setHoursError] = useState("");
  const [hoursSaved, setHoursSaved] = useState(false);

  const toggleService = (id: number) => {
    setProfileSaved(false);
    setServiceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const saveProfile = async () => {
    setProfileError("");
    setSavingProfile(true);
    try {
      await staffApi.update(staff.id, { bio, services_offered: serviceIds });
      setProfileSaved(true);
      onChanged();
    } catch (err: any) {
      setProfileError(extractErrorMessage(err, "Failed to save changes."));
    } finally {
      setSavingProfile(false);
    }
  };

  const loadHours = () => {
    setHoursOpen(true);
    setHoursLoading(true);
    workingHoursApi
      .list(staff.user)
      .then((res) => {
        const next = defaultDays();
        for (const wh of res.data.results) {
          next[wh.weekday] = {
            enabled: true,
            start: wh.start_time.slice(0, 5),
            end: wh.end_time.slice(0, 5),
            id: wh.id,
          };
        }
        setDays(next);
      })
      .finally(() => setHoursLoading(false));
  };

  const updateDay = (index: number, patch: Partial<DayState>) => {
    setHoursSaved(false);
    setDays((prev) =>
      prev.map((d, i) => (i === index ? { ...d, ...patch } : d))
    );
  };

  const saveHours = async () => {
    setHoursError("");
    setSavingHours(true);
    try {
      await Promise.all(
        days.map((day, weekday) => {
          if (day.enabled && !day.id) {
            return workingHoursApi.create({
              staff: staff.user,
              weekday,
              start_time: day.start,
              end_time: day.end,
            });
          }
          if (day.enabled && day.id) {
            return workingHoursApi.update(day.id, {
              start_time: day.start,
              end_time: day.end,
            });
          }
          if (!day.enabled && day.id) {
            return workingHoursApi.delete(day.id);
          }
          return Promise.resolve();
        })
      );
      setHoursSaved(true);
      loadHours();
    } catch (err: any) {
      setHoursError(extractErrorMessage(err, "Failed to save hours."));
    } finally {
      setSavingHours(false);
    }
  };

  return (
    <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{staff.full_name}</h3>
          <p className="text-xs text-gray-400">@{staff.username}</p>
        </div>
      </div>

      <label className="mt-4 block text-xs font-medium uppercase tracking-wide text-gray-500">
        Bio
      </label>
      <textarea
        value={bio}
        onChange={(e) => {
          setProfileSaved(false);
          setBio(e.target.value);
        }}
        rows={2}
        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      />

      <label className="mt-4 block text-xs font-medium uppercase tracking-wide text-gray-500">
        Abilities
      </label>
      <div className="mt-2 flex flex-wrap gap-2">
        {services.map((sv) => (
          <label
            key={sv.id}
            className={`cursor-pointer rounded-full border px-3 py-1 text-xs font-medium transition ${
              serviceIds.includes(sv.id)
                ? "border-brand-600 bg-brand-50 text-brand-700"
                : "border-gray-200 text-gray-600 hover:border-brand-300"
            }`}
          >
            <input
              type="checkbox"
              checked={serviceIds.includes(sv.id)}
              onChange={() => toggleService(sv.id)}
              className="mr-1.5 hidden"
            />
            {sv.name}
          </label>
        ))}
      </div>

      {profileError && (
        <p className="mt-3 rounded-lg bg-red-50 p-2 text-xs text-red-700">
          {profileError}
        </p>
      )}
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={saveProfile}
          disabled={savingProfile}
          className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {savingProfile ? "Saving..." : "Save changes"}
        </button>
        {profileSaved && (
          <span className="text-xs font-medium text-brand-700">Saved ✓</span>
        )}
      </div>

      <div className="mt-5 border-t border-gray-100 pt-4">
        {!hoursOpen ? (
          <button
            onClick={loadHours}
            className="text-xs font-semibold text-brand-700 hover:text-brand-800"
          >
            Manage working hours →
          </button>
        ) : hoursLoading ? (
          <div className="flex justify-center py-4">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
          </div>
        ) : (
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Working hours
            </p>
            <div className="mt-2 space-y-2">
              {WEEKDAYS.map((label, i) => (
                <div key={label} className="flex items-center gap-2 text-sm">
                  <label className="flex w-28 items-center gap-2">
                    <input
                      type="checkbox"
                      checked={days[i].enabled}
                      onChange={(e) =>
                        updateDay(i, { enabled: e.target.checked })
                      }
                      className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                    />
                    <span className="text-gray-700">{label}</span>
                  </label>
                  <input
                    type="time"
                    value={days[i].start}
                    disabled={!days[i].enabled}
                    onChange={(e) => updateDay(i, { start: e.target.value })}
                    className="rounded-md border border-gray-300 px-2 py-1 text-xs disabled:bg-gray-50 disabled:text-gray-400"
                  />
                  <span className="text-gray-400">–</span>
                  <input
                    type="time"
                    value={days[i].end}
                    disabled={!days[i].enabled}
                    onChange={(e) => updateDay(i, { end: e.target.value })}
                    className="rounded-md border border-gray-300 px-2 py-1 text-xs disabled:bg-gray-50 disabled:text-gray-400"
                  />
                </div>
              ))}
            </div>
            {hoursError && (
              <p className="mt-3 rounded-lg bg-red-50 p-2 text-xs text-red-700">
                {hoursError}
              </p>
            )}
            <div className="mt-4 flex items-center gap-3">
              <button
                onClick={saveHours}
                disabled={savingHours}
                className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
              >
                {savingHours ? "Saving..." : "Save hours"}
              </button>
              {hoursSaved && (
                <span className="text-xs font-medium text-brand-700">
                  Saved ✓
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
