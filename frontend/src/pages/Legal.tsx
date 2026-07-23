import { useLocation } from "react-router-dom";
import PageHero from "../components/ui/PageHero";

export default function Legal() {
  const privacy = useLocation().pathname === "/privacy";
  return (
    <>
      <PageHero
        eyebrow="Salon information"
        title={privacy ? "Privacy policy" : "Terms of service"}
        description={privacy ? "A clear overview of how account and appointment information is handled." : "The practical terms that help appointments run smoothly for every guest."}
      />
      <article className="prose mx-auto max-w-3xl px-4 py-14 text-secondary sm:px-6 lg:py-20">
        <div className="beauty-card space-y-7 p-7 sm:p-10">
          <section><h2 className="text-2xl text-heading">{privacy ? "Information we use" : "Appointments"}</h2><p className="mt-2 leading-7">{privacy ? "We use the account and booking details you provide to schedule services, communicate appointment updates, support your account, and maintain salon records." : "Appointment availability is confirmed only after a booking is successfully created. Please arrive on time and contact the salon as early as possible if your plans change."}</p></section>
          <section><h2 className="text-2xl text-heading">{privacy ? "Your choices" : "Changes and cancellations"}</h2><p className="mt-2 leading-7">{privacy ? "You can update your contact information from your profile and choose reminder preferences from the notifications page." : "Cancellation and rescheduling options shown in your account follow the current salon booking rules and appointment status."}</p></section>
          <section><h2 className="text-2xl text-heading">Questions</h2><p className="mt-2 leading-7">For account, accessibility, or appointment questions, use the support page or contact hello@bloomflow.ai.</p></section>
        </div>
      </article>
    </>
  );
}
