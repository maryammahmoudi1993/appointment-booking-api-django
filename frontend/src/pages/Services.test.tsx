import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { servicesApi } from "../api/client";
import Services from "./Services";

vi.mock("../api/client", () => ({
  servicesApi: {
    list: vi.fn(),
  },
}));

const services = [
  {
    id: 1,
    name: "Hair styling",
    description: "Cut and style",
    duration_minutes: 60,
    price: "75.00",
    is_active: true,
  },
  {
    id: 2,
    name: "Hydrating facial",
    description: "Skin treatment",
    duration_minutes: 45,
    price: "65.00",
    is_active: true,
  },
];

describe("Services", () => {
  beforeEach(() => {
    vi.mocked(servicesApi.list).mockReset();
    vi.mocked(servicesApi.list).mockResolvedValue({
      data: { count: services.length, next: null, previous: null, results: services },
    } as never);
  });

  it("honors category links from the landing page", async () => {
    render(
      <MemoryRouter initialEntries={["/services?category=hair"]}>
        <Services />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Hair styling")).toBeInTheDocument();
    expect(screen.queryByText("Hydrating facial")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /hair/i })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("shows a recoverable API error and retries", async () => {
    vi.mocked(servicesApi.list)
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce({
        data: { count: services.length, next: null, previous: null, results: services },
      } as never);
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <Services />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We couldn’t load our service menu",
    );
    await user.click(screen.getByRole("button", { name: "Try again" }));

    await waitFor(() => {
      expect(screen.getByText("Hair styling")).toBeInTheDocument();
    });
    expect(servicesApi.list).toHaveBeenCalledTimes(2);
  });
});
