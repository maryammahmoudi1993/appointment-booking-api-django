// Pings the API's liveness endpoint until it responds, so a cold Render
// instance (free plan spins down after 15 min idle) has time to wake up
// while the visitor is still looking at the static landing page.
const API_ORIGIN = import.meta.env.VITE_API_BASE_URL || "";

const delay = (milliseconds: number): Promise<void> =>
  new Promise((resolve) => window.setTimeout(resolve, milliseconds));

let activeWarmup: Promise<boolean> | null = null;

async function pollBackend(): Promise<boolean> {
  const maxAttempts = 20;
  const retryDelayMs = 4_000;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const response = await fetch(
        `${API_ORIGIN}/api/health/live/?t=${Date.now()}`,
        {
          method: "GET",
          cache: "no-store",
          credentials: "omit",
          headers: { Accept: "application/json" },
        }
      );

      if (response.ok) {
        return true;
      }
    } catch {
      // Backend likely still starting up; retry.
    }

    if (attempt < maxAttempts) {
      await delay(retryDelayMs);
    }
  }

  return false;
}

export function warmBackend(): Promise<boolean> {
  if (!activeWarmup) {
    activeWarmup = pollBackend().finally(() => {
      activeWarmup = null;
    });
  }

  return activeWarmup;
}
