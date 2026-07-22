import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { appointmentsApi, reviewsApi, type Appointment } from "../api/client";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-champagne/15 text-coral-dark",
  confirmed: "bg-brand-100 text-brand-800",
  completed: "bg-blush text-charcoal",
  cancelled: "bg-rose-100 text-rose-800",
};

const POLL_INTERVAL_MS = 20000;

export default function MyBookings() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  const fetchBookings = (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    appointmentsApi
      .list()
      .then((res) => setAppointments(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBookings();
    const interval = setInterval(() => fetchBookings(false), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
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
        <div className="mt-8 rounded-2xl border border-dashed border-brand-200 bg-brand-50/40 p-10 text-center text-charcoal-light">
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
                  <p className="mt-1 text-sm text-charcoal-light">
                    with {a.staff_name}
                  </p>
                  <p className="text-sm text-charcoal-light">
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
                    <p className="mt-2 text-sm text-charcoal-light">
                      Notes: {a.notes}
                    </p>
                  )}
                  {a.discount_amount && (
                    <p className="mt-2 text-xs font-medium text-brand-700">
                      Promo applied: -${a.discount_amount}
                    </p>
                  )}
                  {a.status === "completed" && a.points_earned > 0 && (
                    <p className="mt-2 text-xs font-medium text-brand-700">
                      +{a.points_earned} loyalty pts earned
                    </p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
                      STATUS_COLORS[a.status] || "bg-blush-light text-charcoal"
                    }`}
                  >
                    {a.status}
                  </span>
                  {a.status === "pending" && (
                    <button
                      onClick={() => handleCancel(a.id)}
                      className="rounded-full border border-rose-200 px-3 py-1 text-xs font-medium text-rose-600 hover:bg-rose-50"
                    >
                      Cancel
                    </button>
                  )}
                  {a.status === "completed" && !a.has_review && (
                    <button
                      onClick={() => setReviewingId(a.id)}
                      className="rounded-full border border-brand-200 px-3 py-1 text-xs font-medium text-brand-700 hover:bg-brand-50"
                    >
                      Rate your visit
                    </button>
                  )}
                  {a.status === "completed" && a.has_review && (
                    <span className="text-xs text-charcoal-light/70">Reviewed ✓</span>
                  )}
                </div>
              </div>

              {reviewingId === a.id && (
                <ReviewForm
                  appointment={a}
                  onDone={() => {
                    setReviewingId(null);
                    fetchBookings(false);
                  }}
                  onCancel={() => setReviewingId(null)}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ReviewForm({
  appointment,
  onDone,
  onCancel,
}: {
  appointment: Appointment;
  onDone: () => void;
  onCancel: () => void;
}) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    setSubmitting(true);
    try {
      await reviewsApi.create({ appointment: appointment.id, rating, comment });
      onDone();
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.appointment?.[0] ||
          "Could not submit review."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mt-4 rounded-xl border border-brand-100 bg-brand-50/40 p-4">
      <p className="text-sm font-medium text-charcoal">
        Rate your visit for {appointment.service_name} with {appointment.staff_name}
      </p>
      <div className="mt-2 flex gap-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => setRating(n)}
            className={`text-2xl leading-none ${
              n <= rating ? "text-coral-dark" : "text-charcoal-light/50"
            }`}
            aria-label={`${n} star`}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Optional comment"
        rows={2}
        className="mt-3 block w-full rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      />
      {error && <p className="mt-2 text-xs text-rose-700">{error}</p>}
      <div className="mt-3 flex gap-2">
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "Submit review"}
        </button>
        <button
          onClick={onCancel}
          className="rounded-full border border-champagne/30 px-4 py-1.5 text-xs font-medium text-charcoal-light hover:bg-cream"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
