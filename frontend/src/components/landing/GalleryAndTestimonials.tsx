import { useEffect, useState } from "react";
import { reviewsApi, type Review } from "../../api/client";
import SectionHeading from "../ui/SectionHeading";

const FALLBACK_TESTIMONIALS = [
  {
    name: "Sarah Mitchell",
    role: "Regular Client",
    content: "BloomFlow transformed my hair completely! The colorist understood exactly what I wanted and the result was stunning. I've never felt more confident.",
    rating: 5,
  },
  {
    name: "Emily Chen",
    role: "Bridal Client",
    content: "My bridal makeup and hair were absolutely perfect. The team made me feel like royalty on my special day. The attention to detail was incredible.",
    rating: 5,
  },
  {
    name: "Jessica Park",
    role: "Monthly Member",
    content: "The loyalty program is amazing! I've earned so many rewards and the facials have completely transformed my skin. Best investment in self-care.",
    rating: 5,
  },
];

const galleryItems = [
  { category: "Hair", color: "from-champagne/20 to-blush/30" },
  { category: "Skincare", color: "from-blush/30 to-champagne/10" },
  { category: "Nails", color: "from-champagne/15 to-blush/20" },
  { category: "Spa", color: "from-blush/20 to-champagne/15" },
  { category: "Makeup", color: "from-champagne/25 to-blush/25" },
  { category: "Wellness", color: "from-blush/25 to-champagne/20" },
];

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          className={`h-4 w-4 ${i < rating ? "text-champagne" : "text-champagne/30"}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

export default function GalleryAndTestimonials() {
  const [reviews, setReviews] = useState<Review[]>([]);

  useEffect(() => {
    reviewsApi
      .list()
      .then((res) => setReviews(res.data.results.slice(0, 3)))
      .catch(() => setReviews([]));
  }, []);

  const testimonials =
    reviews.length > 0
      ? reviews.map((r) => ({
          name: r.customer_name || "Verified Client",
          role: r.service_name,
          content: r.comment,
          rating: r.rating,
        }))
      : FALLBACK_TESTIMONIALS;

  return (
    <section className="py-20 bg-cream" aria-labelledby="gallery-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Gallery */}
        <SectionHeading eyebrow="Our Work" id="gallery-heading" title="Transformations That Inspire" />

        <div className="mt-12 columns-2 gap-4 sm:columns-3 lg:columns-3">
          {galleryItems.map((item) => (
            <div
              key={item.category}
              className={`mb-4 break-inside-avoid rounded-xl bg-gradient-to-br ${item.color} p-8 transition-all hover:shadow-md hover:scale-[1.02]`}
            >
              <div className="flex h-32 items-center justify-center">
                <span className="font-display text-lg font-semibold text-charcoal/60">
                  {item.category}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Testimonials */}
        <div className="mt-20">
          <SectionHeading eyebrow="Client Love" title="What Our Clients Say" />

          <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {testimonials.map((testimonial, i) => (
              <div
                key={`${testimonial.name}-${i}`}
                className="rounded-xl border border-champagne/20 bg-white p-8 shadow-sm transition-all hover:shadow-md"
              >
                <StarRating rating={testimonial.rating} />
                <p className="mt-4 text-sm leading-relaxed text-charcoal-light italic">
                  &ldquo;{testimonial.content}&rdquo;
                </p>
                <div className="mt-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-rosegold-gradient text-sm font-semibold text-white">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-charcoal">{testimonial.name}</p>
                    <p className="text-xs text-charcoal-light">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
