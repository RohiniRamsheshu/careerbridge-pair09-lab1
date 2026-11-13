const welcomeMessage = { sender: "assistant", text: "Hi! I can help you find jobs and events in the Pair 09 region." };

export function createInitialAssistantState() {
  return { messages: [{ ...welcomeMessage }], input: "", conversationId: null, pendingSave: null, loading: false, error: "" };
}
