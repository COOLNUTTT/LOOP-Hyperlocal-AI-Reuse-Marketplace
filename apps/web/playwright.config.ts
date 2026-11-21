// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/**
 * Playwright E2E Configuration (`apps/web/playwright.config.ts`).
 *
 * Enforces mobile-first 360px viewport verification (`AGENTS.md` §7) alongside desktop Chrome.
 */

export interface PlaywrightProjectConfig {
  name: string;
  use: {
    viewport: { width: number; height: number };
    isMobile: boolean;
  };
}

export interface PlaywrightConfig {
  testDir: string;
  timeout: number;
  retries: number;
  use: {
    baseURL: string;
    trace: "on-first-retry" | "off";
  };
  projects: PlaywrightProjectConfig[];
}

const config: PlaywrightConfig = {
  testDir: "./e2e",
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "mobile-360px",
      use: {
        viewport: { width: 360, height: 800 },
        isMobile: true,
      },
    },
    {
      name: "desktop-chromium",
      use: {
        viewport: { width: 1280, height: 800 },
        isMobile: false,
      },
    },
  ],
};

export default config;
