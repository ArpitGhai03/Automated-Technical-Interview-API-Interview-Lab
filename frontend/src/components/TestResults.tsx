import type { SubmissionResponse } from "../types";

interface TestResultsProps {
  submission: SubmissionResponse | null;
  loading: boolean;
}

export function TestResults({ submission, loading }: TestResultsProps) {
  return (
    <section className="panel test-results">
      <h3 className="panel-title">Test Results</h3>
      <div className="panel-body">{renderBody(submission, loading)}</div>
    </section>
  );
}

function renderBody(submission: SubmissionResponse | null, loading: boolean) {
  if (loading) {
    return <div className="muted">Running…</div>;
  }
  if (!submission) {
    return <div className="muted">Run your code to see test results.</div>;
  }

  const passed = submission.status === "completed";
  return (
    <>
      <div className={passed ? "test-row pass" : "test-row fail"}>
        <span className="test-icon">{passed ? "✓" : "✗"}</span>
        <span className="test-label">
          Test 1 {passed ? "passed" : "failed"}
        </span>
      </div>
      {passed && submission.output && (
        <pre className="output-block">{submission.output}</pre>
      )}
    </>
  );
}
