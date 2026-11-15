import { describe, expect, it } from "vitest";
import { assistantReducer, applicationsReducer, authReducer, conversationStarted, eventsReducer, itemAdded, jobsReducer, savedReducer, selectAssistant, selectApplications, selectEvents, selectJobs, selectSavedItems, selectUser, sessionSet } from "./slices.js";

describe("Redux Toolkit slices", () => {
  it("stores authenticated user and role without credentials", () => {
    const state = authReducer(undefined, sessionSet({ id: 7, role: "student", email: "student@example.com" }));
    expect(selectUser({ auth: state })).toMatchObject({ id: 7, role: "student" });
    expect(state.access_token).toBeUndefined();
  });

  it("stores jobs and exposes filterable job state", () => {
    const state = jobsReducer(undefined, { type: "jobs/load/fulfilled", payload: [{ id: 1, title: "Data Analyst" }] });
    expect(selectJobs({ jobs: state })).toHaveLength(1);
  });

  it("stores applications and status updates", () => {
    let state = applicationsReducer(undefined, { type: "applications/load/fulfilled", payload: [{ id: 2, status: "Pending" }] });
    state = applicationsReducer(state, { type: "applications/applicationUpdated", payload: { id: 2, status: "Reviewed" } });
    expect(selectApplications({ applications: state })[0].status).toBe("Reviewed");
  });

  it("stores event listings and registrations", () => {
    const state = eventsReducer(undefined, { type: "events/load/fulfilled", payload: [{ id: 3, name: "Career fair" }] });
    expect(selectEvents({ events: state })[0].id).toBe(3);
  });

  it("adds and removes saved items through predictable actions", () => {
    let state = savedReducer(undefined, itemAdded({ id: 4, item_type: "job", item_id: 1 }));
    state = savedReducer(state, { type: "saved/itemRemoved", payload: 4 });
    expect(selectSavedItems({ saved: state })).toEqual([]);
  });

  it("resets assistant conversation without changing authentication", () => {
    const state = assistantReducer(undefined, conversationStarted("conversation-2"));
    expect(selectAssistant({ assistant: state })).toMatchObject({ conversationId: "conversation-2", pendingSave: null });
    expect(state.messages).toHaveLength(1);
  });
});
