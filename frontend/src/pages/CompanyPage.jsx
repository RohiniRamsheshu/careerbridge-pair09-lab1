import { useState } from "react";

function CompanyPage() {
  const [showForm, setShowForm] = useState(false);
  const [posted, setPosted] = useState(false);

  function submitPosting(event) {
    event.preventDefault();
    setPosted(true);
    setShowForm(false);
  }

  return (
    <section>
      <p className="eyebrow">COMPANY WORKSPACE</p>
      <h1>Manage your hiring pipeline.</h1>
      <p className="subtitle">
        Publish opportunities and review applications from Pair 09 students.
      </p>

      <div className="company-stats">
        <div className="stat-card">
          <span>Open postings</span>
          <strong>12</strong>
        </div>

        <div className="stat-card">
          <span>Total applications</span>
          <strong>46</strong>
        </div>

        <div className="stat-card">
          <span>New applicants</span>
          <strong>8</strong>
        </div>
      </div>

      {posted && (
        <div className="success-message">
          Job posting created successfully.
          <button onClick={() => setPosted(false)}>Dismiss</button>
        </div>
      )}

      <div className="company-panel">
        <div>
          <p className="eyebrow">EMPLOYER ACTIONS</p>
          <h2>Build your talent pipeline</h2>
          <p>
            Create a new posting or review the students who have applied to
            your roles.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowForm(true)}
        >
          Create job posting
        </button>
      </div>

      <div className="company-panel">
        <p className="eyebrow">CURRENT POSTINGS</p>

        <div className="posting-row">
          <div>
            <h3>Data Engineering Intern</h3>
            <p>Mountain View · Hybrid</p>
          </div>
          <span>18 applications</span>
          <button className="secondary-button">View applications</button>
        </div>

        <div className="posting-row">
          <div>
            <h3>Frontend Software Intern</h3>
            <p>San Jose · Remote</p>
          </div>
          <span>11 applications</span>
          <button className="secondary-button">View applications</button>
        </div>
      </div>

      {showForm && (
        <div className="modal-overlay">
          <div className="job-modal">
            <button
              className="close-button"
              onClick={() => setShowForm(false)}
            >
              ×
            </button>

            <p className="eyebrow">NEW OPPORTUNITY</p>
            <h2>Create a job posting</h2>

            <form className="posting-form" onSubmit={submitPosting}>
              <label>
                Job title
                <input required placeholder="Example: Data Science Intern" />
              </label>

              <label>
                Location
                <select required defaultValue="">
                  <option value="" disabled>
                    Select location
                  </option>
                  <option>San Jose</option>
                  <option>Mountain View</option>
                  <option>Palo Alto</option>
                </select>
              </label>

              <label>
                Work mode
                <select required defaultValue="">
                  <option value="" disabled>
                    Select work mode
                  </option>
                  <option>Remote</option>
                  <option>Hybrid</option>
                  <option>On-site</option>
                </select>
              </label>

              <label>
                Description
                <textarea
                  required
                  rows="4"
                  placeholder="Describe the opportunity..."
                />
              </label>

              <button className="primary-button" type="submit">
                Publish posting
              </button>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

export default CompanyPage;