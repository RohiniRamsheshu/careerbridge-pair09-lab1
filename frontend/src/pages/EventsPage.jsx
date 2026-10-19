import { useEffect, useMemo, useState } from "react";
import { getEvents, registerForEvent } from "../services/api.js";
function formatEventDate(dateValue) {
  const [year, month, day] = dateValue.split("-").map(Number);

  return new Date(year, month - 1, day).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function formatEventTime(secondsValue) {
  const totalMinutes = Math.floor(Number(secondsValue) / 60);
  const hours24 = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  const suffix = hours24 >= 12 ? "PM" : "AM";
  const hours12 = hours24 % 12 || 12;

  const [eventError, setEventError] = useState("");
const [registering, setRegistering] = useState(false);

  return `${hours12}:${String(minutes).padStart(2, "0")} ${suffix}`;
}
function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("All");
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [registeredEvent, setRegisteredEvent] = useState(null);
  const [savedEvents, setSavedEvents] = useState([]);

  useEffect(() => {
    async function loadEvents() {
      try {
        setLoading(true);
        setError("");

        const data = await getEvents();

        const normalizedEvents = (Array.isArray(data) ? data : []).map(
          (event) => ({
            id: event.id,
            title: event.name,
            organizer: event.company_name || "CareerBridge",
            location: event.location || "Location unavailable",
            date: formatEventDate(event.event_date),
            time: formatEventTime(event.event_time),
            type: "Career Event",
            description: event.description || "",
            eligibility: event.eligibility || "",
          })
        );

        setEvents(normalizedEvents);
      } catch (requestError) {
        setError(requestError.message || "Unable to load events.");
      } finally {
        setLoading(false);
      }
    }

    loadEvents();
  }, []);

  const filteredEvents = useMemo(() => {
  return events.filter((event) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      event.title.toLowerCase().includes(searchText) ||
      event.organizer.toLowerCase().includes(searchText) ||
      event.type.toLowerCase().includes(searchText);

    const matchesLocation =
      location === "All" || event.location.includes(location);

    return matchesSearch && matchesLocation;
  });
}, [events, search, location]);
  function saveEvent(event) {
    const confirmed = window.confirm(
      `Do you want to save "${event.title}" to your profile?`
    );

    if (!confirmed) {
      return;
    }

    setSavedEvents((current) =>
      current.includes(event.id)
        ? current.filter((id) => id !== event.id)
        : [...current, event.id]
    );
  }

  async function handleRegisterForEvent(event) {
  setRegistering(true);
  setEventError("");

  try {
    await registerForEvent(event.id);
    setRegisteredEvent(event);
    setSelectedEvent(null);
  } catch (error) {
    setEventError(error.message);
  } finally {
    setRegistering(false);
  }
}

  return (
    <section>
      <p className="eyebrow">COMMUNITY</p>
      <h1>Upcoming Events</h1>
      <p className="subtitle">
        Discover workshops, networking sessions, and employer events.
      </p>

      <div className="event-filters">
        <input
          className="search-box"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search events or organizers"
        />

        <select
          value={location}
          onChange={(event) => setLocation(event.target.value)}
        >
          <option value="All">All locations</option>
          <option value="San Jose">San Jose</option>
          <option value="Mountain View">Mountain View</option>
          <option value="Palo Alto">Palo Alto</option>
        </select>
      </div>
      {loading && <p className="subtitle">Loading events...</p>}

{error && <div className="error-message">{error}</div>}

      <p className="result-count">
        {filteredEvents.length} event
        {filteredEvents.length === 1 ? "" : "s"} found
      </p>

      <div className="event-list">
        {filteredEvents.map((event) => (
          <article className="event-card" key={event.id}>
            <div className="event-date">
              <strong>{event.date.split(" ")[1].replace(",", "")}</strong>
              <span>{event.date.split(" ")[0]}</span>
            </div>

            <div className="event-content">
              <div className="event-header">
                <div>
                  <h2>{event.title}</h2>
                  <p className="event-meta">
                    {event.organizer} · {event.location}
                  </p>
                </div>

                <span className="event-type">{event.type}</span>
              </div>

              <p>{event.description}</p>

              <p className="event-time">
                {event.date} · {event.time}
              </p>

              <div className="event-actions">
                <button
                  className="secondary-button"
                  onClick={() => setSelectedEvent(event)}
                >
                  View details
                </button>

                <button
                  className={
                    savedEvents.includes(event.id)
                      ? "saved-button"
                      : "secondary-button"
                  }
                  onClick={() => saveEvent(event)}
                >
                  {savedEvents.includes(event.id) ? "Saved" : "Save event"}
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {selectedEvent && (
        <div className="modal-overlay">
          <div className="job-modal">
            <button
              className="close-button"
              onClick={() => setSelectedEvent(null)}
            >
              ×
            </button>

            <p className="eyebrow">EVENT DETAILS</p>
            <h2>{selectedEvent.title}</h2>
            <p className="event-meta">
              {selectedEvent.organizer} · {selectedEvent.location}
            </p>

            <p>{selectedEvent.description}</p>

            <p className="event-time">
              {selectedEvent.date} · {selectedEvent.time}
            </p>

            <button
  className="primary-button"
  onClick={() => handleRegisterForEvent(selectedEvent)}
  disabled={registering}
>
  {registering ? "Registering..." : "Register"}
</button>
          </div>
        </div>
      )}

      {registeredEvent && (
        <div className="success-message">
          Registered for <strong>{registeredEvent.title}</strong>.
          <button onClick={() => setRegisteredEvent(null)}>Dismiss</button>
        </div>
      )}
    </section>
  );
}

{eventError && (
  <div className="error-message">
    Registration failed: {eventError}
  </div>
)}

export default EventsPage;