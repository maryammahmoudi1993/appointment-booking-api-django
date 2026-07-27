import { lazy, Suspense, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import PrivateRoute from "./components/PrivateRoute";
import Home from "./pages/Home";
import { warmBackend } from "./services/backendWarmup";

const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Services = lazy(() => import("./pages/Services"));
const ServiceDetails = lazy(() => import("./pages/ServiceDetails"));
const Staff = lazy(() => import("./pages/Staff"));
const BookAppointment = lazy(() => import("./pages/BookAppointment"));
const MyBookings = lazy(() => import("./pages/MyBookings"));
const Loyalty = lazy(() => import("./pages/Loyalty"));
const Reviews = lazy(() => import("./pages/Reviews"));
const Notifications = lazy(() => import("./pages/Notifications"));
const Profile = lazy(() => import("./pages/Profile"));
const Support = lazy(() => import("./pages/Support"));
const Legal = lazy(() => import("./pages/Legal"));
const CaseStudy = lazy(() => import("./pages/CaseStudy"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const NotFound = lazy(() => import("./pages/NotFound"));

function RouteLoading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8" role="status" aria-live="polite">
      <div className="beauty-skeleton h-[28rem] rounded-[32px]" />
      <span className="sr-only">Loading page…</span>
    </div>
  );
}

export default function App() {
  useEffect(() => {
    // Fire-and-forget: nudges a sleeping Render free-tier instance awake
    // as soon as the (statically hosted) landing page loads, so the API
    // has a head start before the visitor reaches an API-backed page.
    void warmBackend();
  }, []);

  return (
    <Suspense fallback={<RouteLoading />}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/services" element={<Services />} />
          <Route path="/services/:id" element={<ServiceDetails />} />
          <Route path="/staff" element={<Staff />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/privacy" element={<Legal />} />
          <Route path="/terms" element={<Legal />} />
          <Route path="/case-study" element={<CaseStudy />} />
          <Route path="/book" element={<PrivateRoute requiredRole="customer"><BookAppointment /></PrivateRoute>} />
          <Route path="/my-bookings" element={<PrivateRoute><MyBookings /></PrivateRoute>} />
          <Route path="/loyalty" element={<PrivateRoute requiredRole="customer"><Loyalty /></PrivateRoute>} />
          <Route path="/notifications" element={<PrivateRoute><Notifications /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/support" element={<PrivateRoute requiredRole="customer"><Support /></PrivateRoute>} />
          <Route path="/admin/*" element={<PrivateRoute requiredRole="admin"><AdminDashboard /></PrivateRoute>} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
