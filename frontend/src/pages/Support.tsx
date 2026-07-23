import { useEffect, useRef, useState } from "react";
import { supportApi, type SupportMessage } from "../api/client";
import PageHero from "../components/ui/PageHero";

export default function Support() {
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const load = () => {
    setLoading(true);
    setError("");
    supportApi.list()
      .then((res) => setMessages(res.data.results.slice().reverse()))
      .catch(() => setError("We couldn’t load your conversation."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  const send = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!draft.trim()) return;
    setSending(true);
    setError("");
    try {
      const { data } = await supportApi.send(draft.trim());
      setMessages((current) => [...current, data]);
      setDraft("");
    } catch {
      setError("Your message wasn’t sent. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <PageHero eyebrow="Concierge support" title="We’re here to help." description="Send our salon team a message about appointments, services, accessibility, or anything that would make your visit more comfortable." />
      <section className="mx-auto max-w-4xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
        <div className="overflow-hidden rounded-[32px] border border-rose/15 bg-surface shadow-soft">
          <header className="flex items-center gap-4 border-b border-rose/10 bg-soft p-5 sm:p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rosegold-gradient text-xl text-white" aria-hidden="true">✦</div>
            <div><h2 className="font-sans text-base font-bold text-heading">BloomFlow concierge</h2><p className="mt-1 flex items-center gap-2 text-xs text-secondary"><span className="h-2 w-2 rounded-full bg-success" />Salon team available</p></div>
          </header>
          <div className="min-h-[360px] max-h-[520px] overflow-y-auto bg-[linear-gradient(180deg,#fffaf7,#feefe8)] p-5 sm:p-7" aria-live="polite">
            <div className="max-w-[82%] rounded-[22px_22px_22px_6px] bg-surface p-4 text-sm leading-6 text-secondary shadow-raised">Hello! How can our salon team help make your next visit feel effortless?</div>
            {loading && <p className="mt-5 text-center text-sm text-muted">Loading your conversation…</p>}
            {messages.map((message) => (
              <div key={message.id}>
                <div className="ml-auto mt-4 max-w-[82%] rounded-[22px_22px_6px_22px] bg-coral p-4 text-sm leading-6 text-white shadow-button">{message.message}</div>
                {message.admin_reply && <div className="mt-4 max-w-[82%] rounded-[22px_22px_22px_6px] bg-surface p-4 text-sm leading-6 text-secondary shadow-raised">{message.admin_reply}</div>}
              </div>
            ))}
            {!loading && !messages.length && <p className="mt-5 text-center text-sm text-muted">No previous messages—start whenever you’re ready.</p>}
            <div ref={endRef} />
          </div>
          <form onSubmit={send} className="border-t border-rose/10 bg-surface p-4 sm:p-5">
            {error && <div role="alert" className="mb-3 flex items-center justify-between rounded-2xl bg-error/10 px-4 py-3 text-sm text-error"><span>{error}</span><button type="button" onClick={load} className="font-bold underline">Retry</button></div>}
            <div className="flex gap-3">
              <label className="sr-only" htmlFor="support-message">Message the salon</label>
              <textarea id="support-message" className="beauty-input min-h-12 flex-1 resize-none py-3" rows={1} placeholder="Write a message…" value={draft} onChange={(e) => setDraft(e.target.value)} />
              <button className="beauty-button min-w-20" disabled={sending || !draft.trim()} aria-label="Send message">{sending ? "…" : "Send"}</button>
            </div>
          </form>
        </div>
      </section>
    </>
  );
}
