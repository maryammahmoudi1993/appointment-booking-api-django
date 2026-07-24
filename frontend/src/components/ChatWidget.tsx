import { useState, useRef, useEffect } from "react";
import { copilotApi, type CopilotResponse } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: CopilotResponse["tool_calls_made"];
}

const SUGGESTIONS = [
  "What services do you offer?",
  "Show me available times for tomorrow",
  "Recommend a service for me",
  "What are your opening hours?",
  "Check my upcoming appointments",
];

export default function ChatWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");

    // The copilot endpoint requires authentication. Without this guard an
    // anonymous visitor's request would 401, which the global axios
    // interceptor treats as an expired session and redirects to /login —
    // a jarring surprise for someone who was just browsing anonymously.
    if (!user) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Please sign in first so I can help with your bookings and account.",
        },
      ]);
      return;
    }

    setLoading(true);

    try {
      const { data } = await copilotApi.chat({
        message: msg,
        conversation_id: conversationId,
      });

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

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
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 bg-rosegold-gradient text-white rounded-full p-4 shadow-lg transition-all hover:shadow-xl hover:scale-105 active:scale-95 motion-reduce:hover:scale-100"
        aria-label="Toggle AI assistant"
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 max-h-[520px] bg-white rounded-2xl shadow-2xl border border-champagne/20 flex flex-col overflow-hidden">
          <div className="bg-rosegold-gradient text-white px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold">
                B
              </div>
              <div>
                <h3 className="font-semibold text-sm">BloomFlow Assistant</h3>
                <p className="text-xs text-white/80">Ask about services, book, or get help</p>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[300px] max-h-[350px] bg-cream">
            {messages.length === 0 && (
              <div className="mt-12 text-center">
                <div className="h-12 w-12 mx-auto mb-3 rounded-full bg-champagne/20 flex items-center justify-center">
                  <svg className="h-6 w-6 text-coral-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <p className="text-charcoal-light text-sm mb-4">How can I help you today?</p>
                <div className="space-y-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      className="block w-full text-left px-3 py-2 text-sm bg-white border border-champagne/20 hover:border-champagne hover:bg-champagne/10 rounded-lg transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                    msg.role === "user"
                      ? "bg-rosegold-gradient text-white rounded-br-md"
                      : "bg-white text-charcoal border border-champagne/20 rounded-bl-md shadow-sm"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {msg.toolCalls.map((tc) => {
                        const toolName = typeof tc === "string" ? tc : tc.tool;
                        return (
                        <span key={toolName} className="text-[10px] px-1.5 py-0.5 rounded bg-champagne/20 text-coral-dark font-mono">
                          {toolName}
                        </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-champagne/20 px-4 py-2 rounded-2xl rounded-bl-md shadow-sm">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 bg-champagne/50 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="h-2 w-2 bg-champagne/50 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="h-2 w-2 bg-champagne/50 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-champagne/20 p-3 bg-white">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about our services..."
                disabled={loading}
                className="flex-1 border border-champagne/20 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-champagne/40 focus:border-transparent disabled:opacity-50"
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="bg-rosegold-gradient text-white px-4 py-2 rounded-xl text-sm font-medium shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
