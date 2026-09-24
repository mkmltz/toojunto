import { describe, expect, it } from "vitest";

import { DEVELOPMENT_API_URL, resolveApiUrl } from "./api-url";


describe("resolveApiUrl", () => {
  it("preserva a API local como fallback exclusivo de development", () => {
    expect(resolveApiUrl({ development: true })).toBe(DEVELOPMENT_API_URL);
  });

  it("respeita VITE_API_URL explícita", () => {
    expect(resolveApiUrl({ configuredUrl: "https://api.example", development: true }))
      .toBe("https://api.example");
  });

  it("aceita /api em production", () => {
    expect(resolveApiUrl({ configuredUrl: "/api", development: false })).toBe("/api");
  });

  it("impede fallback e endereços locais em production", () => {
    expect(() => resolveApiUrl({ development: false })).toThrow(
      "VITE_API_URL is required for a production build",
    );
    expect(() => resolveApiUrl({ configuredUrl: "http://127.0.0.1:8000", development: false }))
      .toThrow("VITE_API_URL cannot point to localhost");
    expect(() => resolveApiUrl({ configuredUrl: "http://localhost:8000", development: false }))
      .toThrow("VITE_API_URL cannot point to localhost");
  });
});
