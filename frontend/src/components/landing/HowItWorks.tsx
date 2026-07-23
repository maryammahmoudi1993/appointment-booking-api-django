import calendarIcon from "../../assets/landing/icon-book-online-clean.webp";
import scissorsIcon from "../../assets/landing/icon-hair-styling-clean.webp";
import lotusIcon from "../../assets/landing/icon-spa-relax-clean.webp";
import botanicalBranch from "../../assets/landing/botanical-branch-clean.png";

const steps = [
  { icon: scissorsIcon, title: "Choose a Service", description: "Select the treatment you need." },
  { icon: calendarIcon, title: "Pick Date & Time", description: "Choose your preferred time." },
  { icon: lotusIcon, title: "Confirm & Relax", description: "We’ll take care of the rest." },
];

export default function HowItWorks() {
  return (
    <section className="bg-main py-12 sm:py-16" aria-labelledby="how-it-works-heading">
      <div className="mx-auto max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <div className="relative grid min-h-[390px] overflow-hidden rounded-[34px] border border-rose/20 bg-gradient-to-r from-[#f8ded6] to-[#efb8ac] px-6 py-9 shadow-soft sm:px-10 lg:grid-cols-[1.4fr_.6fr] lg:items-center lg:px-12">
          <div className="relative z-10">
            <p className="beauty-eyebrow">How it works</p>
            <h2 id="how-it-works-heading" className="mt-2 text-[clamp(2.3rem,4vw,3.5rem)] font-medium leading-tight text-heading">Book in 3 Simple Steps</h2>
            <div className="relative mt-9 grid gap-6 sm:grid-cols-3 lg:max-w-[760px]">
              <div className="absolute left-[16%] right-[16%] top-10 hidden border-t-2 border-dotted border-coral/45 sm:block" aria-hidden="true" />
              {steps.map((step, index) => (
                <div key={step.title} className="relative text-center">
                  <img src={step.icon} alt="" width="384" height="384" loading="lazy" className="relative z-10 mx-auto h-20 w-20 rounded-[22px] border border-white/70 object-cover shadow-raised" />
                  <h3 className="mt-4 font-sans text-sm font-bold text-heading">{index + 1}. {step.title}</h3>
                  <p className="mx-auto mt-1 max-w-[170px] text-xs leading-5 text-secondary">{step.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mt-12 flex min-h-[350px] items-center justify-center lg:mt-0" aria-label="Booking summary preview">
            <div className="absolute bottom-2 h-12 w-56 rounded-[50%] bg-[#d78d82]/45 blur-sm" />
            <div className="relative z-10 w-[220px] rotate-[9deg] rounded-[34px] border-[6px] border-[#49312b] bg-[#49312b] p-1 shadow-[0_24px_45px_rgba(77,43,35,.28)]">
              <div className="rounded-[26px] bg-[#fff8f4] px-4 pb-5 pt-7">
                <p className="text-center text-[9px] font-bold uppercase tracking-[.16em] text-coral">Book Appointment</p>
                <div className="mt-5 rounded-2xl bg-surface p-4 shadow-raised">
                  <p className="font-display text-base text-heading">Haircut &amp; Style</p>
                  <p className="mt-1 text-[10px] text-muted">with Jessica</p>
                  <div className="mt-4 space-y-2 border-t border-rose/10 pt-3 text-[10px] text-secondary">
                    <p>▦ Sat, 18 May 2026</p><p>◷ 11:00 AM</p>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-xs"><span className="text-muted">Total</span><strong className="font-display text-lg text-heading">$79.00</strong></div>
                <div className="mt-4 rounded-full bg-coral py-2.5 text-center text-[10px] font-bold text-white">Confirm Booking</div>
              </div>
            </div>
            <img src={botanicalBranch} alt="" width="600" height="327" loading="lazy" className="pointer-events-none absolute -bottom-8 -right-24 w-72 rotate-[-16deg] opacity-65" />
          </div>
        </div>
      </div>
    </section>
  );
}
