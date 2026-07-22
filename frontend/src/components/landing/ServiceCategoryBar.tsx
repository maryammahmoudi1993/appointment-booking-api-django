import { Link } from "react-router-dom";
import GradientIcon from "../icons/GradientIcon";
import {
  CalendarIcon,
  ScissorsIcon,
  SparklesIcon,
  HandIcon,
  FaceIcon,
  LotusIcon,
  FlameIcon,
  UsersIcon,
} from "../icons/ServiceIcons";

const categories = [
  { label: "Book Online", icon: CalendarIcon, to: "/book" },
  { label: "Hair Styling", icon: ScissorsIcon, to: "/services" },
  { label: "Facial Care", icon: SparklesIcon, to: "/services" },
  { label: "Nail & Polish", icon: HandIcon, to: "/services" },
  { label: "Makeup", icon: FaceIcon, to: "/services" },
  { label: "Skin Care", icon: FlameIcon, to: "/services" },
  { label: "Spa & Relax", icon: LotusIcon, to: "/services" },
  { label: "Our Team", icon: UsersIcon, to: "/staff" },
];

export default function ServiceCategoryBar() {
  return (
    <section
      aria-label="Service categories"
      className="relative z-10 mx-auto -mt-10 max-w-6xl px-4 sm:px-6 lg:px-8"
    >
      <div className="flex gap-4 overflow-x-auto rounded-3xl border border-champagne/20 bg-white/90 p-5 shadow-[0_20px_45px_-20px_rgba(184,134,11,0.35)] backdrop-blur-sm sm:gap-6 sm:overflow-visible">
        {categories.map((cat) => (
          <Link
            key={cat.label}
            to={cat.to}
            className="group flex shrink-0 flex-col items-center gap-2 text-center"
          >
            <GradientIcon size="sm" className="transition-transform group-hover:-translate-y-0.5">
              <cat.icon />
            </GradientIcon>
            <span className="whitespace-nowrap text-xs font-medium text-charcoal-light group-hover:text-coral-dark">
              {cat.label}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
