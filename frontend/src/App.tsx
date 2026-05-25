import { useState } from "react";
import { submitCode } from "./api";
import type { SubmissionResponse } from "./types";
import { Toolbar } from "./components/Toolbar";
import { ProblemPrompt } from "./components/ProblemPrompt";
import { Editor } from "./components/Editor";
import { TestResults } from "./components/TestResults";
import { ErrorPanel } from "./components/ErrorPanel";
import { OutputPanel } from "./components/OutputPanel";

const DEFAULT_CODE = `def two_sum(nums, target):
    # TODO: return indices of the two numbers that add up to target
    pass


print(two_sum([2, 7, 11, 15], 9))
`;

export default function App() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [language, setLanguage] = useState("python");
  const [submission, setSubmission] = useState<SubmissionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setRequestError(null);
    try {
      const response = await submitCode({ code, language });
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
        language={language}
        onLanguageChange={setLanguage}
        onRun={handleRun}
        loading={loading}
      />
      <ProblemPrompt />
      <main className="workspace">
        <Editor value={code} language={language} onChange={setCode} />
        <aside className="side-panels">
          <TestResults submission={submission} loading={loading} />
          <OutputPanel submission={submission} loading={loading} />
          <ErrorPanel submission={submission} requestError={requestError} />
        </aside>
      </main>
    </div>
  );
}
