/**
 * SessionContext — single source of truth for the chat session + agent outputs.
 *
 * The Chatbot writes to it as SSE events arrive. The Financial / Final Decision
 * tabs and the Recommendation banner read from it. No localStorage beyond the
 * session id; everything else lives on the backend's in-memory session store.
 */
import { createContext, useCallback, useContext, useMemo, useReducer } from "react";
import type {
  FinancialAnalysis, FinalRecommendation, Property, UserProfile, SessionState, Stage,
} from "./types";
import { getSessionId, newSessionId } from "./session";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface State {
  sessionId: string;
  stage: Stage;
  statusLabel: string;
  messages: ChatMessage[];
  streaming: boolean;
  profile: UserProfile | null;
  candidates: Property[];
  financial: FinancialAnalysis | null;
  decision: FinalRecommendation | null;
  error: string | null;
}

type Action =
  | { type: "user_message"; content: string }
  | { type: "assistant_delta"; delta: string }
  | { type: "assistant_done" }
  | { type: "stage"; stage: Stage; label: string }
  | { type: "profile"; profile: UserProfile; ready: boolean }
  | { type: "candidates"; candidates: Property[] }
  | { type: "financial"; financial: FinancialAnalysis }
  | { type: "decision"; decision: FinalRecommendation }
  | { type: "final_message"; text: string }
  | { type: "error"; message: string }
  | { type: "reset"; sessionId: string }
  | { type: "start_streaming" };

function reducer(s: State, a: Action): State {
  switch (a.type) {
    case "user_message":
      return {
        ...s,
        messages: [...s.messages, { id: uid(), role: "user", content: a.content }],
        error: null,
      };
    case "start_streaming":
      return {
        ...s,
        streaming: true,
        messages: [...s.messages, { id: uid(), role: "assistant", content: "" }],
      };
    case "assistant_delta": {
      const last = s.messages[s.messages.length - 1];
      if (!last || last.role !== "assistant") return s;
      const updated = { ...last, content: last.content + a.delta };
      return { ...s, messages: [...s.messages.slice(0, -1), updated] };
    }
    case "assistant_done":
      return { ...s, streaming: false };
    case "stage":
      return { ...s, stage: a.stage, statusLabel: a.label };
    case "profile":
      return { ...s, profile: a.profile };
    case "candidates":
      return { ...s, candidates: a.candidates };
    case "financial":
      return { ...s, financial: a.financial };
    case "decision":
      return { ...s, decision: a.decision };
    case "final_message": {
      const last = s.messages[s.messages.length - 1];
      // Append the chatbot_final_response as a fresh assistant bubble.
      if (last && last.role === "assistant" && last.content.trim() === "") {
        return {
          ...s,
          messages: [
            ...s.messages.slice(0, -1),
            { ...last, content: a.text },
          ],
        };
      }
      return {
        ...s,
        messages: [...s.messages, { id: uid(), role: "assistant", content: a.text }],
      };
    }
    case "error":
      return { ...s, error: a.message, streaming: false };
    case "reset":
      return initial(a.sessionId);
  }
}

function uid(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function initial(sessionId: string): State {
  return {
    sessionId,
    stage: "profiling",
    statusLabel: "Ready",
    messages: [],
    streaming: false,
    profile: null,
    candidates: [],
    financial: null,
    decision: null,
    error: null,
  };
}

interface Ctx extends State {
  dispatch: React.Dispatch<Action>;
  hydrate: (snap: SessionState) => void;
  reset: () => void;
}

const SessionContext = createContext<Ctx | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, () => initial(getSessionId()));

  const hydrate = useCallback((snap: SessionState) => {
    if (snap.profile) dispatch({ type: "profile", profile: snap.profile, ready: snap.profile.profile_completed });
    if (snap.candidates?.length) dispatch({ type: "candidates", candidates: snap.candidates });
    if (snap.financial) dispatch({ type: "financial", financial: snap.financial });
    if (snap.decision) dispatch({ type: "decision", decision: snap.decision });
    dispatch({ type: "stage", stage: snap.stage, label: snap.stage });
  }, []);

  const reset = useCallback(() => {
    const id = newSessionId();
    dispatch({ type: "reset", sessionId: id });
  }, []);

  const value = useMemo<Ctx>(() => ({ ...state, dispatch, hydrate, reset }), [state, hydrate, reset]);
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): Ctx {
  const v = useContext(SessionContext);
  if (!v) throw new Error("useSession must be used within SessionProvider");
  return v;
}
