import { useState } from "react";
import { assistantChat, confirmAssistantAction } from "../services/api.js";
import { createInitialAssistantState } from "./assistantState.js";

const suggestions = ["Find a remote data science internship", "Show upcoming events", "Find machine learning opportunities in Palo Alto"];
const internalToolCall = /^\s*(get_student_preferences|search_jobs|get_job_details|search_events|save_job_or_event)\s*\(/i;
function cleanAssistantText(text, hasPendingSave = false) {
  if (hasPendingSave) return "I found an item to save. Please review and confirm the action below.";
  if (typeof text !== "string" || internalToolCall.test(text)) return "I couldn't complete that request safely. Please try again.";
  return text;
}

function extractPending(text) {
  if (typeof text !== "string") return null;
  const match = text.match(/Confirmation required:\s*(\{.*\})/s);
  if (!match) return null;
  try { return JSON.parse(match[1]); } catch { return null; }
}

function AssistantPage() {
  const initialState = createInitialAssistantState();
  const [messages, setMessages] = useState(initialState.messages);
  const [input, setInput] = useState(initialState.input);
  const [conversationId, setConversationId] = useState(initialState.conversationId);
  const [pendingSave, setPendingSave] = useState(initialState.pendingSave);
  const [loading, setLoading] = useState(initialState.loading);
  const [error, setError] = useState(initialState.error);

  async function sendMessage(message = input) {
    const trimmed = message.trim(); if (!trimmed || loading) return;
    setInput(""); setError(""); setLoading(true); setMessages((current) => [...current, { sender: "user", text: trimmed }]);
    try {
      const response = await assistantChat(trimmed, conversationId);
      setConversationId(response.conversation_id);
      const pending = extractPending(response.answer);
      setMessages((current) => [...current, { sender: "assistant", text: cleanAssistantText(response.answer, Boolean(pending)) }]);
      setPendingSave(pending);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }
  function startNewConversation() {
    if (loading) return;
    const next = createInitialAssistantState();
    setConversationId(next.conversationId); setPendingSave(next.pendingSave); setError(next.error); setInput(next.input); setMessages(next.messages);
  }
  async function decide(approved) {
    if (!pendingSave || loading) return;
    setLoading(true); setError("");
    try {
      const result = await confirmAssistantAction(pendingSave.action_id, approved);
      setMessages((current) => [...current, { sender: "assistant", text: result.message || (approved ? "Save approved." : "Save cancelled; no database write was made.") }]);
      setPendingSave(null);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }
  return <section><div className="page-heading"><div><p className="eyebrow">CUSTOM AI ASSISTANT</p><h1>Opportunity Assistant</h1><p className="subtitle">Search for jobs and events using natural language.</p></div><button className="secondary-button" type="button" onClick={startNewConversation} disabled={loading}>New conversation</button></div>
    <div className="assistant-layout"><div className="chat-card"><div className="message-list">{messages.map((message, index) => <div className={`chat-message ${message.sender}`} key={`${message.sender}-${index}`}><span className="message-label">{message.sender === "assistant" ? "Assistant" : "You"}</span><p>{message.text}</p></div>)}</div>
      {loading && <p className="subtitle" aria-live="polite">Assistant is working...</p>}{error && <div className="error-message">{error}</div>}
      {pendingSave && <div className="confirmation-card"><strong>Action requires confirmation</strong><p>The assistant proposes saving {pendingSave.item_type} {pendingSave.item_id}. Nothing has been saved yet.</p><div className="profile-actions"><button className="primary-button" onClick={() => decide(true)} disabled={loading}>Approve save</button><button className="secondary-button" onClick={() => decide(false)} disabled={loading}>Decline</button></div></div>}
      <div className="suggestion-list">{suggestions.map((suggestion) => <button className="suggestion-button" key={suggestion} onClick={() => sendMessage(suggestion)} disabled={loading}>{suggestion}</button>)}</div>
      <form className="chat-input-row" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }} placeholder="Ask about jobs or events..." aria-label="Assistant message" disabled={loading} rows="2" /><button className="primary-button" type="submit" disabled={loading}>{loading ? "Working..." : "Send"}</button></form>
    </div><aside className="assistant-info"><p className="eyebrow">HOW IT WORKS</p><h2>Search, refine, decide.</h2><p>The assistant searches real opportunities, preserves the conversation, and asks for confirmation before saving anything.</p><ul><li>Natural-language job search</li><li>Event discovery</li><li>Conversational refinement</li><li>Confirmation before saving</li></ul><p className="safety-note"><strong>Safety &amp; Privacy:</strong> saving always requires your explicit confirmation.</p></aside></div>
  </section>;
}
export default AssistantPage;
