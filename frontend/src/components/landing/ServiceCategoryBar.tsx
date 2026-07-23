import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import iconBookOnline from "../../assets/landing/icon-book-online-clean.webp";
import iconHairStyling from "../../assets/landing/icon-hair-styling-clean.webp";
import iconFacialCare from "../../assets/landing/icon-facial-care-clean.webp";
import iconNailPolish from "../../assets/landing/icon-nail-polish-clean.webp";
import iconMakeup from "../../assets/landing/icon-makeup-clean.webp";
import iconSkinCare from "../../assets/landing/icon-skin-care-clean.webp";
import iconSpaRelax from "../../assets/landing/icon-spa-relax-clean.webp";
import iconAllServices from "../../assets/landing/icon-all-services-clean.webp";

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
  const { user } = useAuth();
  return (
    <section
      aria-label="Service categories"
      className="relative z-20 mx-auto -mt-16 max-w-[1240px] px-4 sm:px-6 lg:px-8"
    >
      <div className="flex gap-3 overflow-x-auto rounded-[30px] border border-rose/20 bg-surface/95 p-4 shadow-[0_18px_48px_rgba(124,75,62,.14)] scroll-smooth snap-x snap-mandatory sm:gap-4 lg:justify-between lg:overflow-visible lg:p-5">
        {categories.map((cat) => (
          <Link
            key={cat.label}
            to={cat.label === "Book Online" && !user ? "/register" : cat.to}
            className="group flex w-[92px] shrink-0 snap-start flex-col items-center gap-2 text-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 rounded-xl"
          >
            <span className="flex h-[68px] w-[68px] items-center justify-center overflow-hidden rounded-[19px] border border-rose/15 bg-[#fbe7e1] shadow-[0_8px_18px_-6px_rgba(168,87,75,0.35)] transition-transform duration-300 group-hover:-translate-y-1">
              <img src={cat.icon} alt="" width={384} height={384} className="h-full w-full object-cover" />
            </span>
            <span className="whitespace-nowrap text-[11px] font-semibold text-secondary group-hover:text-coral">
              {cat.label}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
