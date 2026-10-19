import { useEffect, useMemo, useState } from "react";
import { getJobs, createSavedItem } from "../services/api.js";


function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("All");
  const [mode, setMode] = useState("All");
  const [selectedJob, setSelectedJob] = useState(null);
  const [appliedJob, setAppliedJob] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);

  useEffect(() => {
    async function loadJobs() {
      try {
        setLoading(true);
        setError("");

        const data = await getJobs();

        const normalizedJobs = (Array.isArray(data) ? data : []).map(
          (job) => ({
            ...job,
            company: job.company_name || "Unknown company",
            mode: job.is_remote ? "Remote" : "On-site",
            type: job.category || "Opportunity",
            skills: job.skills || [],
          })
        );

        setJobs(normalizedJobs);
      } catch (requestError) {
        setError(requestError.message || "Unable to load jobs.");
      } finally {
        setLoading(false);
      }
    }

    loadJobs();
  }, []);
const filteredJobs = useMemo(() => {
  return jobs.filter((job) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      job.title.toLowerCase().includes(searchText) ||
      job.company.toLowerCase().includes(searchText) ||
      job.skills.join(" ").toLowerCase().includes(searchText);

    const matchesLocation =
      location === "All" || job.location === location;

    const matchesMode =
      mode === "All" || job.mode === mode;

    return matchesSearch && matchesLocation && matchesMode;
  });
}, [jobs, search, location, mode]);
 async function saveJob(job) {
  if (savedJobs.includes(job.id)) {
    return;
  }

  const confirmed = window.confirm(
    `Do you want to save "${job.title}" to your profile?`
  );

  if (!confirmed) {
    return;
  }

  try {
    await createSavedItem("job", job.id);

    setSavedJobs((current) => [...current, job.id]);
  } catch (error) {
    window.alert(`Could not save job: ${error.message}`);
  }
}

  function applyToJob(job) {
    setAppliedJob(job);
    setSelectedJob(null);
  }

  return (
    <section>
      <p className="eyebrow">OPPORTUNITIES</p>
      <h1>Explore Jobs</h1>
      <p className="subtitle">
        Find internships and opportunities in the Pair 09 region.
      </p>

      <div className="job-filters">
        <input
          className="search-box"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by title, company, or skill"
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

        <select
          value={mode}
          onChange={(event) => setMode(event.target.value)}
        >
          <option value="All">All work modes</option>
          <option value="Remote">Remote</option>
          <option value="Hybrid">Hybrid</option>
          <option value="On-site">On-site</option>
        </select>
      </div>

    {loading && <p className="subtitle">Loading jobs...</p>}

{error && <div className="error-message">{error}</div>}

      <p className="result-count">
        {filteredJobs.length} opportunity
        {filteredJobs.length === 1 ? "" : "ies"} found
      </p>

      <div className="job-list">
        {filteredJobs.map((job) => (
          <article className="job-card" key={job.id}>
            <div className="job-card-header">
              <div>
                <h2>{job.title}</h2>
                <p className="job-company">
                  {job.company} · {job.location}
                </p>
              </div>

              <span className="job-mode">{job.mode}</span>
            </div>

            <p>{job.description}</p>

            <div className="skill-list">
              {job.skills.map((skill) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>

            <div className="job-actions">
              <button
                className="secondary-button"
                onClick={() => setSelectedJob(job)}
              >
                View details
              </button>

              <button
                className={
                  savedJobs.includes(job.id)
                    ? "saved-button"
                    : "secondary-button"
                }
                onClick={() => saveJob(job)}
              >
                {savedJobs.includes(job.id) ? "Saved" : "Save job"}
              </button>
            </div>
          </article>
        ))}
      </div>

      {filteredJobs.length === 0 && (
        <div className="empty-card">
          No jobs match your current search filters.
        </div>
      )}

      {selectedJob && (
        <div className="modal-overlay">
          <div className="job-modal">
            <button
              className="close-button"
              onClick={() => setSelectedJob(null)}
            >
              ×
            </button>

            <p className="eyebrow">JOB DETAILS</p>
            <h2>{selectedJob.title}</h2>
            <p className="job-company">
              {selectedJob.company} · {selectedJob.location}
            </p>

            <p>{selectedJob.description}</p>

            <h3>Required skills</h3>
            <div className="skill-list">
              {selectedJob.skills.map((skill) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>

            <button
              className="primary-button"
              onClick={() => applyToJob(selectedJob)}
            >
              Apply now
            </button>
          </div>
        </div>
      )}

      {appliedJob && (
        <div className="success-message">
          Application started for <strong>{appliedJob.title}</strong>.
          <button onClick={() => setAppliedJob(null)}>Dismiss</button>
        </div>
      )}
    </section>
  );
}

export default JobsPage;