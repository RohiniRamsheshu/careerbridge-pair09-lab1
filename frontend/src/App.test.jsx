import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { RoleRedirect } from "./App.jsx";
import { createInitialAssistantState } from "./pages/assistantState.js";

describe("authentication route fallback", () => {
  it("renders a safe redirect for an unauthenticated user", () => {
    expect(() => renderToStaticMarkup(
      <MemoryRouter initialEntries={["/unknown"]}>
        <RoleRedirect user={null} />
      </MemoryRouter>
    )).not.toThrow();
  });

  it("does not treat an invalid stored identity as a role", () => {
    expect(() => renderToStaticMarkup(
      <MemoryRouter initialEntries={["/unknown"]}>
        <RoleRedirect user={{ role: "unknown" }} />
      </MemoryRouter>
    )).not.toThrow();
  });

  it("creates a clean assistant state for a new conversation", () => {
    const state = createInitialAssistantState();
    expect(state.conversationId).toBeNull();
    expect(state.pendingSave).toBeNull();
    expect(state.input).toBe("");
    expect(state.error).toBe("");
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0].text).toContain("find jobs and events");
  });
});
