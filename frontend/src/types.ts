export type SubmissionStatus = "pending" | "running" | "completed" | "error";

export interface Problem {
  id: string;
  title: string;
  language: string;
  prompt: string;
  starter_code: string;
}

export interface SubmissionRequest {
  problem_id: string;
  code: string;
}

export interface SubmissionResponse {
  id: number;
  problem_id: string | null;
  code: string;
  language: string;
  status: SubmissionStatus;
  output: string | null;
  runtime?: number | null;
  test_passed?: number | null;
  test_total?: number | null;
  test_results?: boolean[] | null;  // Individual test results
  created_at: string;
}
