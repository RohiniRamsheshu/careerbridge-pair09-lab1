import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildJobQuery, getApplicantProfile, getEventRegistrantProfile, getEventRegistrants, getEvents, getJob, getStudentApplications, isAuthenticatedUser, login, previewApplicantResume, updateStudentProfile } from "./api.js";

beforeEach(() => {
  vi.stubGlobal("localStorage", { getItem: () => null, setItem: vi.fn(), removeItem: vi.fn() });
  vi.stubGlobal("window", { dispatchEvent: vi.fn() });
});

describe("backend-supported job query mapping", () => {
  it("accepts only authenticated student or company identities", () => {
    expect(isAuthenticatedUser({ id: 1, email: "student@example.com", role: "student" })).toBe(true);
    expect(isAuthenticatedUser({ id: 2, email: "company@example.com", role: "company" })).toBe(true);
    expect(isAuthenticatedUser(null)).toBe(false);
    expect(isAuthenticatedUser({ id: 1, email: "user@example.com", role: "admin" })).toBe(false);
    expect(isAuthenticatedUser({ id: 1, role: "student" })).toBe(false);
  });

  it("rejects malformed login responses without storing a session", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, status: 200, text: async () => JSON.stringify({ access_token: "token", user: null }) })));
    await expect(login("student@example.com", "password")).rejects.toThrow("Invalid authentication response");
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });

  it("maps title, company, category, city, remote, salary, and pagination fields", () => {
    const query = buildJobQuery({ title: "data", company: "Test Co", category: "internship", city: "San Jose", remote: false, minimum_salary: 20, maximum_salary: 80 });
    expect(query.toString()).toBe("limit=50&offset=0&title=data&company=Test+Co&category=internship&city=San+Jose&remote=false&minimum_salary=20&maximum_salary=80");
  });

  it("does not send unsupported empty filters", () => {
    const query = buildJobQuery({ title: "", company: "", remote: "" });
    expect(query.toString()).toBe("limit=50&offset=0");
  });

  it("preserves supported pagination for jobs and events", async () => {
    const fetchMock = vi.fn(async (url) => ({ ok: true, status: 200, text: async () => "[]", url }));
    vi.stubGlobal("fetch", fetchMock);
    await getEvents({ city: "San Jose", limit: 50, offset: 50 });
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:9090/events?limit=50&offset=50&city=San+Jose");
    expect(buildJobQuery({ limit: 50, offset: 100 }).toString()).toBe("limit=50&offset=100");
  });

  it("requests backend total metadata without changing default list callers", async () => {
    const fetchMock = vi.fn(async (url) => ({ ok: true, status: 200, text: async () => JSON.stringify({ items: [], total: 0, limit: 50, offset: 0 }), url }));
    vi.stubGlobal("fetch", fetchMock);
    const { getJobs } = await import("./api.js");
    await getJobs({ include_total: true });
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:9090/jobs?limit=50&offset=0&include_total=true");
  });

  it("uses the existing read endpoints for applications, job details, and registrants", async () => {
    const fetchMock = vi.fn(async (url) => ({ ok: true, status: 200, text: async () => "[]", url }));
    vi.stubGlobal("fetch", fetchMock);
    await getStudentApplications();
    await getJob(12);
    await getEventRegistrants(8);
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:9090/applications/student",
      "http://localhost:9090/jobs/12",
      "http://localhost:9090/events/8/registrants",
    ]);
  });

  it("loads authorized profile endpoints and validates PDF previews", async () => {
    const pdf = new Blob(["%PDF-1.7\nresume"], { type: "application/pdf" });
    const profileResponse = { id: 4, name: "Student", college: "SJSU" };
    const fetchMock = vi.fn(async (url) => ({
      ok: true,
      status: 200,
      headers: { get: (name) => name === "content-type" ? (url.includes("/resume") ? "application/pdf" : "application/json") : null },
      blob: async () => pdf,
      text: async () => JSON.stringify(profileResponse),
      url,
    }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(getApplicantProfile(8, 12)).resolves.toEqual(profileResponse);
    await expect(getEventRegistrantProfile(8, 4)).resolves.toEqual(profileResponse);
    await expect(previewApplicantResume(8, 12)).resolves.toEqual(pdf);
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:9090/applications/company/jobs/8/applicants/12/profile",
      "http://localhost:9090/company/events/8/registrants/4/profile",
      "http://localhost:9090/applications/company/jobs/8/applicants/12/resume",
    ]);
  });

  it("surfaces profile authorization and invalid-PDF errors", async () => {
    vi.stubGlobal("fetch", vi.fn(async (url) => {
      if (url.includes("/profile")) return { ok: false, status: 403, text: async () => JSON.stringify({ detail: "Forbidden" }) };
      return {
        ok: true,
        status: 200,
        headers: { get: () => "application/pdf" },
        blob: async () => new Blob(["not a pdf"], { type: "application/pdf" }),
      };
    }));
    await expect(getApplicantProfile(8, 12)).rejects.toThrow("Forbidden");
    await expect(previewApplicantResume(8, 12)).rejects.toThrow("valid PDF");
  });

  it("surfaces FastAPI detail errors without reporting success", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, status: 403, text: async () => JSON.stringify({ detail: "Forbidden" }) })));
    await expect(getEventRegistrants(8)).rejects.toThrow("Forbidden");
  });

  it("sends the supported student name in profile updates", async () => {
    const fetchMock = vi.fn(async (_url, options) => ({ ok: true, status: 200, text: async () => JSON.stringify({ message: "updated" }), options }));
    vi.stubGlobal("fetch", fetchMock);
    await updateStudentProfile({ name: "Updated Student", college: "SJSU" });
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ name: "Updated Student", college: "SJSU" });
  });
});
