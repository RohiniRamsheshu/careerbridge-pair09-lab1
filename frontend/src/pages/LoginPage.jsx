import { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleLogin(event) {
    event.preventDefault();

    if (role === "company") {
      navigate("/company");
    } else {
      navigate("/");
    }
  }

  return (
    <main className="login-page">
      <div className="login-card">
        <p className="eyebrow">PAIR 09 CAREERBRIDGE</p>
        <h1>Welcome back</h1>
        <p className="subtitle">
          Sign in to continue to your career workspace.
        </p>

        <form className="login-form" onSubmit={handleLogin}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              required
            />
          </label>

          <label>
            Sign in as
            <select
              value={role}
              onChange={(event) => setRole(event.target.value)}
            >
              <option value="student">Student</option>
              <option value="company">Company</option>
            </select>
          </label>

          <button className="primary-button" type="submit">
            Sign in
          </button>
        </form>
      </div>
    </main>
  );
}

export default LoginPage;