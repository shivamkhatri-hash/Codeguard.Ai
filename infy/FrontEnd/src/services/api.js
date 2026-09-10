const rawApiUrl = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/['"]/g, "");
const API_BASE_URL = (rawApiUrl || "http://localhost:8000").replace(/\/$/, "");

async function parseResponse(response) {
  if (response.status === 204) {
    return { success: true };
  }

  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = text;
  }

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

export async function submitCode({ language, code, filename }) {
  const response = await fetch(`${API_BASE_URL}/api/code/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code, filename: filename || undefined })
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

export async function getAnalysisById(analysisId) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${encodeURIComponent(analysisId)}`);
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

export function getAuthToken() {
  return localStorage.getItem("codeguard_token") || "";
}

export function getAuthUser() {
  try {
    const data = localStorage.getItem("codeguard_user");
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

export function saveAuth(authData) {
  localStorage.setItem("codeguard_token", authData.token);
  localStorage.setItem("codeguard_user", JSON.stringify(authData));
}

export function clearAuth() {
  localStorage.removeItem("codeguard_token");
  localStorage.removeItem("codeguard_user");
}

function getAuthHeaders() {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function loginUser({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await parseResponse(response);
  saveAuth(data);
  return data;
}

export async function signupUser({ email, password, full_name, role }) {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name, role: role || "developer" })
  });
  const data = await parseResponse(response);
  saveAuth(data);
  return data;
}

export async function getCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders()
  });
  return parseResponse(response);
}

export async function getAdminUsers() {
  const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
    headers: getAuthHeaders()
  });
  return parseResponse(response);
}

export async function toggleUserStatus(userId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${encodeURIComponent(userId)}/status`, {
    method: "POST",
    headers: getAuthHeaders()
  });
  return parseResponse(response);
}

export async function getAdminStats() {
  const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
    headers: getAuthHeaders()
  });
  return parseResponse(response);
}

export function downloadPDFReportUrl(analysisId) {
  return `${API_BASE_URL}/api/report/pdf/${encodeURIComponent(analysisId)}`;
}

export { API_BASE_URL };