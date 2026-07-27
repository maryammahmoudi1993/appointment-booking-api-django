import PageHero from "../components/ui/PageHero";

const meta = [
  { label: "Project type", value: "Self-initiated product case study" },
  { label: "Role", value: "Product design & full-stack engineering" },
  { label: "Status", value: "Live interactive demo" },
  { label: "Scope", value: "UI/UX, frontend, backend, AI, testing, and deployment" },
];

const contributions = [
  "Product strategy and feature definition",
  "Information architecture and user flows",
  "Original UI/UX and responsive design",
  "Design system and reusable components",
  "Django REST Framework architecture",
  "React and TypeScript implementation",
  "PostgreSQL schema and tenant isolation",
  "Authentication and role-based permissions",
  "Gemini AI function calling",
  "Automated testing and API documentation",
  "Docker and cloud deployment",
];

const decisions = [
  {
    title: "Multi-tenant architecture",
    body: "Business data is isolated by tenant so appointments, staff, customers, services, and analytics remain scoped to the correct organization.",
  },
  {
    title: "Booking conflict prevention",
    body: "Availability is validated on the server against staff schedules, service duration, existing appointments, and booking rules rather than relying only on frontend validation.",
  },
  {
    title: "Grounded AI responses",
    body: "Gemini uses controlled function calling to retrieve application data, reducing unsupported answers and connecting the assistant to real services and availability.",
  },
  {
    title: "Separated deployment",
    body: "The React frontend is deployed independently on Cloudflare, while the Django API and PostgreSQL services run on Render, improving frontend delivery speed and deployment flexibility.",
  },
  {
    title: "Testability",
    body: "Business rules are covered with automated tests for authentication, scheduling, tenant isolation, analytics, AI behavior, and security-sensitive workflows.",
  },
];

const stack = [
  { group: "Frontend", items: "React, TypeScript, Vite, React Router, Axios" },
  { group: "Backend", items: "Python, Django, Django REST Framework" },
  { group: "Data", items: "PostgreSQL" },
  { group: "AI", items: "Google Gemini, function calling, grounded application data" },
  { group: "Authentication", items: "JWT, refresh-token rotation, role-based access control" },
  { group: "Quality", items: "Pytest, Vitest, OpenAPI 3.0, coverage gates" },
  { group: "Deployment", items: "Docker, Cloudflare, Render, GitHub Actions" },
];

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="beauty-card p-7 sm:p-10">
      <h2 className="text-2xl text-heading">{title}</h2>
      <div className="mt-4 space-y-4 leading-7 text-secondary">{children}</div>
    </section>
  );
}

export default function CaseStudy() {
  return (
    <>
      <PageHero
        eyebrow="Full-stack AI SaaS case study"
        title="From appointment booking to AI-assisted business decisions."
        description="BloomFlow AI is a self-initiated SaaS product case study that demonstrates how this platform was designed, engineered, tested, and deployed end to end."
      />

      <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6 lg:py-20">
        <dl className="mb-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {meta.map((m) => (
            <div key={m.label} className="rounded-[20px] border border-rose/15 bg-surface p-4 shadow-raised">
              <dt className="text-[10px] font-bold uppercase tracking-[.12em] text-muted">{m.label}</dt>
              <dd className="mt-2 text-sm font-semibold text-heading">{m.value}</dd>
            </div>
          ))}
        </dl>

        <div className="space-y-7">
          <Section title="The Challenge">
            <p>
              Appointment-based businesses often manage bookings, staff schedules, promotions,
              customer communication, and revenue across disconnected tools. This creates
              scheduling conflicts, manual work, fragmented customer experiences, and limited
              visibility into business performance.
            </p>
          </Section>

          <Section title="The Solution">
            <p>
              A unified multi-tenant platform connects customer booking, staff availability,
              loyalty, reminders, promotions, administration, revenue analytics, and AI-assisted
              support through one consistent product experience.
            </p>
          </Section>

          <Section title="What This Covers">
            <ul className="grid gap-2 sm:grid-cols-2">
              {contributions.map((c) => (
                <li key={c} className="flex items-start gap-2">
                  <span aria-hidden="true" className="mt-1 text-coral">✦</span>
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </Section>

          <Section title="Key Engineering Decisions">
            <div className="space-y-5">
              {decisions.map((d) => (
                <div key={d.title}>
                  <h3 className="font-semibold text-heading">{d.title}</h3>
                  <p className="mt-1">{d.body}</p>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Technology Stack">
            <dl className="grid gap-4 sm:grid-cols-2">
              {stack.map((s) => (
                <div key={s.group}>
                  <dt className="text-xs font-bold uppercase tracking-[.1em] text-muted">{s.group}</dt>
                  <dd className="mt-1">{s.items}</dd>
                </div>
              ))}
            </dl>
          </Section>
        </div>
      </div>
    </>
  );
}
