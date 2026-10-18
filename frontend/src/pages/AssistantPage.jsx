import { useState } from "react";

const suggestions = [
  "Find a remote data science internship",
  "Show upcoming events",
  "Find machine learning opportunities in Palo Alto",
];

function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hi Rohini! I can help you find jobs and events in the Pair 09 region.",
    },
  ]);

  const [input, setInput] = useState("");
  const [pendingSave, setPendingSave] = useState(null);

  function createAssistantResponse(userMessage) {
    const message = userMessage.toLowerCase();

    if (message.includes("remote") && message.includes("data")) {
      return "I found a Remote Data Science Intern opportunity with BlueOrbit Systems in Mountain View. Would you like to save it?";
    }

    if (message.includes("event")) {
      return "I found upcoming events including the Pair 09 Career Mixer and the Technical Resume Workshop. Would you like to see the event listings?";
    }

    if (
      message.includes("machine learning") ||
      message.includes("palo alto")
    ) {
      return "I found a Machine Learning Assistant opportunity at Palo Alto Research. Would you like to save it?";
    }

    if (message.includes("save")) {
      return "I can save that opportunity, but I need your confirmation before changing your profile.";
    }

    return "I can search jobs and events by title, skill, location, and work mode. Try asking for a remote data science internship.";
  }

  function sendMessage(message = input) {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    const response = createAssistantResponse(trimmedMessage);

    setMessages((current) => [
      ...current,
      { sender: "user", text: trimmedMessage },
      { sender: "assistant", text: response },
    ]);

    setInput("");

    if (
      trimmedMessage.toLowerCase().includes("remote") &&
      trimmedMessage.toLowerCase().includes("data")
    ) {
      setPendingSave({
        type: "job",
        title: "Remote Data Science Intern",
      });
    }
  }

  function confirmSave() {
    const confirmed = window.confirm(
      `Allow the assistant to save "${pendingSave.title}"?`
    );

    if (confirmed) {
      setMessages((current) => [
        ...current,
        {
          sender: "assistant",
          text: `${pendingSave.title} was saved successfully.`,
        },
      ]);
    } else {
      setMessages((current) => [
        ...current,
        {
          sender: "assistant",
          text: "Save cancelled. No profile data was changed.",
        },
      ]);
    }

    setPendingSave(null);
  }

  return (
    <section>
      <p className="eyebrow">CUSTOM AI ASSISTANT</p>
      <h1>Opportunity Assistant</h1>
      <p className="subtitle">
        Search for jobs and events using natural language.
      </p>

      <div className="assistant-layout">
        <div className="chat-card">
          <div className="message-list">
            {messages.map((message, index) => (
              <div
                className={`chat-message ${message.sender}`}
                key={`${message.sender}-${index}`}
              >
                <span className="message-label">
                  {message.sender === "assistant" ? "Assistant" : "You"}
                </span>
                <p>{message.text}</p>
              </div>
            ))}
          </div>

          {pendingSave && (
            <div className="confirmation-card">
              <strong>Action requires confirmation</strong>
              <p>
                The assistant wants to save:{" "}
                <strong>{pendingSave.title}</strong>
              </p>
              <button className="primary-button" onClick={confirmSave}>
                Review and confirm
              </button>
            </div>
          )}

          <div className="suggestion-list">
            {suggestions.map((suggestion) => (
              <button
                className="suggestion-button"
                key={suggestion}
                onClick={() => sendMessage(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>

          <form
            className="chat-input-row"
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage();
            }}
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about jobs or events..."
              aria-label="Assistant message"
            />
            <button className="primary-button" type="submit">
              Send
            </button>
          </form>
        </div>

        <aside className="assistant-info">
          <p className="eyebrow">HOW IT WORKS</p>
          <h2>Search, refine, decide.</h2>
          <p>
            The assistant searches opportunities, answers follow-up questions,
            and asks for confirmation before saving anything.
          </p>
          <ul>
            <li>Natural-language job search</li>
            <li>Event discovery</li>
            <li>Conversational refinement</li>
            <li>Confirmation before saving</li>
          </ul>
        </aside>
      </div>
    </section>
  );
}

export default AssistantPage;