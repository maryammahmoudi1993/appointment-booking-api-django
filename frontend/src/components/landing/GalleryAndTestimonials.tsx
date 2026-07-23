import { useEffect, useState } from "react";
import { reviewsApi, type Review } from "../../api/client";
import SectionHeading from "../ui/SectionHeading";
import decorativeFlower from "../../assets/landing/decorative-flower-clean.png";
import botanicalBranch from "../../assets/landing/botanical-branch-clean.png";
import avatar1 from "../../assets/landing/avatar-1.webp";
import avatar2 from "../../assets/landing/avatar-2.webp";
import avatar3 from "../../assets/landing/avatar-3.webp";

const avatars = [avatar1, avatar2, avatar3];
const fallback = [
  { name: "Aisha K.", content: "The best salon experience! Super friendly staff and amazing results.", rating: 5 },
  { name: "Sophia M.", content: "Professional, hygienic, and highly recommended.", rating: 5 },
  { name: "Priya T.", content: "I always leave feeling beautiful and confident.", rating: 5 },
];

export default function GalleryAndTestimonials() {
  const [reviews, setReviews] = useState<Review[]>([]);

  useEffect(() => {
    reviewsApi.list().then((res) => setReviews(res.data.results.slice(0, 3))).catch(() => {});
  }, []);

  const items = reviews.length
    ? reviews.map((review) => ({ name: review.customer_name || "Verified client", content: review.comment, rating: review.rating }))
    : fallback;

  return (
    <section id="reviews" className="relative scroll-mt-8 bg-main py-16 sm:py-20" aria-labelledby="testimonials-heading">
      <img src={botanicalBranch} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -left-24 bottom-0 hidden w-64 -rotate-12 opacity-70 lg:block" />
      <img src={decorativeFlower} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -right-24 top-0 hidden w-64 rotate-12 opacity-75 lg:block" />
      <div className="relative mx-auto max-w-[1060px] px-4 sm:px-6 lg:px-8">
        <SectionHeading eyebrow="What Our Clients Say" id="testimonials-heading" title="Loved by our clients" />
        <div className="mt-9 grid gap-5 md:grid-cols-3">
          {items.map((item, index) => (
            <article key={`${item.name}-${index}`} className="beauty-card flex min-h-[205px] flex-col p-6">
              <div className="tracking-[.14em] text-[#e6a54a]" aria-label={`${item.rating} out of 5 stars`}>{"★".repeat(item.rating)}</div>
              <p className="mt-4 line-clamp-3 flex-1 text-sm leading-6 text-secondary">“{item.content || "A wonderful salon experience from start to finish."}”</p>
              <div className="mt-5 flex items-center gap-3">
                <img src={avatars[index % avatars.length]} alt="" width="200" height="200" loading="lazy" className="h-9 w-9 rounded-full object-cover" />
                <p className="text-xs font-bold text-heading">— {item.name}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
