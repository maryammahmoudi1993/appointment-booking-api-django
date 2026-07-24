import { beforeEach, describe, expect, it, vi } from "vitest";

const registeredResponseInterceptors: {
  fulfilled: (res: unknown) => unknown;
  rejected: (err: unknown) => unknown;
}[] = [];

vi.mock("axios", () => {
  const instance = {
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: {
        use: vi.fn((fulfilled: never, rejected: never) => {
          registeredResponseInterceptors.push({ fulfilled, rejected });
        }),
      },
    },
  };
  return {
    default: {
      create: vi.fn(() => instance),
      post: instance.post,
    },
  };
});

describe("api client 401 interceptor", () => {
  const originalLocation = window.location;

  beforeEach(async () => {
    localStorage.clear();
    registeredResponseInterceptors.length = 0;
    vi.resetModules();
    // Re-import so the interceptor registers fresh against our mock.
    await import("./client");
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { ...originalLocation, href: "" },
    });
  });

  function make401Error() {
    return {
      response: { status: 401 },
      config: { _retry: false, headers: {} },
    };
  }

  it("does not redirect an anonymous request with no tokens at all", async () => {
    const { rejected } = registeredResponseInterceptors[0];

    await rejected(make401Error()).catch(() => {});

    expect(window.location.href).toBe("");
  });

  it("redirects to /login when an access token existed but was rejected with no refresh token", async () => {
    localStorage.setItem("access_token", "stale-token");
    const { rejected } = registeredResponseInterceptors[0];

    await rejected(make401Error()).catch(() => {});

    expect(window.location.href).toBe("/login");
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});
