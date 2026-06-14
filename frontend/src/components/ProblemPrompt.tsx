import type { ReactNode } from "react";
import type { Problem } from "../types";

interface ProblemPromptProps {
  problem: Problem | null;
}

// Tiny markdown-lite renderer for the prompt: `code` spans and **bold**.
function renderInline(text: string): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((token, i) => {
    if (token.startsWith("`") && token.endsWith("`")) {
      return <code key={i}>{token.slice(1, -1)}</code>;
    }
    if (token.startsWith("**") && token.endsWith("**")) {
      return <strong key={i}>{token.slice(2, -2)}</strong>;
    }
    return <span key={i}>{token}</span>;
  });
}

export function ProblemPrompt({ problem }: ProblemPromptProps) {
  return (
    <section className="problem-prompt">
      <h2 className="problem-title">{problem ? problem.title : "Loading…"}</h2>
      {problem && <p className="problem-body">{renderInline(problem.prompt)}</p>}
    </section>
  );
}
