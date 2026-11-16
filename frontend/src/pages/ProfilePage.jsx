import { useEffect, useState } from "react";
import { getStudentProfile, listResumes, updateStudentProfile, uploadResume } from "../services/api.js";

const emptyProfile = { name: "", email: "", city: "", state: "", country: "", career_objective: "", college: "", degree: "", major: "", graduation_year: "", cgpa: "", experience: "", phone: "", date_of_birth: "" };
const MAX_RESUME_SIZE = 5 * 1024 * 1024;

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ProfilePage() {
  const [profile, setProfile] = useState(emptyProfile);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [resumeName, setResumeName] = useState("");
  const [selectedResume, setSelectedResume] = useState(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [resumeMessage, setResumeMessage] = useState("");

  useEffect(() => {
    Promise.all([getStudentProfile(), listResumes()]).then(([data, resumes]) => {
      setProfile({ ...emptyProfile, ...data, date_of_birth: data.date_of_birth || "" });
      setResumeName(resumes?.[0]?.filename || resumes?.[0]?.name || "");
    }).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, []);
  const update = (field, value) => setProfile((current) => ({ ...current, [field]: value }));
  async function save(event) {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    const payload = { ...profile, graduation_year: profile.graduation_year ? Number(profile.graduation_year) : null, cgpa: profile.cgpa ? Number(profile.cgpa) : null, date_of_birth: profile.date_of_birth || null };
    delete payload.email;
    try { await updateStudentProfile(payload); const fresh = await getStudentProfile(); setProfile({ ...emptyProfile, ...fresh, date_of_birth: fresh.date_of_birth || "" }); setEditing(false); setMessage("Profile updated successfully."); }
    catch (requestError) { setError(requestError.message); } finally { setSaving(false); }
  }
  async function handleResume(event) {
    const file = event.target.files[0];
    event.target.value = "";
    if (!file) return;
    setResumeMessage("");
    setSelectedResume({ name: file.name, size: file.size });
    if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
      setResumeMessage("Please choose a PDF resume.");
      return;
    }
    if (file.size > MAX_RESUME_SIZE) {
      setResumeMessage("Resume must be 5 MB or smaller.");
      return;
    }
    setResumeUploading(true);
    setResumeMessage("Uploading resume...");
    try {
      await uploadResume(file);
      const resumes = await listResumes();
      const latest = resumes?.[0];
      setResumeName(latest?.filename || file.name);
      setSelectedResume(null);
      setResumeMessage(`${latest?.filename || file.name} uploaded successfully.`);
    } catch (requestError) {
      setResumeMessage(`Upload failed: ${requestError.message}`);
    } finally {
      setResumeUploading(false);
    }
  }
  if (loading) return <section><p className="subtitle">Loading profile...</p></section>;
  return <section><p className="eyebrow">MY PROFILE</p><h1>Student Profile</h1><p className="subtitle">Manage your information and professional details.</p>
    {message && <div className="success-message inline-message">{message}<button onClick={() => setMessage("")}>Dismiss</button></div>}
    {error && <div className="error-message">Profile request failed: {error}</div>}
    <div className="profile-layout"><div className="profile-card"><div className="profile-avatar">{(profile.name || "S").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase()}</div><h2>{profile.name}</h2><p>{profile.degree || profile.major || "Student"}</p><p>{[profile.city, profile.state].filter(Boolean).join(", ")}</p><button className="primary-button" onClick={() => setEditing(true)}>Edit profile</button></div>
      <div className="profile-card profile-details"><p className="eyebrow">PROFILE INFORMATION</p>{editing ? <form className="profile-form" onSubmit={save}>
        <label>Full name<input type="text" value={profile.name ?? ""} onChange={(event) => update("name", event.target.value)} required placeholder="Your name" /></label>
        {["date_of_birth", "city", "state", "country", "college", "degree", "major", "graduation_year", "cgpa", "phone"].map((field) => <label key={field}>{field.replaceAll("_", " ")}<input type={field === "date_of_birth" ? "date" : field === "graduation_year" || field === "cgpa" ? "number" : "text"} value={profile[field] ?? ""} onChange={(event) => update(field, event.target.value)} required={field === "college"} /></label>)}
        <label>Career objective<textarea value={profile.career_objective || ""} onChange={(event) => update("career_objective", event.target.value)} /></label><label>Experience<textarea value={profile.experience || ""} onChange={(event) => update("experience", event.target.value)} /></label>
        <div className="profile-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? "Saving..." : "Save changes"}</button><button className="secondary-button" type="button" onClick={() => setEditing(false)} disabled={saving}>Cancel</button></div>
      </form> : <div className="details-list">{[["Email", profile.email], ["Location", [profile.city, profile.state, profile.country].filter(Boolean).join(", ")], ["College", profile.college], ["Program", [profile.degree, profile.major].filter(Boolean).join(" · ")]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || "Not provided"}</strong></div>)}</div>}</div></div>
    <div className="profile-card resume-card"><p className="eyebrow">MY RESUME</p><h2>{resumeName || "No resume uploaded"}</h2><p id="resume-help">A PDF resume is required before you can apply for jobs. Maximum size: 5 MB.</p><input id="resume-upload" type="file" accept=".pdf,application/pdf" aria-describedby="resume-help" onChange={handleResume} disabled={resumeUploading} hidden /><label htmlFor="resume-upload" className={`secondary-button upload-label${resumeUploading ? " is-disabled" : ""}`}>{resumeUploading ? "Uploading..." : resumeName ? "Replace resume" : "Upload resume"}</label>{selectedResume && <p className="selected-file">Selected: {selectedResume.name} ({formatFileSize(selectedResume.size)})</p>}{resumeMessage && <p className="upload-message" role="status">{resumeMessage}</p>}</div>
  </section>;
}
export default ProfilePage;
