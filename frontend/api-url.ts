export const DEVELOPMENT_API_URL = "http://127.0.0.1:8000";

interface ApiUrlEnvironment {
  configuredUrl?: string;
  development: boolean;
}

const isLocalUrl = (value: string) =>
  /(^|\/\/)(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/i.test(value);

export function resolveApiUrl({ configuredUrl, development }: ApiUrlEnvironment): string {
  const value = configuredUrl?.trim().replace(/\/$/, "");

  if (value) {
    if (!development && isLocalUrl(value)) {
      throw new Error("VITE_API_URL cannot point to localhost in a production build");
    }
    return value;
  }

  if (development) return DEVELOPMENT_API_URL;

  throw new Error("VITE_API_URL is required for a production build");
}
