import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { supportApi } from "../api/client";

type ChatMessage = { from: "bot" | "user"; text: string };

const GREETING =
  "Hi! I'm here to help with bookings, rescheduling, or any questions about Bloom Studio. Quick answers below, or send the team a message and it'll land straight in their inbox.";

const QUICK_REPLIES: { label: string; reply: string }[] = [
  {
    label: "Reschedule my appointment",
    reply:
      "Head to My Bookings, cancel the current time, then rebook a slot that works better.",
  },
  {
    label: "Cancel a booking",
    reply:
      "You can cancel any pending booking from My Bookings — look for the Cancel button next to it.",
  },
  {
    label: "Ask about pricing",
    reply:
      "Pricing for every service is listed on the Services page, right next to the duration.",
  },
];

export default function SupportWidget() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { from: "bot", text: GREETING },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const handleQuickReply = (label: string, reply: string) => {
    setMessages((m) => [...m, { from: "user", text: label }, { from: "bot", text: reply }]);
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    if (!user) {
      setMessages((m) => [
        ...m,
        { from: "user", text },
        { from: "bot", text: "Please sign in first so our team knows who to reply to." },
      ]);
      setInput("");
      return;
    }

    setSending(true);
    setMessages((m) => [...m, { from: "user", text }]);
    setInput("");
    try {
      await supportApi.send(text);
      setMessages((m) => [
        ...m,
        {
          from: "bot",
          text: "Sent! Your message is in our team's inbox — we'll get back to you soon.",
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { from: "bot", text: "Sorry, that didn't go through. Please try again." },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-40">
      {open && (
        <div className="mb-3 flex h-[28rem] w-80 flex-col overflow-hidden rounded-2xl border border-brand-100 bg-white shadow-xl">
          <div className="flex items-center gap-3 border-b border-brand-100 bg-brand-700 px-4 py-3 text-white">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 text-xs font-bold">
              BS
            </span>
            <div>
              <p className="text-sm font-semibold">Bloom Studio Support</p>
              <p className="text-xs text-brand-100">Replies in minutes</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="ml-auto text-white/80 hover:text-white"
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto px-4 py-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                  m.from === "bot"
                    ? "bg-gray-100 text-gray-800"
                    : "ml-auto bg-brand-600 text-white"
                }`}
              >
                {m.text}
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-2 border-t border-gray-100 px-4 py-2">
            {QUICK_REPLIES.map((q) => (
              <button
                key={q.label}
                onClick={() => handleQuickReply(q.label, q.reply)}
                className="rounded-full bg-brand-50 px-3 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100"
              >
                {q.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 border-t border-gray-100 p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Message the admin..."
              className="flex-1 rounded-full border border-gray-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <button
              onClick={handleSend}
              disabled={sending}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-50"
              aria-label="Send to admin"
              title="Send to admin"
            >
              ↑
            </button>
          </div>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-2xl text-white shadow-lg transition hover:bg-brand-700"
        aria-label="Open support chat"
      >
        {open ? "✕" : "💬"}
      </button>
    </div>
  );
}
