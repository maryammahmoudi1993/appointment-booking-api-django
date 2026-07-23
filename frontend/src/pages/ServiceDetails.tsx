import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { servicesApi, staffApi, type Service, type StaffProfile } from "../api/client";
import { imageForService } from "../utils/serviceImage";
import PageHero from "../components/ui/PageHero";
import { ButtonLink } from "../components/ui/Button";

export default function ServiceDetails() {
  const { id } = useParams();
  const [service, setService] = useState<Service | null>(null);
  const [staff, setStaff] = useState<StaffProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const serviceId = Number(id);
    if (!Number.isFinite(serviceId)) {
      setError("This service could not be found.");
      setLoading(false);
      return;
    }
    Promise.all([servicesApi.get(serviceId), staffApi.list()])
      .then(([serviceRes, staffRes]) => {
        setService(serviceRes.data);
        setStaff(staffRes.data.results.filter((person) => person.services_offered.includes(serviceId)));
      })
      .catch(() => setError("We could not load this treatment right now. Please try again."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8" aria-busy="true">
        <div className="beauty-skeleton h-[32rem] rounded-[32px]" />
      </div>
    );
  }

  if (!service || error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <div className="beauty-card p-10">
          <span className="text-5xl" aria-hidden="true">✦</span>
          <h1 className="mt-5 text-3xl text-heading">Treatment unavailable</h1>
          <p className="mt-3 text-secondary">{error}</p>
          <ButtonLink to="/services" className="mt-7">Browse services</ButtonLink>
        </div>
      </div>
    );
  }

  const image = imageForService(service.name);
  return (
    <>
      <PageHero
        eyebrow="Treatment details"
        title={service.name}
        description="A thoughtful salon ritual tailored to help you feel polished, restored, and completely yourself."
      />
      <section className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:py-20">
        <div className="overflow-hidden rounded-[34px] border border-rose/15 bg-blush shadow-soft">
          <img src={image} alt={`${service.name} treatment`} width="700" height="700" className="h-full min-h-[360px] w-full object-cover" />
        </div>
        <div className="flex flex-col justify-center">
          <span className="w-fit rounded-full bg-blush px-4 py-2 text-sm font-semibold text-coral">
            Premium salon service
          </span>
          <h2 className="mt-5 text-4xl text-heading">Your time, beautifully considered.</h2>
          <p className="mt-5 leading-7 text-secondary">{service.description}</p>
          <dl className="mt-8 grid grid-cols-2 gap-4">
            <div className="beauty-card p-5">
              <dt className="text-xs font-bold uppercase tracking-[.18em] text-muted">Duration</dt>
              <dd className="mt-2 font-display text-2xl text-heading">{service.duration_minutes} min</dd>
            </div>
            <div className="beauty-card p-5">
              <dt className="text-xs font-bold uppercase tracking-[.18em] text-muted">Investment</dt>
              <dd className="mt-2 font-display text-2xl text-coral">${Number(service.price).toFixed(0)}</dd>
            </div>
          </dl>
          <div className="mt-7 rounded-[24px] border border-gold/15 bg-soft p-6">
            <h3 className="text-xl text-heading">What to expect</h3>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-secondary">
              <li>✓ A personal consultation before your service</li>
              <li>✓ Premium professional products selected for you</li>
              <li>✓ Thoughtful aftercare guidance before you leave</li>
            </ul>
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <ButtonLink to={`/book?service=${service.id}`} size="lg">Book this service</ButtonLink>
            <ButtonLink to="/services" variant="secondary" size="lg">All services</ButtonLink>
          </div>
        </div>
      </section>
      <section className="border-y border-rose/10 bg-soft py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="beauty-eyebrow text-center">Your specialists</p>
          <h2 className="mt-2 text-center text-3xl text-heading sm:text-4xl">Meet the team for this service</h2>
          {staff.length ? (
            <div className="mt-9 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {staff.map((person) => (
                <Link key={person.id} to={`/book?service=${service.id}&staff=${person.id}`} className="beauty-card group p-6 transition hover:-translate-y-1">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-rose text-lg font-bold text-white">
                    {(person.full_name || person.username).slice(0, 2).toUpperCase()}
                  </div>
                  <h3 className="mt-4 text-2xl text-heading">{person.full_name || person.username}</h3>
                  <p className="mt-1 text-sm text-secondary">{person.bio || "Beauty specialist"}</p>
                  <p className="mt-4 text-sm font-semibold text-gold">★ {person.average_rating ?? "New"} · {person.review_count} reviews</p>
                </Link>
              ))}
            </div>
          ) : (
            <div className="beauty-card mx-auto mt-8 max-w-xl p-8 text-center text-secondary">
              Choose this treatment in the booking flow to see the next available specialist.
            </div>
          )}
        </div>
      </section>
    </>
  );
}
