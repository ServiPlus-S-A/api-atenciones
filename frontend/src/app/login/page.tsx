"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const base = process.env.NEXT_PUBLIC_API_URL?.replace("/api", "") ?? "http://localhost:8000";
    const { data } = await axios.post(`${base}/api/auth/token/`, { username, password });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    router.push("/dashboard");
  };

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-sm space-y-4 rounded-card border bg-white p-6">
      <h2 className="text-xl font-semibold">Iniciar sesión</h2>
      <label className="block">
        <span className="text-sm">Usuario</span>
        <input
          aria-label="Usuario"
          className="mt-1 w-full rounded border px-3 py-2"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </label>
      <label className="block">
        <span className="text-sm">Contraseña</span>
        <input
          type="password"
          aria-label="Contraseña"
          className="mt-1 w-full rounded border px-3 py-2"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      <Button type="submit">Ingresar</Button>
    </form>
  );
}
