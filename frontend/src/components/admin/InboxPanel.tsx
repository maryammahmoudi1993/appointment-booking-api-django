import { useEffect, useState } from "react";
import { supportApi, type SupportMessage } from "../../api/client";

export default function InboxPanel() {
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyDrafts, setReplyDrafts] = useState<Record<number, string>>({});
  const [sendingId, setSendingId] = useState<number | null>(null);

  const fetchAll = () => {
    setLoading(true);
    supportApi
      .list()
      .then((res) => setMessages(res.data.results))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleReply = async (id: number) => {
    const text = (replyDrafts[id] ?? "").trim();
    if (!text) return;
    setSendingId(id);
    try {
      await supportApi.reply(id, text);
      setReplyDrafts((d) => ({ ...d, [id]: "" }));
      fetchAll();
    } catch {
      alert("Failed to send reply.");
    } finally {
      setSendingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-10">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const unreadCount = messages.filter((m) => !m.is_read).length;

  return (
    <div>
      <div className="mb-6">
        <div className="inline-flex rounded-2xl bg-brand-50 p-5 text-brand-800">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide opacity-70">
              Unread messages
            </p>
            <p className="mt-1 font-display text-3xl font-bold">{unreadCount}</p>
          </div>
        </div>
      </div>

      {messages.length === 0 ? (
        <p className="text-sm text-charcoal-light">No messages yet.</p>
      ) : (
        <div className="space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`rounded-2xl border bg-white p-6 shadow-sm ${
                m.is_read ? "border-champagne/15" : "border-brand-300"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-charcoal">
                    {m.customer_name}
                    {!m.is_read && (
                      <span className="ml-2 rounded-full bg-brand-100 px-2 py-0.5 text-xs font-medium text-brand-700">
                        New
                      </span>
                    )}
                  </p>
                  <p className="mt-1 text-sm text-charcoal">{m.message}</p>
                  <p className="mt-1 text-xs text-charcoal-light/70">
                    {new Date(m.created_at).toLocaleString()}
                  </p>
                </div>
              </div>

              {m.admin_reply ? (
                <div className="mt-4 rounded-xl bg-brand-50 p-3 text-sm text-brand-800">
                  <p className="text-xs font-semibold uppercase tracking-wide opacity-70">
                    Your reply
                  </p>
                  <p className="mt-1">{m.admin_reply}</p>
                </div>
              ) : (
                <div className="mt-4 flex gap-2">
                  <input
                    value={replyDrafts[m.id] ?? ""}
                    onChange={(e) =>
                      setReplyDrafts((d) => ({ ...d, [m.id]: e.target.value }))
                    }
                    onKeyDown={(e) => e.key === "Enter" && handleReply(m.id)}
                    placeholder="Type a reply..."
                    className="flex-1 rounded-lg border border-champagne/30 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                  <button
                    onClick={() => handleReply(m.id)}
                    disabled={sendingId === m.id}
                    className="rounded-full bg-brand-600 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
                  >
                    {sendingId === m.id ? "Sending..." : "Reply"}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
