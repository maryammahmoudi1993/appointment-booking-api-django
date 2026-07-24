import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import PrivateRoute from "./PrivateRoute";

const mockUseAuth = vi.fn();
vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

function renderWithRoute(requiredRole?: "admin" | "staff" | "customer") {
  return render(
    <MemoryRouter initialEntries={["/protected"]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/" element={<div>Home page</div>} />
        <Route
          path="/protected"
          element={
            <PrivateRoute requiredRole={requiredRole}>
              <div>Protected content</div>
            </PrivateRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe("PrivateRoute", () => {
  it("shows a loading spinner while auth state resolves", () => {
    mockUseAuth.mockReturnValue({ user: null, loading: true });
    renderWithRoute();
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
    expect(screen.queryByText("Login page")).not.toBeInTheDocument();
  });

  it("redirects to /login when there is no authenticated user", () => {
    mockUseAuth.mockReturnValue({ user: null, loading: false });
    renderWithRoute();
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("redirects to / when the user's role does not match requiredRole", () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: "customer" },
      loading: false,
    });
    renderWithRoute("admin");
    expect(screen.getByText("Home page")).toBeInTheDocument();
  });

  it("renders children when the user's role matches requiredRole", () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: "admin" },
      loading: false,
    });
    renderWithRoute("admin");
    expect(screen.getByText("Protected content")).toBeInTheDocument();
  });

  it("renders children when no requiredRole is set and any authenticated user is present", () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: "customer" },
      loading: false,
    });
    renderWithRoute();
    expect(screen.getByText("Protected content")).toBeInTheDocument();
  });
});
