import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BrandLogo from "./icons/BrandLogo";

const navLinks = [
  { to: "/services", label: "Services" },
  { to: "/staff", label: "Stylists" },
  { to: "/reviews", label: "Reviews" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setOpen(false);
    navigate("/");
  };

  const initials = user?.username?.slice(0, 2).toUpperCase() ?? "";
  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-30 border-b border-champagne/20 bg-cream/90 backdrop-blur-md" role="banner">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8" aria-label="Main navigation">
        <Link
          to="/"
          className="flex items-center gap-2.5 font-display text-xl font-bold text-charcoal"
          aria-label="BloomFlow AI home"
        >
          <BrandLogo size={32} />
          <span className="hidden sm:inline">BloomFlow</span>
        </Link>

        <div className="hidden items-center gap-8 text-sm font-medium text-charcoal-light md:flex" role="menubar">
          {navLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`transition-colors hover:text-coral-dark ${isActive(l.to) ? "text-coral-dark font-semibold" : ""}`}
              role="menuitem"
              aria-current={isActive(l.to) ? "page" : undefined}
            >
              {l.label}
            </Link>
          ))}
          {user && (
            <>
              {user.role === "customer" && (
                <Link
                  to="/book"
                  className={`transition-colors hover:text-coral-dark ${isActive("/book") ? "text-coral-dark font-semibold" : ""}`}
                  role="menuitem"
                  aria-current={isActive("/book") ? "page" : undefined}
                >
                  Book Now
                </Link>
              )}
              <Link
                to="/my-bookings"
                className={`transition-colors hover:text-coral-dark ${isActive("/my-bookings") ? "text-coral-dark font-semibold" : ""}`}
                role="menuitem"
                aria-current={isActive("/my-bookings") ? "page" : undefined}
              >
                My Bookings
              </Link>
              {user.role === "customer" && (
                <>
                  <Link to="/loyalty" className={`transition-colors hover:text-coral-dark ${isActive("/loyalty") ? "text-coral-dark font-semibold" : ""}`} role="menuitem">Rewards</Link>
                  <Link to="/profile" className={`transition-colors hover:text-coral-dark ${isActive("/profile") ? "text-coral-dark font-semibold" : ""}`} role="menuitem">Profile</Link>
                </>
              )}
              {user.role === "admin" && (
                <Link
                  to="/admin"
                  className={`transition-colors hover:text-coral-dark ${location.pathname.startsWith("/admin") ? "text-coral-dark font-semibold" : ""}`}
                  role="menuitem"
                  aria-current={location.pathname.startsWith("/admin") ? "page" : undefined}
                >
                  Admin
                </Link>
              )}
            </>
          )}
        </div>

        <div className="hidden items-center gap-4 md:flex">
          {user ? (
            <>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-rosegold-gradient text-xs font-semibold text-white" aria-label={`Logged in as ${user.username}`}>
                {initials}
              </span>
              <button
                onClick={handleLogout}
                className="rounded-full border border-charcoal/20 px-4 py-1.5 text-sm font-medium text-charcoal transition-colors hover:border-coral hover:text-coral-dark"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-charcoal-light hover:text-coral-dark transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="rounded-full bg-rosegold-gradient px-6 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:scale-[1.02] active:scale-[0.98]"
              >
                Book Appointment
              </Link>
            </>
          )}
        </div>

        <button
          className="flex h-9 w-9 items-center justify-center rounded-md text-charcoal md:hidden"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          <span className="sr-only">Menu</span>
          <div className="space-y-1.5" aria-hidden="true">
            <span className="block h-0.5 w-5 bg-charcoal" />
            <span className="block h-0.5 w-5 bg-charcoal" />
            <span className="block h-0.5 w-5 bg-charcoal" />
          </div>
        </button>
      </nav>

      {open && (
        <div className="border-t border-champagne/20 bg-cream px-4 py-4 md:hidden" role="menu">
          <div className="flex flex-col gap-3 text-sm font-medium text-charcoal">
            {navLinks.map((l) => (
              <Link key={l.to} to={l.to} onClick={() => setOpen(false)} role="menuitem" aria-current={isActive(l.to) ? "page" : undefined}>
                {l.label}
              </Link>
            ))}
            {user ? (
              <>
                {user.role === "customer" && (
                  <Link to="/book" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/book") ? "page" : undefined}>
                    Book Now
                  </Link>
                )}
                <Link to="/my-bookings" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/my-bookings") ? "page" : undefined}>
                  My Bookings
                </Link>
                {user.role === "customer" && (
                  <>
                    <Link to="/loyalty" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/loyalty") ? "page" : undefined}>Rewards</Link>
                    <Link to="/notifications" onClick={() => setOpen(false)} role="menuitem">Notifications</Link>
                    <Link to="/profile" onClick={() => setOpen(false)} role="menuitem">Profile</Link>
                    <Link to="/support" onClick={() => setOpen(false)} role="menuitem">Support</Link>
                  </>
                )}
                {user.role === "admin" && (
                  <Link to="/admin" onClick={() => setOpen(false)} role="menuitem" aria-current={location.pathname.startsWith("/admin") ? "page" : undefined}>
                    Admin
                  </Link>
                )}
                <button onClick={handleLogout} className="text-left text-rose-600" role="menuitem">
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setOpen(false)} role="menuitem">
                  Sign in
                </Link>
                <Link
                  to="/register"
                  onClick={() => setOpen(false)}
                  className="rounded-full bg-rosegold-gradient px-6 py-2.5 text-center font-semibold text-white"
                  role="menuitem"
                >
                  Book Appointment
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
