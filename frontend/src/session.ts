/**
 * Tiny session-id manager. Stores one id per browser tab in localStorage.
 * Used by every chat / agent call so the backend can keep the workflow state.
 */
const KEY = "estate.session_id";

function uuid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return "s-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export function getSessionId(): string {
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = uuid();
    localStorage.setItem(KEY, id);
  }
  return id;
}

export function newSessionId(): string {
  const id = uuid();
  localStorage.setItem(KEY, id);
  return id;
}
