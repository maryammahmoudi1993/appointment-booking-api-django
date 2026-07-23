import { useEffect, useState } from "react";
import { appointmentsApi, loyaltyApi } from "../api/client";
import { useAuth } from "../context/AuthContext";
import PageHero from "../components/ui/PageHero";
import avatar from "../assets/landing/avatar-2.webp";

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    email: user?.email ?? "",
    phone_number: user?.phone_number ?? "",
  });
  const [visits, setVisits] = useState(0);
  const [points, setPoints] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      appointmentsApi.list({ status: "completed", page_size: 100 }),
      user?.role === "customer" ? loyaltyApi.summary() : Promise.resolve(null),
    ]).then(([appointments, loyalty]) => {
      setVisits(appointments.data.count);
      if (loyalty) setPoints(loyalty.data.balance);
    }).catch(() => {});
  }, [user?.role]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    setError("");
    try {
      await updateProfile(form);
      setMessage("Your profile has been updated.");
    } catch (err: any) {
      const data = err.response?.data;
      setError(typeof data === "object" ? Object.values(data).flat().join(" ") : "We could not save your profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHero eyebrow="My account" title="A profile made personal." description="Keep your contact details current and see the little milestones from your salon journey." />
      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
        <div className="grid gap-8 lg:grid-cols-[300px_1fr]">
          <aside className="beauty-card h-fit p-7 text-center">
            <div className="relative mx-auto w-fit">
              <img src={avatar} alt="" width="200" height="200" className="h-28 w-28 rounded-full border-4 border-surface object-cover shadow-raised" />
              <span className="absolute bottom-1 right-1 flex h-8 w-8 items-center justify-center rounded-full bg-coral text-xs text-white" aria-hidden="true">✦</span>
            </div>
            <h2 className="mt-5 text-2xl text-heading">{[user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username}</h2>
            <p className="mt-1 text-sm text-coral">{user?.email}</p>
            <div className="mt-7 grid grid-cols-2 gap-3">
              <div className="rounded-2xl bg-soft p-4"><strong className="block font-display text-2xl text-heading">{visits}</strong><span className="text-xs text-muted">visits</span></div>
              <div className="rounded-2xl bg-soft p-4"><strong className="block font-display text-2xl text-heading">{points ?? "—"}</strong><span className="text-xs text-muted">points</span></div>
            </div>
            <p className="mt-6 rounded-full bg-gold/10 px-4 py-2 text-xs font-bold uppercase tracking-wider text-gold">Gold member</p>
          </aside>
          <form onSubmit={submit} className="beauty-card p-6 sm:p-9">
            <p className="beauty-eyebrow">Personal information</p>
            <h2 className="mt-2 text-3xl text-heading">Your details</h2>
            <div className="mt-7 grid gap-5 sm:grid-cols-2">
              <label className="beauty-label">First name<input className="beauty-input" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} autoComplete="given-name" /></label>
              <label className="beauty-label">Last name<input className="beauty-input" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} autoComplete="family-name" /></label>
              <label className="beauty-label sm:col-span-2">Email address<input className="beauty-input" required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" /></label>
              <label className="beauty-label sm:col-span-2">Phone number<input className="beauty-input" value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} autoComplete="tel" /></label>
            </div>
            {error && <p role="alert" className="mt-5 rounded-2xl bg-error/10 p-4 text-sm text-error">{error}</p>}
            <div className="mt-7 flex flex-wrap items-center gap-4">
              <button className="beauty-button min-w-40" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
              <p role="status" className="text-sm text-success">{message}</p>
            </div>
          </form>
        </div>
      </section>
    </>
  );
}
