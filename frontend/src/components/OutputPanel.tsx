import type { SubmissionResponse } from "../types";

interface OutputPanelProps {
  submission: SubmissionResponse | null;
  loading: boolean;
}

export function OutputPanel({ submission, loading }: OutputPanelProps) {
  return (
    <section className="panel output-panel">
      <h3 className="panel-title">Output</h3>
      <div className="panel-body">{renderBody(submission, loading)}</div>
    </section>
  );
}

function renderBody(submission: SubmissionResponse | null, loading: boolean) {
  if (loading) {
    return <div className="muted">Running…</div>;
  }
  if (!submission) {
    return <div className="muted">Run your code to see output.</div>;
  }

  if (submission.status === "error") {
    return (
      <pre className="output-block error">{submission.output || "Unknown error"}</pre>
    );
  }

  return (
    <pre className="output-block">
      {submission.output || "(No output)"}
    </pre>
  );
}
