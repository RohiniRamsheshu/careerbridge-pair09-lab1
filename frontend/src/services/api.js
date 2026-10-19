const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:9090";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

export function getJobs(filters = {}) {
  const params = new URLSearchParams();

  params.set("limit", "50");
  params.set("offset", "0");

  if (filters.title) params.set("title", filters.title);
  if (filters.company) params.set("company", filters.company);
  if (filters.category) params.set("category", filters.category);
  if (filters.city) params.set("city", filters.city);

  return request(`/jobs?${params.toString()}`);
}

export function getJob(jobId) {
  return request(`/jobs/${jobId}`);
}

export function getEvents() {
  return request("/events?limit=50&offset=0");
}