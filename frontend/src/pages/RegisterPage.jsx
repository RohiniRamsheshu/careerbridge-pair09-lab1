import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerAccount } from "../services/api.js";

function RegisterPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState("student");
  const [form, setForm] = useState({ name: "", email: "", password: "", college: "", company_name: "", location: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  async function submit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);
    const payload = { name: form.name, email: form.email, password: form.password, role };
    if (role === "student") payload.college = form.college;
    else { payload.company_name = form.company_name; payload.location = form.location; }
    try {
      await registerAccount(payload);
      setMessage("Account created. Sign in to continue.");
      setTimeout(() => navigate("/login"), 700);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  return <main className="login-page"><div className="login-card">
    <p className="eyebrow">PAIR 09 CAREERBRIDGE</p>
    <h1>Create account</h1>
    <p className="subtitle">Register as a student or company using the CareerBridge account service.</p>
    {error && <div className="error-message">{error}</div>}
    {message && <div className="success-message inline-message">{message}</div>}
    <form className="login-form" onSubmit={submit}>
      <label>{role === "company" ? "Contact person's full name" : "Student's full name"}<input value={form.name} onChange={(event) => update("name", event.target.value)} required />{role === "company" && <small className="field-help">This identifies the company representative for this account.</small>}</label>
      <label>Email<input type="email" value={form.email} onChange={(event) => update("email", event.target.value)} required /></label>
      <label>Password<input type="password" minLength="8" value={form.password} onChange={(event) => update("password", event.target.value)} required /></label>
      <label>Account type<select value={role} onChange={(event) => setRole(event.target.value)}><option value="student">Student</option><option value="company">Company</option></select></label>
      {role === "student" ? <label>College<input value={form.college} onChange={(event) => update("college", event.target.value)} required /></label> : <>
        <label>Company name<input value={form.company_name} onChange={(event) => update("company_name", event.target.value)} required /></label>
        <label>Company location<input value={form.location} onChange={(event) => update("location", event.target.value)} required /></label>
      </>}
      <button className="primary-button" type="submit" disabled={loading}>{loading ? "Creating account..." : "Create account"}</button>
    </form>
    <p className="auth-link"><Link to="/login">Already have an account? Sign in</Link></p>
  </div></main>;
}

export default RegisterPage;
