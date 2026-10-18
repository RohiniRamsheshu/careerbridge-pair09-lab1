import { useMemo, useState } from "react";

const events = [
  {
    id: 1,
    title: "Pair 09 Career Mixer",
    organizer: "CareerBridge",
    location: "San Jose",
    date: "October 24, 2026",
    time: "5:30 PM",
    type: "Networking",
    description:
      "Meet local employers, students, and technology professionals from the Pair 09 region.",
  },
  {
    id: 2,
    title: "Building Your Technical Resume",
    organizer: "CareerBridge",
    location: "Mountain View",
    date: "November 2, 2026",
    time: "12:00 PM",
    type: "Workshop",
    description:
      "Learn how to communicate your technical projects, skills, and professional impact.",
  },
  {
    id: 3,
    title: "Introduction to Machine Learning Careers",
    organizer: "Palo Alto Research",
    location: "Palo Alto",
    date: "November 10, 2026",
    time: "6:00 PM",
    type: "Career Talk",
    description:
      "Explore career paths, internship opportunities, and skills needed for machine learning roles.",
  },
];

function EventsPage() {
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("All");
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [registeredEvent, setRegisteredEvent] = useState(null);
  const [savedEvents, setSavedEvents] = useState([]);

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const matchesSearch =
        event.title.toLowerCase().includes(search.toLowerCase()) ||
        event.organizer.toLowerCase().includes(search.toLowerCase()) ||
        event.type.toLowerCase().includes(search.toLowerCase());

      const matchesLocation =
        location === "All" || event.location === location;

      return matchesSearch && matchesLocation;
    });
  }, [search, location]);

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

  function registerForEvent(event) {
    setRegisteredEvent(event);
    setSelectedEvent(null);
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
              onClick={() => registerForEvent(selectedEvent)}
            >
              Register
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

export default EventsPage;