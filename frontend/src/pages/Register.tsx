import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BrandLogo from "../components/icons/BrandLogo";
import { Button } from "../components/ui/Button";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.password2) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await register(form);
      navigate("/");
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        Object.values(err.response?.data || {}).flat().join(", ") ||
        "Registration failed.";
      setError(msg);
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
          Create your account
        </h2>
        <p className="mt-1 text-center text-sm text-charcoal-light">
          Join Bloom Studio to start booking appointments.
        </p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          {error && (
            <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">
              {error}
            </p>
          )}
          {(["username", "email", "password", "password2"] as const).map(
            (field) => (
              <div key={field}>
                <label htmlFor={`register-${field}`} className="block text-sm font-medium capitalize text-charcoal">
                  {field === "password2" ? "Confirm Password" : field}
                </label>
                <input
                  id={`register-${field}`}
                  type={field.includes("password") ? "password" : "text"}
                  name={field}
                  required
                  value={form[field]}
                  onChange={handleChange}
                  className="mt-1.5 block w-full rounded-lg border border-champagne/30 bg-cream/40 px-3.5 py-2.5 text-charcoal shadow-sm focus:border-champagne focus:outline-none focus:ring-2 focus:ring-champagne/25"
                />
              </div>
            )
          )}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Creating account..." : "Register"}
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-charcoal-light">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-champagne-dark hover:text-champagne">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
