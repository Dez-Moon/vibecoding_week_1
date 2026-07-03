import { defineConfig, devices } from "@playwright/test";
import path from "path";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://127.0.0.1:3100",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      // bash -lc so env vars (DATABASE_URL) are read and PATH includes .venv/bin.
      // Use a temp file so each playwright run gets a fresh database.
      command: `bash -lc 'rm -f /tmp/pm_e2e.db && cd ../backend && DATABASE_URL=sqlite:///tmp/pm_e2e.db SECRET_KEY=test-secret uv run uvicorn app.main:app --host 127.0.0.1 --port 8000'`,
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command:
        "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev -- --hostname 127.0.0.1 --port 3100",
      url: "http://127.0.0.1:3100",
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
