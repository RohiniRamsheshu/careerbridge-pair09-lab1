const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:9090";


export function registerForEvent(eventId) {
  return request(`/events/${eventId}/register`, {
    method: "POST",
  });
}

async function request(path, options = {}) {
  const { headers = {}, ...rest } = options;
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  localStorage.setItem("access_token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
}

export function updateStudentProfile(profile) {
  return request("/student/profile", {
    method: "PUT",
    body: JSON.stringify(profile),
  });
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

