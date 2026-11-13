const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:9090").replace(/\/$/, "");

function getErrorMessage(response, body) {
  if (body && typeof body === "object" && body.detail) {
    if (Array.isArray(body.detail)) return body.detail.map((item) => item.msg || "Validation error").join("; ");
    return String(body.detail);
  }
  if (typeof body === "string" && body.trim()) return body;
  return `Request failed: ${response.status}`;
}

async function request(path, options = {}) {
  const { headers = {}, ...rest } = options;
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      ...(rest.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });
  const text = await response.text();
  let body = null;
  try { body = text ? JSON.parse(text) : null; } catch { body = text; }
  if (!response.ok) {
    if (response.status === 401) window.dispatchEvent(new Event("careerbridge:unauthorized"));
    throw new Error(getErrorMessage(response, body));
  }
  return body;
}

async function requestPdf(path) {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    const text = await response.text();
    let body = null;
    try { body = text ? JSON.parse(text) : null; } catch { body = text; }
    if (response.status === 401) window.dispatchEvent(new Event("careerbridge:unauthorized"));
    throw new Error(getErrorMessage(response, body));
  }

  const contentType = (response.headers.get("content-type") || "").split(";", 1)[0].toLowerCase();
  const blob = await response.blob();
  if (contentType !== "application/pdf" || blob.type && blob.type !== "application/pdf") {
    throw new Error("The applicant resume response was not a PDF.");
  }
  const signature = new TextDecoder().decode(await blob.slice(0, 5).arrayBuffer());
  if (signature !== "%PDF-") throw new Error("The applicant resume is not a valid PDF.");
  return blob;
}

export function getApiBaseUrl() { return API_BASE_URL; }
export function isAuthenticatedUser(value) {
  return Boolean(
    value &&
    (value.role === "student" || value.role === "company") &&
    value.id !== undefined &&
    typeof value.email === "string"
  );
}
export function registerAccount(payload) { return request("/auth/register", { method: "POST", body: JSON.stringify(payload) }); }
export async function login(email, password) {
  const data = await request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  if (!data?.access_token || !isAuthenticatedUser(data.user)) {
    throw new Error("Invalid authentication response.");
  }
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("careerbridge_user", JSON.stringify(data.user));
  return data;
}
export function getMe() { return request("/auth/me"); }
export function logout() { localStorage.removeItem("access_token"); localStorage.removeItem("careerbridge_user"); }
export function getStudentDashboard() { return request("/dashboard/student"); }
export function getCompanyDashboard() { return request("/dashboard/company"); }
export function getStudentProfile() { return request("/student/profile"); }
export function updateStudentProfile(profile) { return request("/student/profile", { method: "PUT", body: JSON.stringify(profile) }); }
export function getCompanyProfile() { return request("/company/profile"); }
export function updateCompanyProfile(profile) { return request("/company/profile", { method: "PUT", body: JSON.stringify(profile) }); }
export function getJobs(filters = {}) {
  const params = buildJobQuery(filters);
  return request(`/jobs?${params.toString()}`);
}
export function buildJobQuery(filters = {}) {
  const params = new URLSearchParams({ limit: "50", offset: "0" });
  if (filters.title) params.set("title", filters.title);
  if (filters.company) params.set("company", filters.company);
  if (filters.category) params.set("category", filters.category);
  if (filters.city) params.set("city", filters.city);
  if (filters.remote !== undefined && filters.remote !== "") params.set("remote", String(filters.remote));
  if (filters.minimum_salary !== undefined && filters.minimum_salary !== "") params.set("minimum_salary", String(filters.minimum_salary));
  if (filters.maximum_salary !== undefined && filters.maximum_salary !== "") params.set("maximum_salary", String(filters.maximum_salary));
  return params;
}
export function getJob(jobId) { return request(`/jobs/${jobId}`); }
export function getStudentApplications() { return request("/applications/student"); }
export function createJob(payload) { return request("/jobs", { method: "POST", body: JSON.stringify(payload) }); }
export function getCompanyJobs() { return request("/company/jobs"); }
export function getApplicants(jobId) { return request(`/applications/company/jobs/${jobId}/applicants`); }
export function getApplicantProfile(jobId, applicationId) { return request(`/applications/company/jobs/${jobId}/applicants/${applicationId}/profile`); }
export function previewApplicantResume(jobId, applicationId) { return requestPdf(`/applications/company/jobs/${jobId}/applicants/${applicationId}/resume`); }
export function updateApplicationStatus(jobId, applicationId, status) { return request(`/applications/company/jobs/${jobId}/applicants/${applicationId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }); }
export function searchStudents(filters = {}) {
  const params = new URLSearchParams({ limit: "50" });
  for (const field of ["name", "college", "major", "city"]) if (filters[field]) params.set(field, filters[field]);
  return request(`/search/students?${params.toString()}`);
}
export function applyToJob(jobId, resumePath = null) { return request(`/applications/${jobId}/apply`, { method: "POST", body: JSON.stringify(resumePath ? { resume_path: resumePath } : {}) }); }
export function getEvents(filters = {}) {
  const params = new URLSearchParams({ limit: "50", offset: "0" });
  if (filters.name) params.set("name", filters.name);
  if (filters.city) params.set("city", filters.city);
  if (filters.event_date) params.set("event_date", filters.event_date);
  return request(`/events?${params.toString()}`);
}
export function registerForEvent(eventId) { return request(`/events/${eventId}/register`, { method: "POST" }); }
export function getStudentEventRegistrations() { return request("/events/student/registrations"); }
export function getCompanyEvents() { return request("/company/events"); }
export function getEventRegistrants(eventId) { return request(`/events/${eventId}/registrants`); }
export function getEventRegistrantProfile(eventId, studentId) { return request(`/company/events/${eventId}/registrants/${studentId}/profile`); }
export function createEvent(payload) { return request("/events", { method: "POST", body: JSON.stringify(payload) }); }
export function updateEvent(eventId, payload) { return request(`/events/${eventId}`, { method: "PUT", body: JSON.stringify(payload) }); }
export function deleteEvent(eventId) { return request(`/events/${eventId}`, { method: "DELETE" }); }
export function createSavedItem(itemType, itemId) { return request("/saved-items", { method: "POST", body: JSON.stringify({ item_type: itemType, item_id: itemId }) }); }
export function getSavedItems() { return request("/saved-items"); }
export function deleteSavedItem(savedItemId) { return request(`/saved-items/${savedItemId}`, { method: "DELETE" }); }
export function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/applications/resume", { method: "POST", body: formData });
}
export function listResumes() { return request("/applications/resume"); }
export async function assistantChat(message, conversationId) {
  const started = performance.now();
  try {
    return await request("/assistant/chat", { method: "POST", body: JSON.stringify({ message, ...(conversationId ? { conversation_id: conversationId } : {}) }) });
  } finally {
    console.debug("careerbridge_assistant_request_ms", Math.round(performance.now() - started));
  }
}
export function confirmAssistantAction(actionId, approved) { return request("/assistant/confirm", { method: "POST", body: JSON.stringify({ action_id: actionId, approved }) }); }

