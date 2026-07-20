import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { appointmentsApi, type Appointment } from "../api/client";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-amber-100 text-amber-800",
  confirmed: "bg-brand-100 text-brand-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

export default function MyBookings() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBookings = () => {
    setLoading(true);
    appointmentsApi
      .list()
      .then((res) => setAppointments(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleCancel = async (id: number) => {
    try {
      await appointmentsApi.cancel(id);
      fetchBookings();
    } catch {
      alert("Failed to cancel appointment.");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-2xl font-bold text-brand-900">
          My Bookings
        </h2>
        <Link
          to="/book"
          className="rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
        >
          Book another
        </Link>
      </div>

      {appointments.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-dashed border-brand-200 bg-brand-50/40 p-10 text-center text-gray-500">
          You don&apos;t have any bookings yet.
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {appointments.map((a) => (
            <div
              key={a.id}
              className="rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-display font-semibold text-brand-900">
                    {a.service_name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-600">
                    with {a.staff_name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(a.start_datetime).toLocaleDateString("en-US", {
                      weekday: "long",
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}{" "}
                    &middot;{" "}
                    {new Date(a.start_datetime).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}{" "}
                    -{" "}
                    {new Date(a.end_datetime).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  {a.notes && (
                    <p className="mt-2 text-sm text-gray-500">
                      Notes: {a.notes}
                    </p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
                      STATUS_COLORS[a.status] || "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {a.status}
                  </span>
                  {a.status === "pending" && (
                    <button
                      onClick={() => handleCancel(a.id)}
                      className="rounded-full border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
