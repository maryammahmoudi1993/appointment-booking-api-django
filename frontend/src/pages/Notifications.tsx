import { useEffect, useState } from "react";
import { appointmentsApi, notificationsApi, type Appointment, type Notification } from "../api/client";
import PageHero from "../components/ui/PageHero";
import { useAuth } from "../context/AuthContext";

type Preferences = { email: boolean; sms: boolean; reminders: boolean };
const defaultPreferences: Preferences = { email: true, sms: false, reminders: true };

export default function Notifications() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [preferences, setPreferences] = useState<Preferences>(() => {
    try {
      return JSON.parse(localStorage.getItem("beauty-notification-preferences") || "") as Preferences;
    } catch {
      return defaultPreferences;
    }
  });

  useEffect(() => {
    const request = user?.role === "admin"
      ? notificationsApi.list().then((res) => setNotifications(res.data.results))
      : appointmentsApi.list({ page_size: 20 }).then((res) => setAppointments(res.data.results));
    request.catch(() => {}).finally(() => setLoading(false));
  }, [user?.role]);

  const save = () => {
    localStorage.setItem("beauty-notification-preferences", JSON.stringify(preferences));
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2500);
  };

  return (
    <>
      <PageHero
        eyebrow="Your inbox"
        title="Every detail, right on time."
        description="Appointment updates and the reminder preferences saved on this device."
      />
      <section className="mx-auto grid max-w-7xl gap-8 px-4 py-14 sm:px-6 lg:grid-cols-[1fr_360px] lg:px-8 lg:py-20">
        <div>
          <h2 className="text-3xl text-heading">Recent updates</h2>
          {loading && <div className="beauty-skeleton mt-6 h-72 rounded-[28px]" aria-busy="true" />}
          {!loading && user?.role === "admin" && notifications.map((item) => (
            <article key={item.id} className="beauty-card mt-4 flex gap-4 p-5">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blush text-xl text-coral" aria-hidden="true">♢</span>
              <div><h3 className="font-sans text-sm font-bold text-heading">{item.subject}</h3><p className="mt-1 text-sm leading-6 text-secondary">{item.body}</p><time className="mt-2 block text-xs text-muted">{new Date(item.created_at).toLocaleString()}</time></div>
            </article>
          ))}
          {!loading && user?.role !== "admin" && appointments.map((item) => (
            <article key={item.id} className="beauty-card mt-4 flex gap-4 p-5">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blush text-xl text-coral" aria-hidden="true">▦</span>
              <div>
                <h3 className="font-sans text-sm font-bold text-heading">{item.status === "cancelled" ? "Appointment cancelled" : "Appointment update"}</h3>
                <p className="mt-1 text-sm leading-6 text-secondary">{item.service_name} with {item.staff_name} · {new Date(item.start_datetime).toLocaleString()}</p>
                <span className="mt-2 inline-block rounded-full bg-soft px-3 py-1 text-xs font-semibold capitalize text-coral">{item.status}</span>
              </div>
            </article>
          ))}
          {!loading && !notifications.length && !appointments.length && (
            <div className="beauty-card mt-6 p-10 text-center text-secondary">You’re all caught up. New booking updates will appear here.</div>
          )}
        </div>
        <aside className="beauty-card h-fit p-7">
          <p className="beauty-eyebrow">Preferences</p>
          <h2 className="mt-2 text-2xl text-heading">How should we reach you?</h2>
          <div className="mt-6 space-y-3">
            {([
              ["email", "Email updates", "Confirmations and changes"],
              ["sms", "Text messages", "Time-sensitive reminders"],
              ["reminders", "Appointment reminders", "A gentle prompt before your visit"],
            ] as const).map(([key, label, hint]) => (
              <label key={key} className="flex cursor-pointer items-center justify-between rounded-2xl bg-soft p-4">
                <span><span className="block text-sm font-bold text-heading">{label}</span><span className="mt-1 block text-xs text-muted">{hint}</span></span>
                <input className="beauty-toggle" type="checkbox" checked={preferences[key]} onChange={(event) => setPreferences({ ...preferences, [key]: event.target.checked })} />
              </label>
            ))}
          </div>
          <button onClick={save} className="beauty-button mt-6 w-full">Save preferences</button>
          <p role="status" className="mt-3 min-h-5 text-center text-sm text-success">{saved ? "Preferences saved." : ""}</p>
        </aside>
      </section>
    </>
  );
}
