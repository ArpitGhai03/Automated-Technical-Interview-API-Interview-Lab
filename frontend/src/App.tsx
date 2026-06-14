import { useEffect, useState } from "react";
import { getProblems, submitCode } from "./api";
import type { Problem, SubmissionResponse } from "./types";
import { Toolbar } from "./components/Toolbar";
import { ProblemPrompt } from "./components/ProblemPrompt";
import { Editor } from "./components/Editor";
import { TestResults } from "./components/TestResults";
import { ErrorPanel } from "./components/ErrorPanel";
import { OutputPanel } from "./components/OutputPanel";

export default function App() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [problemId, setProblemId] = useState("");
  const [code, setCode] = useState("");
  const [submission, setSubmission] = useState<SubmissionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);

  // Load the problem catalog once; select the first problem.
  useEffect(() => {
    getProblems()
      .then((list) => {
        setProblems(list);
        if (list.length > 0) {
          setProblemId(list[0].id);
          setCode(list[0].starter_code);
        }
      })
      .catch((err) =>
        setRequestError(err instanceof Error ? err.message : String(err)),
      );
  }, []);

  const problem = problems.find((p) => p.id === problemId) ?? null;

  function handleProblemChange(id: string) {
    const next = problems.find((p) => p.id === id);
    setProblemId(id);
    setSubmission(null);
    setRequestError(null);
    if (next) setCode(next.starter_code);
  }

  async function handleRun() {
    if (!problem) return;
    setLoading(true);
    setRequestError(null);
    try {
      const response = await submitCode({ problem_id: problem.id, code });
      setSubmission(response);
    } catch (err) {
      setRequestError(err instanceof Error ? err.message : String(err));
      setSubmission(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <Toolbar
        problems={problems}
        problemId={problemId}
        onProblemChange={handleProblemChange}
        language={problem?.language ?? ""}
        onRun={handleRun}
        loading={loading}
      />
      <ProblemPrompt problem={problem} />
      <main className="workspace">
        <Editor
          value={code}
          language={problem?.language ?? "plaintext"}
          onChange={setCode}
        />
        <aside className="side-panels">
          <TestResults submission={submission} loading={loading} />
          <OutputPanel submission={submission} loading={loading} />
          <ErrorPanel submission={submission} requestError={requestError} />
        </aside>
      </main>
    </div>
  );
}
