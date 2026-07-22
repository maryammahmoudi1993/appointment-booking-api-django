import { Outlet } from "react-router-dom";
import ChatWidget from "./ChatWidget";
import Footer from "./Footer";
import Navbar from "./Navbar";
import SupportWidget from "./SupportWidget";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
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
