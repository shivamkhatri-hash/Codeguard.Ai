const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "object" && data?.detail
        ? data.detail
        : typeof data === "object" && data?.message
          ? data.message
          : typeof data === "string" && data
            ? data
            : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data;
}

export async function submitCode({ language, code }) {
  const response = await fetch(`${API_BASE_URL}/api/code/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code })
  });
  return parseResponse(response);
}

export async function uploadCodeFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/code/upload`, {
    method: "POST",
    body: formData
  });

  return parseResponse(response);
}

export async function getAnalysisHistory() {
  const response = await fetch(`${API_BASE_URL}/api/analysis`);
  return parseResponse(response);
}

export async function deleteAnalysis(analysisId) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${encodeURIComponent(analysisId)}`, {
    method: "DELETE"
  });
  return parseResponse(response);
}

export async function generateRemediation(analysisId) {
  const response = await fetch(
    `${API_BASE_URL}/api/remediation/${encodeURIComponent(analysisId)}`,
    {
      method: "POST",
    }
  );

  return parseResponse(response);
}

export async function getPRSummary(analysisId) {
  const response = await fetch(
    `${API_BASE_URL}/api/summary/${encodeURIComponent(analysisId)}`,
    {
      method: "GET",
    }
  );

  return parseResponse(response);
}

export async function sendChatMessage({ query, analysisId, language, history }) {
  const response = await fetch(`${API_BASE_URL}/api/assistant/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      analysis_id: analysisId || null,
      language: language || "python",
      history: history || [],
    }),
  });

  return parseResponse(response);
}

export { API_BASE_URL };