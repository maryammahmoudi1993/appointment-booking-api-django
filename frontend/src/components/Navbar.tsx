import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navLinks = [
  { to: "/services", label: "Services" },
  { to: "/staff", label: "Staff" },
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
    <header className="sticky top-0 z-30 border-b border-brand-100 bg-white/90 backdrop-blur" role="banner">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8" aria-label="Main navigation">
        <Link
          to="/"
          className="flex items-center gap-2 font-display text-xl font-bold text-brand-800"
          aria-label="BloomFlow AI home"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-600 text-sm text-white" aria-hidden="true">
            BF
          </span>
          BloomFlow AI
        </Link>

        <div className="hidden items-center gap-6 text-sm font-medium text-gray-600 md:flex" role="menubar">
          {navLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`transition hover:text-brand-700 ${isActive(l.to) ? "text-brand-700 font-semibold" : ""}`}
              role="menuitem"
              aria-current={isActive(l.to) ? "page" : undefined}
            >
              {l.label}
            </Link>
          ))}
          {user && (
            <>
              <Link
                to="/book"
                className={`transition hover:text-brand-700 ${isActive("/book") ? "text-brand-700 font-semibold" : ""}`}
                role="menuitem"
                aria-current={isActive("/book") ? "page" : undefined}
              >
                Book Now
              </Link>
              <Link
                to="/my-bookings"
                className={`transition hover:text-brand-700 ${isActive("/my-bookings") ? "text-brand-700 font-semibold" : ""}`}
                role="menuitem"
                aria-current={isActive("/my-bookings") ? "page" : undefined}
              >
                My Bookings
              </Link>
              {user.role === "customer" && (
                <Link
                  to="/loyalty"
                  className={`transition hover:text-brand-700 ${isActive("/loyalty") ? "text-brand-700 font-semibold" : ""}`}
                  role="menuitem"
                  aria-current={isActive("/loyalty") ? "page" : undefined}
                >
                  Loyalty
                </Link>
              )}
              {user.role === "admin" && (
                <Link
                  to="/admin"
                  className={`transition hover:text-brand-700 ${location.pathname.startsWith("/admin") ? "text-brand-700 font-semibold" : ""}`}
                  role="menuitem"
                  aria-current={location.pathname.startsWith("/admin") ? "page" : undefined}
                >
                  Admin
                </Link>
              )}
            </>
          )}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700" aria-label={`Logged in as ${user.username}`}>
                {initials}
              </span>
              <button
                onClick={handleLogout}
                className="rounded-full border border-gray-200 px-4 py-1.5 text-sm font-medium text-gray-700 transition hover:border-brand-300 hover:text-brand-700"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-gray-700 hover:text-brand-700"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
              >
                Get started
              </Link>
            </>
          )}
        </div>

        <button
          className="flex h-9 w-9 items-center justify-center rounded-md text-gray-600 md:hidden"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          <span className="sr-only">Menu</span>
          <div className="space-y-1.5" aria-hidden="true">
            <span className="block h-0.5 w-5 bg-gray-700" />
            <span className="block h-0.5 w-5 bg-gray-700" />
            <span className="block h-0.5 w-5 bg-gray-700" />
          </div>
        </button>
      </nav>

      {open && (
        <div className="border-t border-brand-100 bg-white px-4 py-4 md:hidden" role="menu">
          <div className="flex flex-col gap-3 text-sm font-medium text-gray-700">
            {navLinks.map((l) => (
              <Link key={l.to} to={l.to} onClick={() => setOpen(false)} role="menuitem" aria-current={isActive(l.to) ? "page" : undefined}>
                {l.label}
              </Link>
            ))}
            {user ? (
              <>
                <Link to="/book" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/book") ? "page" : undefined}>
                  Book Now
                </Link>
                <Link to="/my-bookings" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/my-bookings") ? "page" : undefined}>
                  My Bookings
                </Link>
                {user.role === "customer" && (
                  <Link to="/loyalty" onClick={() => setOpen(false)} role="menuitem" aria-current={isActive("/loyalty") ? "page" : undefined}>
                    Loyalty
                  </Link>
                )}
                {user.role === "admin" && (
                  <Link to="/admin" onClick={() => setOpen(false)} role="menuitem" aria-current={location.pathname.startsWith("/admin") ? "page" : undefined}>
                    Admin
                  </Link>
                )}
                <button onClick={handleLogout} className="text-left text-red-600" role="menuitem">
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setOpen(false)} role="menuitem">
                  Sign in
                </Link>
                <Link to="/register" onClick={() => setOpen(false)} className="font-semibold text-brand-700" role="menuitem">
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
