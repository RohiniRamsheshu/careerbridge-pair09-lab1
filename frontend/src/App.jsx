import { BrowserRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import "./App.css";
import JobsPage from "./pages/JobsPage.jsx";
import AssistantPage from "./pages/AssistantPage.jsx";
import EventsPage from "./pages/EventsPage.jsx";
import CompanyPage from "./pages/CompanyPage.jsx";
import SafetyPage from "./pages/SafetyPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
function Layout({ children }) {
  const location = useLocation();
  const isCompany = location.pathname.startsWith("/company");

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>CareerBridge</h2>
        <p className="pair-label">PAIR 09</p>

        <nav>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/jobs">Jobs</NavLink>
          <NavLink to="/events">Events</NavLink>
          <NavLink to="/assistant">Assistant</NavLink>
          <NavLink to="/company">Company</NavLink>
          <NavLink to="/safety">Safety</NavLink>
          <NavLink to="/profile">Profile</NavLink>
        </nav>

        <div className="profile">
          <strong>Rohini Ramasheshu.</strong>
          <span>{isCompany ? "Company" : "Student"}</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span>{isCompany ? "Company Portal" : "Student Portal"}</span>
          <button className="logout-button">Log out</button>
        </header>

        {children}
      </main>
    </div>
  );
}

function Dashboard() {
  return (
    <section>
      <p className="eyebrow">WELCOME BACK</p>
      <h1>Build your next opportunity.</h1>
      <p className="subtitle">
        Search jobs, discover events, and connect with Pair 09 employers.
      </p>

      <div className="stats">
        <div className="stat-card">
          <span>Recommended Jobs</span>
          <strong>24</strong>
        </div>

        <div className="stat-card">
          <span>Applications</span>
          <strong>8</strong>
        </div>

        <div className="stat-card">
          <span>Saved Items</span>
          <strong>0</strong>
        </div>
      </div>

      <div className="welcome-card">
        <p className="eyebrow">PAIR 09 LOCATIONS</p>
        <h2>San Jose · Mountain View · Palo Alto</h2>
        <p>
          Explore opportunities and events across the local technology
          community.
        </p>
      </div>
    </section>
  );
}

function Jobs() {
  return (
    <section>
      <p className="eyebrow">OPPORTUNITIES</p>
      <h1>Explore Jobs</h1>
      <p className="subtitle">Search internships and job opportunities.</p>

      <input
        className="search-box"
        placeholder="Search by title, skill, or city"
      />

      <div className="empty-card">
        Job search results will appear here.
      </div>
    </section>
  );
}

function Events() {
  return (
    <section>
      <p className="eyebrow">COMMUNITY</p>
      <h1>Upcoming Events</h1>
      <p className="subtitle">
        Discover workshops, networking sessions, and employer events.
      </p>

      <div className="empty-card">
        Event listings will appear here.
      </div>
    </section>
  );
}

function Assistant() {
  return (
    <section>
      <p className="eyebrow">CUSTOM AI ASSISTANT</p>
      <h1>Opportunity Assistant</h1>
      <p className="subtitle">
        Ask questions about jobs and events.
      </p>

      <div className="chat-card">
        <div className="assistant-message">
          Hi Rohini! I can help you find jobs and events.
        </div>

        <div className="chat-input-row">
          <input placeholder="Ask about internships or events..." />
          <button>Send</button>
        </div>
      </div>
    </section>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<JobsPage />} />          
          <Route path="/events" element={<EventsPage />} />          
          <Route path="/assistant" element={<AssistantPage />} /> 
          <Route path="/company" element={<CompanyPage />} />
          <Route path="/safety" element={<SafetyPage />} />      
           <Route path="/profile" element={<ProfilePage />} />
           </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;