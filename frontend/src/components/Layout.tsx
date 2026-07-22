import { Outlet } from "react-router-dom";
import ChatWidget from "./ChatWidget";
import Footer from "./Footer";
import Navbar from "./Navbar";
import SupportWidget from "./SupportWidget";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <svg width="0" height="0" className="absolute" aria-hidden="true">
        <defs>
          <linearGradient id="icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E8A798" />
            <stop offset="50%" stopColor="#C97B6E" />
            <stop offset="100%" stopColor="#A8574B" />
          </linearGradient>
        </defs>
      </svg>
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <SupportWidget />
      <ChatWidget />
    </div>
  );
}
