import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BrandLogo from "../components/icons/BrandLogo";
import { Button } from "../components/ui/Button";

function extractLoginError(err: any): string {
  const status = err.response?.status;
  const detail = err.response?.data?.detail;
  if (status === 429) {
    return typeof detail === "string"
      ? detail
      : "Too many attempts — please wait a moment and try again.";
  }
  if (status === 401 || status === 400) {
    return "Invalid username or password.";
  }
  return typeof detail === "string"
    ? detail
    : "Something went wrong signing in. Please try again.";
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err: any) {
      setError(extractLoginError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-[calc(100vh-8rem)] items-center justify-center overflow-hidden bg-blush-gradient px-4 py-16">
      <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-champagne/15 blur-3xl" aria-hidden="true" />
      <div className="pointer-events-none absolute -bottom-20 -right-20 h-64 w-64 rounded-full bg-blush blur-3xl" aria-hidden="true" />

      <div className="relative w-full max-w-md rounded-3xl border border-champagne/20 bg-white p-8 shadow-[0_20px_45px_-20px_rgba(184,134,11,0.3)] sm:p-10">
        <BrandLogo size={44} className="mx-auto" />
        <h2 className="mt-5 text-center font-display text-2xl font-bold text-charcoal">
          Welcome back
        </h2>
        <p className="mt-1 text-center text-sm text-charcoal-light">
          Sign in to manage your bookings.
        </p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          {error && (
            <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">
              {error}
            </p>
          )}
          <div>
            <label htmlFor="login-username" className="block text-sm font-medium text-charcoal">
              Username
            </label>
            <input
              id="login-username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1.5 block w-full rounded-lg border border-champagne/30 bg-cream/40 px-3.5 py-2.5 text-charcoal shadow-sm focus:border-champagne focus:outline-none focus:ring-2 focus:ring-champagne/25"
            />
          </div>
          <div>
            <label htmlFor="login-password" className="block text-sm font-medium text-charcoal">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1.5 block w-full rounded-lg border border-champagne/30 bg-cream/40 px-3.5 py-2.5 text-charcoal shadow-sm focus:border-champagne focus:outline-none focus:ring-2 focus:ring-champagne/25"
            />
          </div>
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Signing in..." : "Sign In"}
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-charcoal-light">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="font-medium text-champagne-dark hover:text-champagne">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
