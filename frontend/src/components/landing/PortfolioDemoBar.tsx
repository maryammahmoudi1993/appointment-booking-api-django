import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

// Seeded by core/management/commands/seed_demo_data.py — safe to expose
// since these accounts only ever exist on the demo deployment.
const DEMO_CUSTOMER = { username: "emma.johnson", password: "customer123" };
const DEMO_ADMIN = { username: "admin", password: "admin123" };

export default function PortfolioDemoBar() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [pending, setPending] = useState<"customer" | "admin" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const enterAs = async (role: "customer" | "admin") => {
    setError(null);
    setPending(role);
    const creds = role === "customer" ? DEMO_CUSTOMER : DEMO_ADMIN;
    try {
      await login(creds.username, creds.password);
      navigate(role === "customer" ? "/book" : "/admin");
    } catch {
      setError("The demo backend is still waking up — please try again in a few seconds.");
    } finally {
      setPending(null);
    }
  };

  return (
    <div className="border-b border-rose/15 bg-rose-deep/95 px-4 py-4 text-center text-white sm:px-6 lg:px-8" role="region" aria-label="Portfolio demo access">
      <p className="text-xs font-bold uppercase tracking-[.14em] text-white/70">
        Portfolio Demo — Full-Stack AI SaaS Case Study
      </p>
      <div className="mt-3 flex flex-wrap items-center justify-center gap-3">
        <button
          type="button"
          onClick={() => enterAs("customer")}
          disabled={pending !== null}
          className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-rose-deep transition hover:bg-white/90 disabled:opacity-60"
        >
          {pending === "customer" ? "Preparing demo…" : "Explore Customer Demo"}
        </button>
        <button
          type="button"
          onClick={() => enterAs("admin")}
          disabled={pending !== null}
          className="rounded-full border border-white/50 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10 disabled:opacity-60"
        >
          {pending === "admin" ? "Preparing demo…" : "Open Admin Dashboard"}
        </button>
        <Link
          to="/case-study"
          className="rounded-full border border-white/50 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
        >
          View Case Study
        </Link>
      </div>
      {error ? (
        <p className="mt-2 text-xs text-white/80" role="alert">{error}</p>
      ) : (
        <p className="mt-2 text-xs text-white/60">No signup required • Preloaded demonstration data</p>
      )}
    </div>
  );
}
