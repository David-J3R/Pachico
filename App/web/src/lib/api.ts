import { ChatResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendMessage(
  message: string,
  threadId: string
): Promise<ChatResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000);

  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, thread_id: threadId }),
      signal: controller.signal,
    });

    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`API error ${res.status}: ${body || res.statusText}`);
    }

    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Request timed out — the agent took too long to respond.");
    }
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      throw new Error(
        "Cannot reach the backend. Make sure FastAPI is running on " + API_URL
      );
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export function getFileUrl(relativePath: string): string {
  const normalized = relativePath.replace(/\\/g, "/");
  return `${API_URL}/${normalized}`;
}
