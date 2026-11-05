import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "/api";
const ORIGIN = BASE.startsWith("http") ? new URL(BASE).origin : "";

export const api = axios.create({ baseURL: BASE });

// Attach the JWT to every request.
api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("ts_token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

// Expired / invalid token -> back to login.
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && !err.config.url.includes("/auth/login")) {
      localStorage.removeItem("ts_token");
      if (!location.pathname.startsWith("/login")) location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const mediaUrl = (p) => (p ? ORIGIN + p : null);

export function errMsg(e) {
  const d = e.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join(", ");
  return e.message === "Network Error" ? "Cannot reach the server. Is the backend running?" : "Something went wrong.";
}
