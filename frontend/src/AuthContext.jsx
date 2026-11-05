import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem("ts_token"));

  useEffect(() => {
    if (!localStorage.getItem("ts_token")) return;
    api.get("/auth/me").then((r) => setUser(r.data)).catch(() => localStorage.removeItem("ts_token")).finally(() => setLoading(false));
  }, []);

  const finish = (data) => { localStorage.setItem("ts_token", data.access_token); setUser(data.user); return data.user; };
  const login = async (email, password) => finish((await api.post("/auth/login", { email, password })).data);
  const register = async (body) => finish((await api.post("/auth/register", body)).data);
  const logout = () => { localStorage.removeItem("ts_token"); setUser(null); };
  const refresh = async () => setUser((await api.get("/auth/me")).data);

  return <Ctx.Provider value={{ user, loading, login, register, logout, refresh }}>{children}</Ctx.Provider>;
}
