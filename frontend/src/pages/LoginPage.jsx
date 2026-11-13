import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api.js";

function LoginPage({ onLogin }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await login(email, password);
      onLogin(data.user);
      navigate(data.user.role === "company" ? "/company" : "/");
    } catch (loginError) {
      setError(
        loginError.message || "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
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

        {error && <div className="error-message">{error}</div>}

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

          <button
            className="primary-button"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="auth-link"><a href="/register">Need an account? Register</a></p>
      </div>
    </main>
  );
}

export default LoginPage;
