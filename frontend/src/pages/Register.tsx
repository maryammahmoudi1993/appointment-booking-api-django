import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center bg-brand-50/40 px-4 py-12">
      <div className="w-full max-w-md rounded-2xl border border-brand-100 bg-white p-8 shadow-sm">
        <h2 className="font-display text-2xl font-bold text-brand-900">
          Create your account
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Join Bloom Studio to start booking appointments.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {error && (
            <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}
          {(["username", "email", "password", "password2"] as const).map(
            (field) => (
              <div key={field}>
                <label className="block text-sm font-medium capitalize text-gray-700">
                  {field === "password2" ? "Confirm Password" : field}
                </label>
                <input
                  type={field.includes("password") ? "password" : "text"}
                  name={field}
                  required
                  value={form[field]}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>
            )
          )}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
          >
            {submitting ? "Creating account..." : "Register"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-700 hover:text-brand-800">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
