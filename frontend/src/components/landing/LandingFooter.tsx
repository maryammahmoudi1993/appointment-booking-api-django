import { Link } from "react-router-dom";
import BrandLogo from "../icons/BrandLogo";

export default function LandingFooter() {
  return (
    <footer className="bg-main px-4 pb-5 pt-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1240px] rounded-t-[34px] bg-gradient-to-br from-[#bd6c68] to-[#a85652] px-6 py-10 text-white shadow-soft sm:px-10">
        <div className="grid gap-9 sm:grid-cols-2 lg:grid-cols-[1.35fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2"><BrandLogo size={28} /><span className="font-display text-xl">BloomFlow</span></div>
            <p className="mt-3 max-w-xs text-sm leading-6 text-white/75">Beauty that feels personal. Confidence that lasts.</p>
          </div>
          <div>
            <h2 className="font-sans text-xs font-bold uppercase tracking-[.18em] text-white/60">Quick links</h2>
            <div className="mt-4 grid gap-2 text-sm text-white/80"><a href="#home">Home</a><a href="#services">Services</a><a href="#about">About us</a><a href="#services">Prices</a></div>
          </div>
          <div>
            <h2 className="font-sans text-xs font-bold uppercase tracking-[.18em] text-white/60">For customers</h2>
            <div className="mt-4 grid gap-2 text-sm text-white/80"><Link to="/book">Book an appointment</Link><Link to="/staff">Meet the stylists</Link><Link to="/support">Contact support</Link></div>
          </div>
        </div>
        <div className="mt-9 flex flex-col gap-3 border-t border-white/15 pt-5 text-xs text-white/55 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} BloomFlow. All rights reserved.</p>
          <div className="flex gap-5"><Link to="/privacy">Privacy policy</Link><Link to="/terms">Terms of service</Link></div>
        </div>
      </div>
    </footer>
  );
}
