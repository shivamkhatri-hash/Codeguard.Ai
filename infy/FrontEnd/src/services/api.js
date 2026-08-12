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

export { API_BASE_URL };