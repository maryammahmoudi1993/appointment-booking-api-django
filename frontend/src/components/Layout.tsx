import { Outlet } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Footer from "./Footer";
import Navbar from "./Navbar";
import ChatWidget from "./ChatWidget";
import CustomerDock from "./CustomerDock";
import LandingHeader from "./landing/LandingHeader";
import LandingFooter from "./landing/LandingFooter";
import PortfolioDemoBar from "./landing/PortfolioDemoBar";

export default function Layout() {
  const { user } = useAuth();
  // The marketing landing header/footer only make sense for a logged-out
  // visitor. Once signed in, the landing page should behave like every
  // other page — otherwise a logged-in customer visiting "/" loses access
  // to My Bookings/Rewards/Profile until they navigate elsewhere first.
  const landing = useLocation().pathname === "/" && !user;
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
      {landing && <PortfolioDemoBar />}
      {/* LandingHeader floats absolutely over the Hero's background, so it
          needs its own positioned ancestor here — otherwise its `top: 0`
          anchors to the page's absolute top and overlaps whatever renders
          above it (the demo bar), instead of the Hero underneath it. */}
      <div className="relative flex flex-1 flex-col">
        {landing ? <LandingHeader /> : <Navbar />}
        <main id="main-content" className="flex-1" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
      {landing ? <LandingFooter /> : <Footer />}
      <ChatWidget />
      <CustomerDock />
    </div>
  );
}
