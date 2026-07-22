import { useState, useRef, useEffect } from "react";
import { copilotApi } from "../../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: string[];
}

const QUICK_PROMPTS = [
  { label: "Revenue this month", icon: "$", prompt: "Show revenue this month" },
  { label: "Completion rate", icon: "%", prompt: "What is our completion rate?" },
  { label: "Top staff", icon: "*", prompt: "Top performing staff" },
  { label: "Popular services", icon: "#", prompt: "Most popular services" },
  { label: "30-day forecast", icon: "~", prompt: "Forecast next 30 days revenue" },
  { label: "Staff performance", icon: "@", prompt: "How is each staff member performing?" },
];

export default function AdminCopilotPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    setLoading(true);

    try {
      const { data } = await copilotApi.adminChat({ message: msg });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          toolCalls: data.tool_calls_made,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Failed to get analytics. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-champagne/20 shadow-sm flex flex-col h-[520px]">
      <div className="border-b border-champagne/15 px-4 py-3 bg-gradient-to-r from-cream to-white">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-champagne/20 flex items-center justify-center">
            <svg className="h-4 w-4 text-coral-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-sm text-charcoal">Analytics Copilot</h3>
            <p className="text-[11px] text-charcoal-light">Ask about your business performance</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-cream/50">
        {messages.length === 0 && (
          <div className="mt-6">
            <p className="text-charcoal-light/70 text-xs font-medium uppercase tracking-wide text-center mb-3">
              Quick queries
            </p>
            <div className="grid grid-cols-2 gap-2">
              {QUICK_PROMPTS.map(({ label, icon, prompt }) => (
                <button
                  key={label}
                  onClick={() => sendMessage(prompt)}
                  className="flex items-center gap-2 px-3 py-2.5 text-sm bg-white border border-champagne/20 hover:border-indigo-300 hover:bg-champagne/10 rounded-lg transition-colors text-left"
                >
                  <span className="h-5 w-5 rounded bg-champagne/20 text-coral-dark flex items-center justify-center text-[10px] font-bold shrink-0">
                    {icon}
                  </span>
                  <span className="text-charcoal">{label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm ${
                msg.role === "user"
                  ? "bg-coral-dark text-white rounded-br-md"
                  : "bg-white text-charcoal border border-champagne/20 rounded-bl-md shadow-sm"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {msg.toolCalls.map((tc) => (
                    <span key={tc} className="text-[10px] px-1.5 py-0.5 rounded bg-champagne/20 text-coral-dark font-mono">
                      {tc}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-champagne/20 px-4 py-2 rounded-2xl rounded-bl-md shadow-sm">
              <div className="flex gap-1">
                <span className="h-2 w-2 bg-coral-dark/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="h-2 w-2 bg-coral-dark/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="h-2 w-2 bg-coral-dark/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-champagne/15 p-3 bg-white">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), sendMessage())}
            placeholder="Ask about revenue, staff, services..."
            disabled={loading}
            className="flex-1 border border-champagne/20 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="bg-coral-dark text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-coral-dark/90 disabled:opacity-50 transition-colors"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}
