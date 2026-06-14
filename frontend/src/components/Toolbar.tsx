import type { Problem } from "../types";

interface ToolbarProps {
  problems: Problem[];
  problemId: string;
  onProblemChange: (id: string) => void;
  language: string;
  onRun: () => void;
  loading: boolean;
}

export function Toolbar({
  problems,
  problemId,
  onProblemChange,
  language,
  onRun,
  loading,
}: ToolbarProps) {
  return (
    <header className="toolbar">
      <div className="toolbar-left">
        <span className="toolbar-logo">⌨</span>
        <h1 className="toolbar-title">Interview Lab</h1>
      </div>
      <div className="toolbar-right">
        {language && <span className="lang-badge">{language.toUpperCase()}</span>}
        <select
          className="lang-select"
          value={problemId}
          onChange={(e) => onProblemChange(e.target.value)}
          disabled={loading || problems.length === 0}
        >
          {problems.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title}
            </option>
          ))}
        </select>
        <button
          className="run-button"
          onClick={onRun}
          disabled={loading || problems.length === 0}
        >
          {loading ? "Running…" : "▶ Run"}
        </button>
      </div>
    </header>
  );
}
