import { useState } from "react";

function ProfilePage() {
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);
    const [resumeName, setResumeName] = useState(
  "Rohini_Ramasheshu_Resume.pdf"
);

const [resumeMessage, setResumeMessage] = useState("");
  const [profile, setProfile] = useState({
    name: "Rohini Ramasheshu",
    email: "rohini@example.com",
    location: "San Jose, CA",
    program: "Master's in Computer Science",
    skills: ["Python", "React", "FastAPI", "Machine Learning"],
  });

  function updateField(field, value) {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));
  }
function handleResumeUpload(event) {
  const file = event.target.files[0];

  if (!file) {
    return;
  }

  if (file.type !== "application/pdf") {
    setResumeMessage("Please upload a PDF resume.");
    return;
  }

  setResumeName(file.name);
  setResumeMessage(`${file.name} selected successfully.`);
}

  function saveProfile(event) {
    event.preventDefault();
    setEditing(false);
    setSaved(true);
  }

  return (
    <section>
      <p className="eyebrow">MY PROFILE</p>
      <h1>Student Profile</h1>
      <p className="subtitle">
        Manage your information and professional details.
      </p>

      {saved && (
        <div className="success-message">
          Profile updated successfully.
          <button onClick={() => setSaved(false)}>Dismiss</button>
        </div>
      )}

      <div className="profile-layout">
        <div className="profile-card">
          <div className="profile-avatar">RR</div>
          <h2>{profile.name}</h2>
          <p>{profile.program}</p>
          <p>{profile.location}</p>

          <button
            className="primary-button"
            onClick={() => setEditing(true)}
          >
            Edit profile
          </button>
        </div>

        <div className="profile-card profile-details">
          <p className="eyebrow">PROFILE INFORMATION</p>

          {editing ? (
            <form className="profile-form" onSubmit={saveProfile}>
              <label>
                Full name
                <input
                  value={profile.name}
                  onChange={(event) =>
                    updateField("name", event.target.value)
                  }
                />
              </label>

              <label>
                Email
                <input
                  type="email"
                  value={profile.email}
                  onChange={(event) =>
                    updateField("email", event.target.value)
                  }
                />
              </label>

              <label>
                Location
                <input
                  value={profile.location}
                  onChange={(event) =>
                    updateField("location", event.target.value)
                  }
                />
              </label>

              <label>
                Program
                <input
                  value={profile.program}
                  onChange={(event) =>
                    updateField("program", event.target.value)
                  }
                />
              </label>

              <div className="profile-actions">
                <button className="primary-button" type="submit">
                  Save changes
                </button>

                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="details-list">
              <div>
                <span>Email</span>
                <strong>{profile.email}</strong>
              </div>

              <div>
                <span>Location</span>
                <strong>{profile.location}</strong>
              </div>

              <div>
                <span>Program</span>
                <strong>{profile.program}</strong>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="profile-card resume-card">
        <p className="eyebrow">RESUME</p>
        <h2>{resumeName}</h2>
<p>Uploaded resume · Updated recently</p>

<input
  id="resume-upload"
  type="file"
  accept=".pdf,application/pdf"
  onChange={handleResumeUpload}
  hidden
/>

<label htmlFor="resume-upload" className="secondary-button upload-label">
  Upload new resume
</label>

{resumeMessage && (
  <p className="upload-message">{resumeMessage}</p>
)}
      </div>

      <div className="profile-card">
        <p className="eyebrow">SKILLS</p>
        <div className="skill-list">
          {profile.skills.map((skill) => (
            <span key={skill}>{skill}</span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ProfilePage;