import { useState } from "react";
import { updateStudentProfile } from "../services/api.js";

function ProfilePage() {
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

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

  async function saveProfile(event) {
    event.preventDefault();

    setSavingProfile(true);
    setProfileError("");
    setSaved(false);

    const [city = "San Jose"] = profile.location.split(",");

    const profileData = {
      date_of_birth: "2002-05-15",
      city: city.trim(),
      state: "CA",
      country: "USA",
      career_objective: "Seeking a software engineering internship",
      college: "San Jose State University",
      degree: "MS",
      major: "Applied Data Intelligence",
      graduation_year: 2027,
      cgpa: 3.3,
      experience: "Student",
      phone: "4085550100",
    };

    try {
      await updateStudentProfile(profileData);

      setEditing(false);
      setSaved(true);
    } catch (error) {
      setProfileError(error.message);
    } finally {
      setSavingProfile(false);
    }
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

      {profileError && (
        <div className="error-message">
          Profile update failed: {profileError}
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
            onClick={() => {
              setEditing(true);
              setSaved(false);
              setProfileError("");
            }}
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
                  placeholder="San Jose, CA"
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
                <button
                  className="primary-button"
                  type="submit"
                  disabled={savingProfile}
                >
                  {savingProfile ? "Saving..." : "Save changes"}
                </button>

                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => {
                    setEditing(false);
                    setProfileError("");
                  }}
                  disabled={savingProfile}
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

        <label
          htmlFor="resume-upload"
          className="secondary-button upload-label"
        >
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