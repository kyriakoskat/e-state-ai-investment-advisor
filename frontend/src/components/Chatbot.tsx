/**
 * The conversational entry point. Owns the SSE stream and routes the typed
 * events into the global SessionContext.
 *
 * Visible chat content = `messages[]` of {user, assistant}. Other event types
 * (profile_ready, candidates, financial, decision) silently populate the side
 * panels and agent reasoning tabs.
 */
import { useEffect, useRef, useState } from "react";
import { MessageSquare, Send, Sparkles, X } from "lucide-react";
import ReactMarkdown from "react-markdown";

import { streamChat } from "../api";
import { useSession } from "../store";

const SUGGESTED = [
  "I have 1M EUR and I want low-risk farmland in central Greece.",
  "Looking for the best plot for solar panels.",
  "Θέλω επένδυση με γρήγορη απόσβεση σε αγροτική γη.",
  "Compare the top plots for wind energy.",
];

export default function Chatbot() {
  const [open, setOpen] = useState(true);
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const session = useSession();

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [session.messages, session.streaming]);

  const submit = async (text: string) => {
    if (!text.trim() || session.streaming) return;
    setInput("");
    session.dispatch({ type: "user_message", content: text });
    session.dispatch({ type: "start_streaming" });

    try {
      await streamChat(session.sessionId, text, (evt) => {
        switch (evt.type) {
          case "message":
            session.dispatch({ type: "assistant_delta", delta: evt.data.delta });
            break;
          case "status":
            session.dispatch({ type: "stage", stage: evt.data.stage as never, label: evt.data.label });
            break;
          case "profile_partial":
          case "profile_ready":
            session.dispatch({ type: "profile", profile: evt.data, ready: evt.type === "profile_ready" });
            break;
          case "candidates":
            session.dispatch({ type: "candidates", candidates: evt.data });
            break;
          case "financial":
            session.dispatch({ type: "financial", financial: evt.data });
            break;
          case "decision":
            session.dispatch({ type: "decision", decision: evt.data });
            break;
          case "final_message":
            session.dispatch({ type: "final_message", text: evt.data.text });
            break;
          case "error":
            session.dispatch({ type: "error", message: evt.data.message });
            break;
        }
      });
    } finally {
      session.dispatch({ type: "assistant_done" });
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-[9999] flex items-center gap-2 px-5 py-3 bg-primary text-primary-foreground font-mono text-xs font-bold tracking-widest uppercase shadow-lg rounded-md hover:opacity-90"
      >
        <Sparkles className="w-4 h-4" /> Investment Copilot
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-[9999] w-[440px] max-w-[calc(100vw-2rem)] h-[640px] max-h-[calc(100vh-3rem)] flex flex-col terminal-panel rounded-md shadow-2xl">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${session.streaming ? "bg-warning animate-pulse" : "bg-positive"}`} />
          <div>
            <div className="text-xs font-bold tracking-wider">INVESTMENT COPILOT</div>
            <div className="text-[10px] text-muted-foreground tracking-widest uppercase font-mono">
              {session.statusLabel}
            </div>
          </div>
        </div>
        <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {session.messages.length === 0 && (
          <div className="space-y-3">
            <div className="text-xs text-muted-foreground leading-relaxed">
              Tell me your <b>exploitation type</b> (agriculture, PV, wind, battery, data center),
              optionally your <b>preferred region</b> and <b>budget</b>. I will rank the best plots
              and explain the trade-offs.
            </div>
            <div className="space-y-1.5 pt-2">
              <div className="terminal-label">Try:</div>
              {SUGGESTED.map((s) => (
                <button
                  key={s}
                  onClick={() => submit(s)}
                  className="block w-full text-left text-xs px-3 py-2 border border-border hover:border-primary hover:bg-card rounded-sm"
                >
                  → {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {session.messages.map((m) => (
          <div key={m.id} className={m.role === "user" ? "flex justify-end" : ""}>
            <div
              className={
                m.role === "user"
                  ? "max-w-[85%] px-3 py-2 bg-primary text-primary-foreground text-xs font-mono rounded-sm"
                  : "max-w-[92%] text-sm leading-relaxed agent-md"
              }
            >
              {m.role === "assistant" && (
                <div className="terminal-label mb-1.5 flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-accent" /> COPILOT
                </div>
              )}
              {m.role === "assistant"
                ? <ReactMarkdown>{m.content || (session.streaming ? "…" : "")}</ReactMarkdown>
                : m.content}
            </div>
          </div>
        ))}

        {session.error && (
          <div className="text-xs text-negative border border-negative/50 rounded-sm px-3 py-2">
            {session.error}
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); submit(input); }}
        className="flex items-center gap-2 px-3 py-3 border-t border-border"
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={session.streaming ? "Working…" : "Type your goal…"}
          disabled={session.streaming}
          className="flex-1 bg-input border border-border px-3 py-2 text-xs font-mono focus:outline-none focus:border-primary rounded-sm"
        />
        <button
          type="submit"
          disabled={!input.trim() || session.streaming}
          className="p-2 bg-primary text-primary-foreground disabled:opacity-40 rounded-sm"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

export function ChatLauncherIcon() { return <MessageSquare className="w-4 h-4" />; }
