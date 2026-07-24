import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { copilotApi } from "../api/client";
import { useAuth } from "../context/AuthContext";
import ChatWidget from "./ChatWidget";

vi.mock("../api/client", () => ({
  copilotApi: {
    chat: vi.fn(),
  },
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: vi.fn(),
}));

describe("ChatWidget", () => {
  beforeEach(() => {
    vi.mocked(useAuth).mockReturnValue({ user: null } as never);
    vi.mocked(copilotApi.chat).mockReset();
  });

  it("does not call the protected API for anonymous visitors", async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: "Toggle AI assistant" }));
    await user.type(screen.getByPlaceholderText("Ask about our services..."), "Book a haircut");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(
      await screen.findByText(/Please sign in first so I can help/i),
    ).toBeInTheDocument();
    expect(copilotApi.chat).not.toHaveBeenCalled();
  });

  it("renders a grounded copilot reply for an authenticated customer", async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 1, username: "jane", role: "customer" },
    } as never);
    vi.mocked(copilotApi.chat).mockResolvedValue({
      data: {
        reply: "I found two available haircut times.",
        tool_calls_made: [{ tool: "find_available_slots", args: {} }],
      },
    } as never);
    const user = userEvent.setup();
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: "Toggle AI assistant" }));
    await user.type(screen.getByPlaceholderText("Ask about our services..."), "Find a haircut");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(
      await screen.findByText("I found two available haircut times."),
    ).toBeInTheDocument();
    expect(copilotApi.chat).toHaveBeenCalledWith({ message: "Find a haircut" });
  });
});
