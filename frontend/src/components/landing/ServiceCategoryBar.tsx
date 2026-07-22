import { Link } from "react-router-dom";
import iconBookOnline from "../../assets/landing/icon-book-online.webp";
import iconHairStyling from "../../assets/landing/icon-hair-styling.webp";
import iconFacialCare from "../../assets/landing/icon-facial-care.webp";
import iconNailPolish from "../../assets/landing/icon-nail-polish.webp";
import iconMakeup from "../../assets/landing/icon-makeup.webp";
import iconSkinCare from "../../assets/landing/icon-skin-care.webp";
import iconSpaRelax from "../../assets/landing/icon-spa-relax.webp";
import iconAllServices from "../../assets/landing/feature-products.webp";

const categories = [
  { label: "Book Online", icon: iconBookOnline, to: "/book" },
  { label: "Hair Styling", icon: iconHairStyling, to: "/services" },
  { label: "Facial Care", icon: iconFacialCare, to: "/services" },
  { label: "Nail & Polish", icon: iconNailPolish, to: "/services" },
  { label: "Makeup", icon: iconMakeup, to: "/services" },
  { label: "Skin Care", icon: iconSkinCare, to: "/services" },
  { label: "Spa & Relax", icon: iconSpaRelax, to: "/services" },
  { label: "All Services", icon: iconAllServices, to: "/services" },
];

export default function ServiceCategoryBar() {
  return (
    <section
      aria-label="Service categories"
      className="relative z-10 mx-auto -mt-10 max-w-6xl px-4 sm:px-6 lg:px-8"
    >
      <div className="flex gap-4 overflow-x-auto rounded-3xl border border-champagne/20 bg-white/90 p-5 shadow-[0_20px_45px_-20px_rgba(184,134,11,0.35)] backdrop-blur-sm scroll-smooth snap-x snap-mandatory sm:gap-6 sm:overflow-visible sm:snap-none">
        {categories.map((cat) => (
          <Link
            key={cat.label}
            to={cat.to}
            className="group flex shrink-0 snap-start flex-col items-center gap-2 text-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 rounded-xl"
          >
            <span className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-2xl shadow-[0_8px_18px_-6px_rgba(168,87,75,0.35)] transition-transform group-hover:-translate-y-1">
              <img src={cat.icon} alt="" width={56} height={56} className="h-full w-full object-cover" />
            </span>
            <span className="whitespace-nowrap text-xs font-medium text-charcoal-light group-hover:text-coral-dark">
              {cat.label}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
