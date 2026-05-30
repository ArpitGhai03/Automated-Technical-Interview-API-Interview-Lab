import type { SubmissionRequest, SubmissionResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export async function submitCode(
  req: SubmissionRequest,
): Promise<SubmissionResponse> {
  const res = await fetch(`${API_URL}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API error ${res.status}: ${detail}`);
  }

  return res.json();
}
