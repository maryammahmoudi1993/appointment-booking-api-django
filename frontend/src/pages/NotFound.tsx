import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-24">
      <h1 className="font-display text-6xl font-bold text-brand-200">404</h1>
      <p className="mt-4 text-lg text-gray-600">Page not found.</p>
      <Link
        to="/"
        className="mt-6 rounded-full bg-brand-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
      >
        Go Home
      </Link>
    </div>
  );
}
