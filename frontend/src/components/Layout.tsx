import { Outlet } from "react-router-dom";
import { useLocation } from "react-router-dom";
import Footer from "./Footer";
import Navbar from "./Navbar";
import SupportWidget from "./SupportWidget";
import CustomerDock from "./CustomerDock";
import LandingHeader from "./landing/LandingHeader";
import LandingFooter from "./landing/LandingFooter";

export default function Layout() {
  const landing = useLocation().pathname === "/";
  return (
    <div className="flex min-h-screen flex-col pb-20 md:pb-0">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <svg width="0" height="0" className="absolute" aria-hidden="true">
        <defs>
          <linearGradient id="icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E8A798" />
            <stop offset="50%" stopColor="#C97B6E" />
            <stop offset="100%" stopColor="#A8574B" />
          </linearGradient>
        </defs>
      </svg>
      {landing ? <LandingHeader /> : <Navbar />}
      <main id="main-content" className="flex-1" tabIndex={-1}>
        <Outlet />
      </main>
      {landing ? <LandingFooter /> : <Footer />}
      <SupportWidget />
      <CustomerDock />
    </div>
  );
}
