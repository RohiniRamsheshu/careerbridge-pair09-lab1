import { useEffect, useMemo, useRef, useState } from "react";
import { NavLink } from "react-router-dom";
import { useDispatch } from "react-redux";
import { loadApplications as loadApplicationsThunk, loadJobs as loadJobsThunk, loadSavedItems } from "../store/slices.js";
import {
  createSavedItem,
  deleteSavedItem,
  listResumes,
  applyToJob as submitApplication,
  getJob,
} from "../services/api.js";

function JobsPage() {
  const PAGE_SIZE = 50;
  const dispatch = useDispatch();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [searchField, setSearchField] = useState("title");
  const [location, setLocation] = useState("All");
  const [mode, setMode] = useState("All");
  const [category, setCategory] = useState("All");
  const [selectedJob, setSelectedJob] = useState(null);
  const [appliedJob, setAppliedJob] = useState(null);
const [savedJobs, setSavedJobs] = useState([]);
const [savedJobRecords, setSavedJobRecords] = useState({});
const [resumes, setResumes] = useState([]);
const [applicationError, setApplicationError] = useState("");
const [applications, setApplications] = useState([]);
const [applicationsError, setApplicationsError] = useState("");
const [applicationsLoading, setApplicationsLoading] = useState(true);
const [resumeRequired, setResumeRequired] = useState(false);
const [applicationStatus, setApplicationStatus] = useState("All");
const [detailsLoading, setDetailsLoading] = useState(false);
const [detailsError, setDetailsError] = useState("");
  const [page, setPage] = useState(0);
  const [totalJobs, setTotalJobs] = useState(0);
  const requestSequence = useRef(0);


useEffect(() => {
  async function loadSavedJobs() {
    try {
      const data = await dispatch(loadSavedItems()).unwrap();

      const jobRecords = data.filter(
        (item) => item.item_type === "job"
      );

      setSavedJobs(jobRecords.map((item) => item.item_id));

      setSavedJobRecords(
        Object.fromEntries(
          jobRecords.map((item) => [item.item_id, item.id])
        )
      );
    } catch (error) {
      console.error("Could not load saved jobs:", error);
    }
  }

  loadSavedJobs();
}, [dispatch]);
useEffect(() => {
  listResumes().then(setResumes).catch(() => setResumes([]));
}, []);
useEffect(() => {
  async function loadApplications() {
    setApplicationsLoading(true);
    setApplicationsError("");
    try { setApplications(await dispatch(loadApplicationsThunk()).unwrap()); }
    catch (requestError) { setApplicationsError(requestError.message || "Unable to load applications."); }
    finally { setApplicationsLoading(false); }
  }
  loadApplications();
  }, [dispatch]);
  useEffect(() => {
    async function loadJobs() {
      const requestId = ++requestSequence.current;
      try {
        setLoading(true);
        setError("");

        const filters = {
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
          include_total: true,
          ...(search.trim() && searchField === "title" ? { title: search.trim() } : {}),
          ...(search.trim() && searchField === "company" ? { company: search.trim() } : {}),
          ...(location !== "All" ? { city: location } : {}),
          ...(mode === "Remote" ? { remote: true } : mode === "On-site" ? { remote: false } : {}),
          ...(category !== "All" ? { category } : {}),
        };
        const result = await dispatch(loadJobsThunk(filters)).unwrap();
        const data = Array.isArray(result) ? result : result.items;
        if (requestId !== requestSequence.current) return;
        setTotalJobs(Array.isArray(result) ? data.length : (result.total ?? 0));

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
        if (requestId !== requestSequence.current) return;
        setError(requestError.message || "Unable to load jobs.");
      } finally {
        if (requestId === requestSequence.current) setLoading(false);
      }
    }

    loadJobs();
  }, [dispatch, search, searchField, location, mode, category, page]);
  useEffect(() => { setPage(0); }, [search, searchField, location, mode, category]);
const filteredJobs = useMemo(() => {
  return jobs.filter((job) => {
    return (category === "All" || job.category === category) &&
      (location === "All" || job.location.toLowerCase().includes(location.toLowerCase())) &&
      (mode === "All" || job.mode === mode);
  });
}, [jobs, category, location, mode]);
 async function saveJob(job) {
  const savedItemId = savedJobRecords[job.id];

  const confirmed = window.confirm(
    savedItemId
      ? `Remove "${job.title}" from your saved items?`
      : `Do you want to save "${job.title}" to your profile?`
  );

  if (!confirmed) {
    return;
  }

  try {
    if (savedItemId) {
      await deleteSavedItem(savedItemId);

      setSavedJobs((current) =>
        current.filter((id) => id !== job.id)
      );

      setSavedJobRecords((current) => {
        const updated = { ...current };
        delete updated[job.id];
        return updated;
      });
    } else {
      const savedItem = await createSavedItem("job", job.id);

      setSavedJobs((current) => [...current, job.id]);

      setSavedJobRecords((current) => ({
        ...current,
        [job.id]: savedItem.id,
      }));
    }
  } catch (error) {
    window.alert(`Could not update saved job: ${error.message}`);
  }
}






  async function openJobDetails(jobId) {
    setDetailsLoading(true);
    setDetailsError("");
    try { setSelectedJob(await getJob(jobId)); }
    catch (requestError) { setDetailsError(requestError.message || "Unable to load job details."); }
    finally { setDetailsLoading(false); }
  }
  async function applyToJob(job) {
    setApplicationError("");
    setResumeRequired(false);
    if (!resumes.length) {
      setApplicationError("Upload a PDF resume in your profile before applying.");
      setResumeRequired(true);
      return;
    }
    try {
      await submitApplication(job.id, resumes[0].resume_path);
      setAppliedJob(job);
      setSelectedJob(null);
      try { setApplications(await getStudentApplications()); }
      catch (requestError) { setApplicationsError(requestError.message || "Application submitted, but history could not be refreshed."); }
    } catch (requestError) {
      setApplicationError(requestError.message);
    }
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
          placeholder="Search by title or company"
        />

        <select value={searchField} onChange={(event) => setSearchField(event.target.value)} aria-label="Job search field">
          <option value="title">Title</option>
          <option value="company">Company</option>
        </select>

        <select
          value={location}
          onChange={(event) => setLocation(event.target.value)}
        >
          <option value="All">All locations</option>
          <option value="San Jose">San Jose</option>
          <option value="Mountain View">Mountain View</option>
          <option value="Palo Alto">Palo Alto</option>
        </select>

        <select value={category} onChange={(event) => setCategory(event.target.value)} aria-label="Job category">
          <option value="All">All categories</option>
          <option value="full time">Full time</option>
          <option value="part time">Part time</option>
          <option value="on campus">On campus</option>
          <option value="internship">Internship</option>
        </select>

        <select
          value={mode}
          onChange={(event) => setMode(event.target.value)}
        >
          <option value="All">All work modes</option>
          <option value="Remote">Remote</option>
          <option value="On-site">On-site</option>
        </select>
      </div>

    {loading && <p className="subtitle">Loading jobs...</p>}

{error && <div className="error-message">{error}</div>}
      {applicationError && <div className="error-message">Application failed: {applicationError}{resumeRequired && <NavLink className="inline-link" to="/profile">Go to Profile to upload a PDF resume</NavLink>}</div>}
      {detailsError && <div className="error-message">Job details failed: {detailsError}</div>}

      <p className="result-count">
        {totalJobs} matching opportunit{totalJobs === 1 ? "y" : "ies"} · Showing {totalJobs === 0 ? 0 : page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, totalJobs)} of {totalJobs}
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
                onClick={() => openJobDetails(job.id)}
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

      <div className="pagination-controls" aria-label="Job results pagination">
        <button className="secondary-button" type="button" onClick={() => setPage((current) => Math.max(0, current - 1))} disabled={page === 0 || loading}>Previous</button>
        <span>Page {page + 1} of {Math.max(1, Math.ceil(totalJobs / PAGE_SIZE))}</span>
        <button className="secondary-button" type="button" onClick={() => setPage((current) => current + 1)} disabled={loading || (page + 1) * PAGE_SIZE >= totalJobs}>Next</button>
      </div>

      {detailsLoading && <p className="subtitle">Loading job details...</p>}

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
              {selectedJob.company_name || selectedJob.company || "Unknown company"} · {selectedJob.location}
            </p>

            <p>{selectedJob.description}</p>

            <div className="details-list job-detail-list">
              <div><span>Deadline</span><strong>{String(selectedJob.deadline || "Not provided").slice(0, 10)}</strong></div>
              <div><span>Salary</span><strong>{selectedJob.salary == null ? "Not provided" : `$${selectedJob.salary}`}</strong></div>
              <div><span>Category</span><strong>{selectedJob.category || "Not provided"}</strong></div>
              <div><span>Company contact</span><strong>{selectedJob.contact_information || "Not provided"}</strong></div>
              {selectedJob.website && <div><span>Company website</span><strong>{selectedJob.website}</strong></div>}
            </div>

            {Array.isArray(selectedJob.skills) && selectedJob.skills.length > 0 && <><h3>Required skills</h3><div className="skill-list">{selectedJob.skills.map((skill) => <span key={skill}>{skill}</span>)}</div></>}

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

      <div className="company-panel application-history">
        <p className="eyebrow">MY APPLICATIONS</p>
        <select value={applicationStatus} onChange={(event) => setApplicationStatus(event.target.value)} aria-label="Application status filter">
          <option>All</option><option>Pending</option><option>Reviewed</option><option>Declined</option>
        </select>
        {applicationsLoading ? <p className="subtitle">Loading applications...</p> : applicationsError ? <div className="error-message">Application history failed: {applicationsError}</div> : applications.filter((application) => applicationStatus === "All" || application.status === applicationStatus).length === 0 ? <p className="subtitle">No applications match this status.</p> : applications.filter((application) => applicationStatus === "All" || application.status === applicationStatus).map((application) => <div className="posting-row" key={application.id}><div><h3>{application.title}</h3><p>{application.company_name} · Applied {String(application.applied_at || "").slice(0, 10)}</p></div><span>{application.status}</span></div>)}
      </div>
    </section>
  );
}

export default JobsPage;
