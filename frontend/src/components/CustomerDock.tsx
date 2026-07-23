import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const items = [
  { to: "/", label: "Home", glyph: "⌂" },
  { to: "/my-bookings", label: "Bookings", glyph: "▦" },
  { to: "/notifications", label: "Inbox", glyph: "♢" },
  { to: "/loyalty", label: "Rewards", glyph: "☆" },
  { to: "/profile", label: "Profile", glyph: "○" },
];

export default function CustomerDock() {
  const { user } = useAuth();
  const location = useLocation();
  if (!user || user.role !== "customer") return null;

  return (
    <nav
      aria-label="Customer navigation"
      className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-5 rounded-[24px] border border-rose/15 bg-surface/95 p-2 shadow-raised backdrop-blur md:hidden"
    >
      {items.map((item) => {
        const active = location.pathname === item.to;
        return (
          <Link
            key={item.to}
            to={item.to}
            aria-current={active ? "page" : undefined}
            className={`flex min-h-12 flex-col items-center justify-center rounded-2xl text-[10px] font-semibold transition ${
              active ? "bg-blush text-coral" : "text-muted"
            }`}
          >
            <span className="text-lg leading-none" aria-hidden="true">{item.glyph}</span>
            <span className="mt-1">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
