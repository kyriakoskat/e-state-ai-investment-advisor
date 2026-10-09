import type {
  Property, SessionState, UserProfile, FinancialAnalysis, FinalRecommendation,
} from "./types";

// API base resolution: in production configure VITE_API_BASE_URL at build time.
// Locally, Vite proxies /api requests to the backend container.
// Do not embed a live production deployment URL in this public repository.
function resolveBase(): string {
  const fromEnv = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, "");
  return fromEnv ? `${fromEnv}/api` : "/api";
}

const BASE = resolveBase();

// ---------- REST -----------------------------------------------------------

export async function listProperties(): Promise<Property[]> {
  const r = await fetch(`${BASE}/properties`);
  if (!r.ok) throw new Error(`GET /properties ${r.status}`);
  return r.json();
}

export async function getProperty(id: string): Promise<Property> {
  const r = await fetch(`${BASE}/properties/${encodeURIComponent(id)}`);
  if (!r.ok) throw new Error(`GET /properties/${id} ${r.status}`);
  return r.json();
}

export async function createSession(): Promise<{ session_id: string }> {
  const r = await fetch(`${BASE}/session`, { method: "POST" });
  if (!r.ok) throw new Error(`POST /session ${r.status}`);
  return r.json();
}

export async function resetSession(sessionId: string): Promise<void> {
  await fetch(`${BASE}/session/${encodeURIComponent(sessionId)}/reset`, { method: "POST" });
}

export async function getSessionState(sessionId: string): Promise<SessionState> {
  const r = await fetch(`${BASE}/session/${encodeURIComponent(sessionId)}/state`);
  if (!r.ok) throw new Error(`GET /session/${sessionId}/state ${r.status}`);
  return r.json();
}

// ---------- SSE chat stream -----------------------------------------------

export type StreamEvent =
  | { type: "status";          data: { stage: string; label: string } }
  | { type: "message";         data: { delta: string } }
  | { type: "profile_partial"; data: UserProfile }
  | { type: "profile_ready";   data: UserProfile }
  | { type: "candidates";      data: Property[] }
  | { type: "financial";       data: FinancialAnalysis }
  | { type: "decision";        data: FinalRecommendation }
  | { type: "final_message";   data: { text: string } }
  | { type: "error";           data: { message: string } };

export async function streamChat(
  sessionId: string,
  message: string,
  onEvent: (evt: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal,
  });
  if (!res.ok || !res.body) {
    onEvent({ type: "error", data: { message: `Chat request failed: ${res.status}` } });
    return;
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const evt = parseFrame(frame);
      if (evt) onEvent(evt);
    }
  }
  if (buffer.trim()) {
    const evt = parseFrame(buffer);
    if (evt) onEvent(evt);
  }
}

function parseFrame(raw: string): StreamEvent | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
  }
  if (dataLines.length === 0) return null;
  const dataStr = dataLines.join("\n");
  try {
    const data = JSON.parse(dataStr);
    return { type: event as StreamEvent["type"], data } as StreamEvent;
  } catch {
    return { type: "message", data: { delta: dataStr } as { delta: string } };
  }
}
