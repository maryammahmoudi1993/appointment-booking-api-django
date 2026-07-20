import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const steps = [
  {
    title: "Browse services",
    desc: "View every service we offer with pricing and duration up front.",
  },
  {
    title: "Choose your specialist",
    desc: "Pick from our team based on availability and expertise, or let us match you.",
  },
  {
    title: "Instant confirmation",
    desc: "Get your booking confirmed in real time — no double-booking, no phone tag.",
  },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <div>
      <div className="bg-gradient-to-b from-brand-50 to-white">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-700">
              Appointment booking, simplified
            </span>
            <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-brand-900 sm:text-5xl">
              Book your appointment in minutes
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-lg text-gray-600">
              Browse our services, pick a time that works for you, and secure
              your booking instantly — no phone calls, no back-and-forth.
            </p>
            <div className="mt-8 flex items-center justify-center gap-4">
              {user ? (
                <Link
                  to="/book"
                  className="rounded-full bg-brand-600 px-7 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
                >
                  Book Now
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="rounded-full bg-brand-600 px-7 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="rounded-full border border-brand-200 bg-white px-7 py-3 text-sm font-semibold text-brand-800 transition hover:border-brand-300"
                  >
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 pb-20 pt-4 sm:px-6 lg:px-8">
        <div className="grid gap-6 sm:grid-cols-3">
          {steps.map((item, i) => (
            <div
              key={item.title}
              className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-600 font-display text-sm font-bold text-white">
                {i + 1}
              </span>
              <h3 className="mt-4 font-display text-lg font-semibold text-brand-900">
                {item.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-600">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
