import { Link } from "react-router-dom";
import BrandLogo from "../icons/BrandLogo";

export default function LandingFooter() {
  return (
    <footer className="bg-main px-4 pb-5 pt-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1240px] rounded-t-[34px] bg-gradient-to-br from-[#bd6c68] to-[#a85652] px-6 py-10 text-white shadow-soft sm:px-10">
        <div className="grid gap-9 sm:grid-cols-2 lg:grid-cols-[1.35fr_.8fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2"><BrandLogo size={28} /><span className="font-display text-xl">Beauty Studio</span></div>
            <p className="mt-3 max-w-xs text-sm leading-6 text-white/75">Beauty that feels personal. Confidence that lasts.</p>
            <form className="mt-5 flex max-w-sm overflow-hidden rounded-full bg-white" onSubmit={(event) => event.preventDefault()}>
              <label htmlFor="landing-newsletter" className="sr-only">Email address</label>
              <input id="landing-newsletter" type="email" placeholder="Enter your email…" className="min-w-0 flex-1 px-4 py-2.5 text-sm text-heading outline-none" />
              <button type="submit" className="px-4 text-coral" aria-label="Join newsletter">→</button>
            </form>
          </div>
          <div>
            <h2 className="font-sans text-xs font-bold uppercase tracking-[.18em] text-white/60">Quick links</h2>
            <div className="mt-4 grid gap-2 text-sm text-white/80"><a href="#home">Home</a><a href="#services">Services</a><a href="#about">About us</a><a href="#services">Prices</a></div>
          </div>
          <div>
            <h2 className="font-sans text-xs font-bold uppercase tracking-[.18em] text-white/60">Contact us</h2>
            <div className="mt-4 space-y-2 text-sm text-white/80"><p>+1 234 567 8900</p><p>hello@beautystudio.com</p></div>
          </div>
          <div>
            <h2 className="font-sans text-xs font-bold uppercase tracking-[.18em] text-white/60">Our address</h2>
            <p className="mt-4 text-sm leading-6 text-white/80">123 Beauty Lane<br />Glam City, CA 90210</p>
          </div>
        </div>
        <div className="mt-9 flex flex-col gap-3 border-t border-white/15 pt-5 text-xs text-white/55 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} Beauty Studio. All rights reserved.</p>
          <div className="flex gap-5"><Link to="/privacy">Privacy policy</Link><Link to="/terms">Terms of service</Link></div>
        </div>
      </div>
    </footer>
  );
}
