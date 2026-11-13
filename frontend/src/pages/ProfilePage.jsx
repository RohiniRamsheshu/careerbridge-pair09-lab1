import { useEffect, useState } from "react";
import { getStudentProfile, listResumes, updateStudentProfile, uploadResume } from "../services/api.js";

const emptyProfile = { name: "", email: "", city: "", state: "", country: "", career_objective: "", college: "", degree: "", major: "", graduation_year: "", cgpa: "", experience: "", phone: "", date_of_birth: "" };

function ProfilePage() {
  const [profile, setProfile] = useState(emptyProfile);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [resumeName, setResumeName] = useState("");
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
    const file = event.target.files[0]; if (!file) return;
    if (file.type !== "application/pdf") { setResumeMessage("Please upload a PDF resume."); return; }
    setResumeMessage("Uploading resume...");
    try { await uploadResume(file); setResumeName(file.name); setResumeMessage(`${file.name} uploaded successfully.`); } catch (requestError) { setResumeMessage(`Upload failed: ${requestError.message}`); }
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
    <div className="profile-card resume-card"><p className="eyebrow">RESUME</p><h2>{resumeName || "No resume uploaded"}</h2><p>Upload a PDF resume for applications.</p><input id="resume-upload" type="file" accept=".pdf,application/pdf" onChange={handleResume} hidden /><label htmlFor="resume-upload" className="secondary-button upload-label">Upload new resume</label>{resumeMessage && <p className="upload-message">{resumeMessage}</p>}</div>
  </section>;
}
export default ProfilePage;
