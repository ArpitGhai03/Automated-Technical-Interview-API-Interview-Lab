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
  created_at: string;
}
