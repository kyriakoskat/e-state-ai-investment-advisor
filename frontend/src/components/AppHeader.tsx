import { Link } from "@tanstack/react-router";
import { Satellite, RotateCcw } from "lucide-react";
import { useSession } from "../store";

export default function AppHeader() {
  const { reset, stage } = useSession();
  return (
    <header className="border-b border-border bg-card/60 backdrop-blur-sm sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-3">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 border border-primary flex items-center justify-center rounded-sm">
            <Satellite className="w-4 h-4 text-primary" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-wider ticker-glow">E-STATE · BEYOND RGB</div>
            <div className="text-[10px] text-muted-foreground tracking-[0.25em] uppercase font-mono">
              Multi-Agent Investment Advisor
            </div>
          </div>
        </Link>
        <div className="hidden md:flex items-center gap-4 text-[10px] tracking-widest uppercase font-mono">
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-positive animate-pulse" />
            <span className="terminal-value">{stage}</span>
          </div>
          <button
            onClick={reset}
            className="flex items-center gap-1.5 text-muted-foreground hover:text-primary"
            title="Start a new session"
          >
            <RotateCcw className="w-3 h-3" /> New session
          </button>
        </div>
      </div>
    </header>
  );
}
