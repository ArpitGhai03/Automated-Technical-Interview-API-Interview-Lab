import type { SubmissionResponse } from "../types";

interface ErrorPanelProps {
  submission: SubmissionResponse | null;
  requestError: string | null;
}

export function ErrorPanel({ submission, requestError }: ErrorPanelProps) {
  const errorText = resolveError(submission, requestError);

  return (
    <section className="panel error-panel">
      <h3 className="panel-title">Errors</h3>
      <div className="panel-body">
        {errorText ? (
          <pre className="error-block">{errorText}</pre>
        ) : (
          <div className="muted">No errors.</div>
        )}
      </div>
    </section>
  );
}

function resolveError(
  submission: SubmissionResponse | null,
  requestError: string | null,
): string | null {
  if (requestError) return requestError;
  if (submission && submission.status === "error") {
    return submission.output ?? "Unknown error.";
  }
  return null;
}
