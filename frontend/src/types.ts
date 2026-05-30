export type SubmissionStatus = "pending" | "running" | "completed" | "error";

export interface SubmissionRequest {
  code: string;
  language: string;
}

export interface SubmissionResponse {
  id: number;
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
