import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { staffApi, type StaffProfile } from "../api/client";

export default function Staff() {
  const [staff, setStaff] = useState<StaffProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    staffApi
      .list()
      .then((res) => setStaff(res.data.results))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 lg:px-8">
      <div className="text-center">
        <h2 className="font-display text-3xl font-bold text-brand-900">
          Meet the Team
        </h2>
        <p className="mt-2 text-gray-600">
          Experienced specialists, ready to help you look and feel your best.
        </p>
      </div>
      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        {staff.map((s) => (
          <div
            key={s.id}
            className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm transition hover:shadow-md"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-100 font-display text-sm font-bold text-brand-700">
                {s.user_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase()}
              </span>
              <h3 className="font-display text-lg font-semibold text-brand-900">
                {s.user_name}
              </h3>
            </div>
            <p className="mt-3 text-sm text-gray-600">{s.bio}</p>
            {s.specialties.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {s.specialties.map((sp) => (
                  <span
                    key={sp}
                    className="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700"
                  >
                    {sp}
                  </span>
                ))}
              </div>
            )}
            <Link
              to="/book"
              className="mt-5 inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
            >
              Book
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
