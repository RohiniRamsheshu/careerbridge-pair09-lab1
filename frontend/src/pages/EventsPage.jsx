import { useEffect, useMemo, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { loadEvents, loadSavedItems } from "../store/slices.js";
import { createSavedItem, deleteSavedItem, getStudentEventRegistrations, registerForEvent } from "../services/api.js";

function formatEventDate(value) {
  if (!value) return "Date unavailable";
  const [year, month, day] = String(value).split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}
function formatEventTime(value) {
  if (typeof value === "string" && value.includes(":")) return value.slice(0, 5);
  const totalMinutes = Math.floor(Number(value || 0) / 60); const hours = Math.floor(totalMinutes / 60); const minutes = totalMinutes % 60;
  return `${hours % 12 || 12}:${String(minutes).padStart(2, "0")} ${hours >= 12 ? "PM" : "AM"}`;
}

function EventsPage() {
  const PAGE_SIZE = 50;
  const dispatch = useDispatch();
  const [events, setEvents] = useState([]); const [registeredEvents, setRegisteredEvents] = useState([]); const [savedEventRecords, setSavedEventRecords] = useState({});
  const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [search, setSearch] = useState(""); const [location, setLocation] = useState("All"); const [selectedEvent, setSelectedEvent] = useState(null); const [registeredEvent, setRegisteredEvent] = useState(null); const [eventError, setEventError] = useState(""); const [registering, setRegistering] = useState(false); const [page, setPage] = useState(0); const [totalEvents, setTotalEvents] = useState(0); const requestSequence = useRef(0);

  useEffect(() => {
    async function load() {
      const requestId = ++requestSequence.current;
      try {
        const [eventResult, savedRows, registrationRows] = await Promise.all([dispatch(loadEvents({ name: search.trim() || undefined, city: location !== "All" ? location : undefined, include_total: true, limit: PAGE_SIZE, offset: page * PAGE_SIZE })).unwrap(), dispatch(loadSavedItems()).unwrap(), getStudentEventRegistrations()]);
        const eventRows = Array.isArray(eventResult) ? eventResult : eventResult.items;
        if (requestId !== requestSequence.current) return;
        setTotalEvents(Array.isArray(eventResult) ? eventRows.length : (eventResult.total ?? 0));
        setEvents((Array.isArray(eventRows) ? eventRows : []).map((event) => ({ ...event, title: event.name, organizer: event.company_name || "CareerBridge", date: formatEventDate(event.event_date), time: formatEventTime(event.event_time), type: "Career Event" })));
        const savedEvents = (savedRows || []).filter((item) => item.item_type === "event");
        setSavedEventRecords(Object.fromEntries(savedEvents.map((item) => [item.item_id, item.id])));
        setRegisteredEvents(registrationRows || []);
      } catch (requestError) { if (requestId === requestSequence.current) setError(requestError.message || "Unable to load events."); }
      finally { if (requestId === requestSequence.current) setLoading(false); }
    }
    load();
  }, [dispatch, search, location, page]);
  useEffect(() => { setPage(0); }, [search, location]);

  const filteredEvents = useMemo(() => events.filter((event) => {
    const query = search.toLowerCase();
    return ((event.title || "").toLowerCase().includes(query) || (event.organizer || "").toLowerCase().includes(query)) && (location === "All" || (event.location || "").includes(location));
  }), [events, search, location]);

  async function saveEvent(event) {
    const savedItemId = savedEventRecords[event.id];
    if (!window.confirm(savedItemId ? `Remove "${event.title}" from your saved items?` : `Do you want to save "${event.title}" to your profile?`)) return;
    try {
      if (savedItemId) { await deleteSavedItem(savedItemId); setSavedEventRecords((current) => { const next = { ...current }; delete next[event.id]; return next; }); }
      else { const saved = await createSavedItem("event", event.id); setSavedEventRecords((current) => ({ ...current, [event.id]: saved.id })); }
    } catch (requestError) { setEventError(`Could not update saved event: ${requestError.message}`); }
  }
  async function register(event) {
    setRegistering(true); setEventError("");
    try { await registerForEvent(event.id); setRegisteredEvent(event); setSelectedEvent(null); setRegisteredEvents((current) => [...current, event]); }
    catch (requestError) { setEventError(requestError.message); }
    finally { setRegistering(false); }
  }

  return <section><p className="eyebrow">COMMUNITY</p><h1>Upcoming Events</h1><p className="subtitle">Discover workshops, networking sessions, and employer events.</p>
    <div className="event-filters"><input className="search-box" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search events or organizers" /><select value={location} onChange={(event) => setLocation(event.target.value)}><option value="All">All locations</option><option>San Jose</option><option>Mountain View</option><option>Palo Alto</option></select></div>
    {loading && <p className="subtitle">Loading events...</p>}{error && <div className="error-message">{error}</div>}{eventError && <div className="error-message">{eventError}</div>}
    <p className="result-count">{totalEvents} matching event{totalEvents === 1 ? "" : "s"} · Showing {totalEvents === 0 ? 0 : page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, totalEvents)} of {totalEvents}</p>
    <div className="event-list">{filteredEvents.map((event) => <article className="event-card" key={event.id}><div className="event-date"><strong>{event.date.split(" ")[1]?.replace(",", "")}</strong><span>{event.date.split(" ")[0]}</span></div><div className="event-content"><div className="event-header"><div><h2>{event.title}</h2><p className="event-meta">{event.organizer} · {event.location}</p></div><span className="event-type">{event.type}</span></div><p>{event.description}</p><p className="event-time">{event.date} · {event.time}</p><div className="event-actions"><button className="secondary-button" onClick={() => setSelectedEvent(event)}>View details</button><button className={savedEventRecords[event.id] ? "saved-button" : "secondary-button"} onClick={() => saveEvent(event)}>{savedEventRecords[event.id] ? "Saved" : "Save event"}</button></div></div></article>)}</div>
    {filteredEvents.length === 0 && <div className="empty-card">No events match your current search filters.</div>}
    <div className="pagination-controls" aria-label="Event results pagination"><button className="secondary-button" type="button" onClick={() => setPage((current) => Math.max(0, current - 1))} disabled={page === 0 || loading}>Previous</button><span>Page {page + 1} of {Math.max(1, Math.ceil(totalEvents / PAGE_SIZE))}</span><button className="secondary-button" type="button" onClick={() => setPage((current) => current + 1)} disabled={loading || (page + 1) * PAGE_SIZE >= totalEvents}>Next</button></div>
    <div className="company-panel student-events-history"><p className="eyebrow">MY REGISTERED EVENTS</p>{registeredEvents.length === 0 ? <p className="subtitle">You have no registered upcoming events.</p> : registeredEvents.map((event) => <div className="posting-row" key={event.id}><div><h3>{event.name}</h3><p>{event.event_date} · {event.location}</p></div><span>Registered</span></div>)}</div>
    {selectedEvent && <div className="modal-overlay"><div className="job-modal"><button className="close-button" onClick={() => setSelectedEvent(null)}>×</button><p className="eyebrow">EVENT DETAILS</p><h2>{selectedEvent.title}</h2><p className="event-meta">{selectedEvent.organizer} · {selectedEvent.location}</p><p>{selectedEvent.description}</p><p className="event-time">{selectedEvent.date} · {selectedEvent.time}</p><button className="primary-button" onClick={() => register(selectedEvent)} disabled={registering}>{registering ? "Registering..." : "Register"}</button></div></div>}
    {registeredEvent && <div className="success-message">Registered for <strong>{registeredEvent.title}</strong>.<button onClick={() => setRegisteredEvent(null)}>Dismiss</button></div>}
  </section>;
}
export default EventsPage;
