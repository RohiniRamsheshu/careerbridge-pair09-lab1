import { useState } from "react";
import { confirmAssistantAction } from "../services/api.js";
import { createInitialAssistantState } from "./assistantState.js";
import { useDispatch, useSelector } from "react-redux";
import { confirmationResolved, conversationStarted, selectAssistant, sendAssistantMessage } from "../store/slices.js";

const suggestions = ["Find a remote data science internship", "Show upcoming events", "Find machine learning opportunities in Palo Alto"];
function AssistantPage() {
  const initialState = createInitialAssistantState();
  const [input, setInput] = useState(initialState.input);
  const dispatch = useDispatch();
  const assistant = useSelector(selectAssistant);
  const { messages, conversationId, pendingSave, metrics } = assistant;
  const loading = assistant.status === "loading";
  const error = assistant.error || "";

  async function sendMessage(message = input) {
    const trimmed = message.trim(); if (!trimmed || loading) return;
    setInput("");
    try {
      await dispatch(sendAssistantMessage({ message: trimmed, conversationId })).unwrap();
    } catch { /* Redux stores the recoverable request error. */ }
  }
  function startNewConversation() {
    if (loading) return;
    const next = createInitialAssistantState();
    dispatch(conversationStarted(next.conversationId)); setInput(next.input);
  }
  async function decide(approved) {
    if (!pendingSave || loading) return;
    try {
      const result = await confirmAssistantAction(pendingSave.action_id, approved);
      dispatch(confirmationResolved({ sender: "assistant", text: result.message || (approved ? "Save approved." : "Save cancelled; no database write was made.") }));
    } catch { /* Keep the pending action visible when approval fails. */ }
  }
  return <section><div className="page-heading"><div><p className="eyebrow">CUSTOM AI ASSISTANT</p><h1>Opportunity Assistant</h1><p className="subtitle">Search for jobs and events using natural language.</p></div><button className="secondary-button" type="button" onClick={startNewConversation} disabled={loading}>New conversation</button></div>
    <div className="assistant-layout"><div className="chat-card"><div className="message-list">{messages.map((message, index) => <div className={`chat-message ${message.sender}`} key={`${message.sender}-${index}`}><span className="message-label">{message.sender === "assistant" ? "Assistant" : "You"}</span><p>{message.text}</p></div>)}</div>
      {loading && <p className="subtitle" aria-live="polite">Assistant is working...</p>}{error && <div className="error-message">{error}</div>}
      {metrics && <p className="assistant-metrics" aria-live="polite">Context: {metrics.context_utilization_percent}% ({metrics.estimated ? "estimated" : "provider reported"} tokens){metrics.warning ? " — context warning" : ""}</p>}
      {pendingSave && <div className="confirmation-card"><strong>Action requires confirmation</strong><p>The assistant proposes saving {pendingSave.item_type} {pendingSave.item_id}. Nothing has been saved yet.</p><div className="profile-actions"><button className="primary-button" onClick={() => decide(true)} disabled={loading}>Approve save</button><button className="secondary-button" onClick={() => decide(false)} disabled={loading}>Decline</button></div></div>}
      <div className="suggestion-list">{suggestions.map((suggestion) => <button className="suggestion-button" key={suggestion} onClick={() => sendMessage(suggestion)} disabled={loading}>{suggestion}</button>)}</div>
      <form className="chat-input-row" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }} placeholder="Ask about jobs or events..." aria-label="Assistant message" disabled={loading} rows="2" /><button className="primary-button" type="submit" disabled={loading}>{loading ? "Working..." : "Send"}</button></form>
    </div><aside className="assistant-info"><p className="eyebrow">HOW IT WORKS</p><h2>Search, refine, decide.</h2><p>The assistant searches real opportunities, preserves the conversation, and asks for confirmation before saving anything.</p><ul><li>Natural-language job search</li><li>Event discovery</li><li>Conversational refinement</li><li>Confirmation before saving</li></ul><p className="safety-note"><strong>Safety &amp; Privacy:</strong> saving always requires your explicit confirmation.</p></aside></div>
  </section>;
}
export default AssistantPage;
