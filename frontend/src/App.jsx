import { BrowserRouter, NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe, isAuthenticatedUser, logout } from "./services/api.js";
import "./App.css";
import JobsPage from "./pages/JobsPage.jsx";
import AssistantPage from "./pages/AssistantPage.jsx";
import EventsPage from "./pages/EventsPage.jsx";
import CompanyPage from "./pages/CompanyPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import SavedItemsPage from "./pages/SavedItemsPage.jsx";
import { getCompanyDashboard, getCompanyEvents, getCompanyJobs, getSavedItems, getStudentApplications, getStudentDashboard } from "./services/api.js";
import { useDispatch } from "react-redux";
import { loggedOut, sessionSet } from "./store/slices.js";

function Layout({ children, user, onLogout }) {
  const navigate = useNavigate();
  const isCompany = user.role === "company";
  return <div className="app">
    <aside className="sidebar"><h2>CareerBridge</h2><p className="pair-label">PAIR 09</p>
      <nav>
        <NavLink to="/">Dashboard</NavLink>
        {!isCompany && <><NavLink to="/jobs">Jobs</NavLink><NavLink to="/events">Events</NavLink><NavLink to="/assistant">Assistant</NavLink></>}
        {isCompany && <NavLink to="/company">Company</NavLink>}
        {!isCompany && <><NavLink to="/profile">Profile</NavLink><NavLink to="/saved">Saved & applications</NavLink></>}
      </nav>
      <div className="profile"><strong>{user.name}</strong><span>{isCompany ? "Company" : "Student"}</span></div>
    </aside>
    <main className="main-content"><header className="topbar"><span>{isCompany ? "Company Portal" : "Student Portal"}</span><button className="logout-button" onClick={() => { onLogout(); navigate("/login"); }}>Log out</button></header>{children}</main>
  </div>;
}

function Dashboard({ user }) {
  if (user.role === "company") return <CompanyDashboard />;
  return <StudentDashboard />;
}

function CompanyDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([getCompanyDashboard(), getCompanyJobs(), getCompanyEvents()])
      .then(([summary, postings, companyEvents]) => { setDashboard(summary); setJobs(postings || []); setEvents(companyEvents || []); })
      .catch((requestError) => setError(requestError.message || "Unable to load the company overview."))
      .finally(() => setLoading(false));
  }, []);
  if (loading) return <section><p className="eyebrow">COMPANY DASHBOARD</p><h1>Hiring overview.</h1><p className="subtitle">Loading your company activity...</p></section>;
  const applications = (dashboard?.applications || []).reduce((sum, item) => sum + Number(item.count || 0), 0);
  return <section><p className="eyebrow">COMPANY DASHBOARD</p><h1>Hiring overview.</h1><p className="subtitle">A concise view of your company’s current activity.</p>{error && <div className="error-message">{error}</div>}
    <div className="company-stats"><div className="stat-card"><span>Open postings</span><strong>{dashboard?.jobs_count?.count ?? jobs.length}</strong></div><div className="stat-card"><span>Events</span><strong>{dashboard?.events_count?.count ?? events.length}</strong></div><div className="stat-card"><span>Total applications</span><strong>{applications}</strong></div></div>
    <div className="dashboard-grid"><div className="company-panel"><p className="eyebrow">RECENT POSTINGS</p>{jobs.length ? jobs.slice(0, 5).map((job) => <div className="posting-row" key={job.id}><div><h3>{job.title}</h3><p>{job.location} · {job.is_remote ? "Remote" : "On-site"}</p></div><span>{job.application_count ?? 0} applications</span></div>) : <p className="subtitle">No postings yet.</p>}</div>
      <div className="company-panel"><p className="eyebrow">UPCOMING EVENTS</p>{events.length ? events.slice(0, 5).map((event) => <div className="posting-row" key={event.id}><div><h3>{event.name}</h3><p>{String(event.event_date || "").slice(0, 10)} · {event.location || "Location not provided"}</p></div></div>) : <p className="subtitle">No events yet.</p>}</div></div>
    <div className="profile-actions"><NavLink className="primary-button inline-link" to="/company">Manage jobs and events</NavLink></div>
  </section>;
}

function StudentDashboard() {
  const [dashboard, setDashboard] = useState(null); const [saved, setSaved] = useState([]); const [applications, setApplications] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  useEffect(() => { Promise.all([getStudentDashboard(), getSavedItems(), getStudentApplications()]).then(([summary, savedItems, applicationRows]) => { setDashboard(summary); setSaved(Array.isArray(savedItems) ? savedItems : []); setApplications(Array.isArray(applicationRows) ? applicationRows : []); }).catch((requestError) => setError(requestError.message || "Unable to load your dashboard.")).finally(() => setLoading(false)); }, []);
  const savedJobs = saved.filter((item) => item.item_type === "job"); const savedEvents = saved.filter((item) => item.item_type === "event"); const applicationCount = applications.length || (dashboard?.applications || []).reduce((sum, item) => sum + Number(item.count || 0), 0);
  if (loading) return <section><p className="eyebrow">STUDENT DASHBOARD</p><h1>Welcome back.</h1><p className="subtitle">Loading your career workspace...</p></section>;
  return <section className="student-dashboard"><p className="eyebrow">STUDENT DASHBOARD</p><h1>Build your next opportunity.</h1><p className="subtitle">Search jobs, discover events, and connect with Pair 09 employers.</p>{error && <div className="error-message">{error}</div>}<div className="student-stats"><div className="stat-card"><span>Applications</span><strong>{applicationCount}</strong></div><div className="stat-card"><span>Saved jobs</span><strong>{savedJobs.length}</strong></div><div className="stat-card"><span>Saved events</span><strong>{savedEvents.length}</strong></div></div><div className="dashboard-grid student-dashboard-grid"><div className="company-panel student-dashboard-panel"><p className="eyebrow">RECENT APPLICATIONS</p>{applications.length === 0 ? <p className="subtitle">No applications yet. Explore jobs to get started.</p> : applications.slice(0, 5).map((application) => <div className="posting-row" key={application.id}><div><h3>{application.title}</h3><p>{application.company_name || "Company unavailable"} · Applied {String(application.applied_at || "").slice(0, 10)}</p></div><span>{application.status}</span></div>)}</div><div className="company-panel student-dashboard-panel"><p className="eyebrow">SAVED ITEMS</p>{saved.length === 0 ? <p className="subtitle">No saved jobs or events yet.</p> : saved.slice(0, 5).map((item) => <div className="posting-row" key={item.id}><div><h3>{item.details?.title || item.details?.name || "Saved opportunity"}</h3><p>{item.details?.company_name || item.details?.location || "Details available in Saved Items"}</p></div><span>{item.item_type}</span></div>)}<NavLink className="secondary-button inline-link" to="/saved">View saved items and applications</NavLink></div></div></section>;
}

function Protected({ user, children, role }) {
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to={user.role === "company" ? "/company" : "/"} replace />;
  return children;
}

export function RoleRedirect({ user }) {
  if (!isAuthenticatedUser(user)) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "company" ? "/company" : "/"} replace />;
}

function hasStoredAccessToken() {
  try {
    return Boolean(localStorage.getItem("access_token"));
  } catch {
    return false;
  }
}

function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(hasStoredAccessToken);
  const dispatch = useDispatch();
  useEffect(() => {
    const unauthorized = () => { logout(); setUser(null); dispatch(loggedOut()); };
    window.addEventListener("careerbridge:unauthorized", unauthorized);
    if (hasStoredAccessToken()) {
      getMe()
        .then((sessionUser) => {
          if (!isAuthenticatedUser(sessionUser)) throw new Error("Invalid session response.");
          setUser(sessionUser); dispatch(sessionSet(sessionUser));
        })
        .catch(() => { logout(); setUser(null); dispatch(loggedOut()); })
        .finally(() => setChecking(false));
    }
    return () => window.removeEventListener("careerbridge:unauthorized", unauthorized);
  }, [dispatch]);
  if (checking) return <main className="login-page"><div className="login-card"><p className="subtitle">Loading your session...</p></div></main>;
  return <BrowserRouter><Routes>
    <Route path="/login" element={user ? <Navigate to={user.role === "company" ? "/company" : "/"} replace /> : <LoginPage onLogin={(sessionUser) => { setUser(sessionUser); dispatch(sessionSet(sessionUser)); }} />} />
    <Route path="/register" element={user ? <Navigate to="/" replace /> : <RegisterPage />} />
    <Route path="*" element={<Protected user={user}><Layout user={user} onLogout={() => { logout(); setUser(null); dispatch(loggedOut()); }}><Routes>
      <Route path="/" element={<Dashboard user={user} />} />
      <Route path="/jobs" element={<Protected user={user} role="student"><JobsPage /></Protected>} />
      <Route path="/events" element={<Protected user={user} role="student"><EventsPage /></Protected>} />
      <Route path="/assistant" element={<Protected user={user} role="student"><AssistantPage /></Protected>} />
      <Route path="/company" element={<Protected user={user} role="company"><CompanyPage /></Protected>} />
      <Route path="/profile" element={<Protected user={user} role="student"><ProfilePage /></Protected>} />
      <Route path="/saved" element={<Protected user={user} role="student"><SavedItemsPage /></Protected>} />
      <Route path="*" element={<RoleRedirect user={user} />} />
    </Routes></Layout></Protected>} />
  </Routes></BrowserRouter>;
}

export default App;
