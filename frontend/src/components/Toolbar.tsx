interface ToolbarProps {
  language: string;
  onLanguageChange: (lang: string) => void;
  onRun: () => void;
  loading: boolean;
}

export function Toolbar({
  language,
  onLanguageChange,
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
        <select
          className="lang-select"
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          disabled={loading}
        >
          <option value="python">Python</option>
        </select>
        <button className="run-button" onClick={onRun} disabled={loading}>
          {loading ? "Running…" : "▶ Run"}
        </button>
      </div>
    </header>
  );
}
