import { useEffect, useMemo, useState } from "react";
import { reviewsApi, type Review } from "../api/client";
import PageHero from "../components/ui/PageHero";
import avatar1 from "../assets/landing/avatar-1.webp";
import avatar2 from "../assets/landing/avatar-2.webp";
import avatar3 from "../assets/landing/avatar-3.webp";

const avatars = [avatar1, avatar2, avatar3];

export default function Reviews() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    reviewsApi.list()
      .then((res) => setReviews(res.data.results))
      .catch(() => setError("Client stories are taking a little longer to arrive."))
      .finally(() => setLoading(false));
  }, []);

  const average = useMemo(
    () => reviews.length ? reviews.reduce((total, review) => total + review.rating, 0) / reviews.length : 0,
    [reviews],
  );
  const distribution = [5, 4, 3, 2, 1].map((rating) => ({
    rating,
    count: reviews.filter((review) => review.rating === rating).length,
  }));

  return (
    <>
      <PageHero
        eyebrow="Client love"
        title="Real stories, radiant results."
        description="Thoughtful feedback from guests who trust our team with the rituals that help them feel their best."
      />
      <section className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
        <div className="grid gap-8 lg:grid-cols-[340px_1fr]">
          <aside className="beauty-card h-fit p-7">
            <p className="beauty-eyebrow">Average rating</p>
            <div className="mt-3 font-display text-6xl text-heading">{average ? average.toFixed(1) : "—"}</div>
            <div className="mt-2 text-2xl tracking-widest text-gold" aria-label={`${average.toFixed(1)} out of 5 stars`}>★★★★★</div>
            <p className="mt-2 text-sm text-secondary">Based on {reviews.length} verified appointments</p>
            <div className="mt-7 space-y-3">
              {distribution.map(({ rating, count }) => (
                <div key={rating} className="grid grid-cols-[28px_1fr_24px] items-center gap-3 text-xs text-muted">
                  <span>{rating}★</span>
                  <div className="h-2 overflow-hidden rounded-full bg-blush">
                    <div className="h-full rounded-full bg-gold" style={{ width: `${reviews.length ? (count / reviews.length) * 100 : 0}%` }} />
                  </div>
                  <span>{count}</span>
                </div>
              ))}
            </div>
          </aside>
          <div>
            {loading && <div className="grid gap-5 sm:grid-cols-2" aria-busy="true">{[1, 2, 3, 4].map((n) => <div key={n} className="beauty-skeleton h-56 rounded-[26px]" />)}</div>}
            {error && <div role="alert" className="beauty-card p-8 text-center text-error">{error}</div>}
            {!loading && !error && !reviews.length && (
              <div className="beauty-card p-10 text-center">
                <span className="text-5xl text-gold" aria-hidden="true">☆</span>
                <h2 className="mt-4 text-2xl text-heading">The first review is waiting to be written.</h2>
                <p className="mt-2 text-secondary">Completed guests can share feedback from My Bookings.</p>
              </div>
            )}
            <div className="grid gap-5 sm:grid-cols-2">
              {reviews.map((review, index) => (
                <article key={review.id} className="beauty-card p-6">
                  <div className="flex items-center gap-3">
                    <img src={avatars[index % avatars.length]} alt="" width="200" height="200" className="h-11 w-11 rounded-full object-cover" />
                    <div>
                      <h2 className="font-sans text-sm font-bold text-heading">{review.customer_name}</h2>
                      <p className="text-xs text-muted">{new Date(review.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="mt-5 tracking-widest text-gold" aria-label={`${review.rating} out of 5 stars`}>
                    {"★".repeat(review.rating)}<span className="text-blush">{"★".repeat(5 - review.rating)}</span>
                  </div>
                  <p className="mt-4 leading-7 text-secondary">{review.comment || "A wonderful experience from beginning to end."}</p>
                  <p className="mt-5 border-t border-rose/10 pt-4 text-xs font-semibold uppercase tracking-wider text-coral">{review.service_name} · {review.staff_name}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
