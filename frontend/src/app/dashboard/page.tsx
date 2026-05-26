"use client";

import Link from "next/link";
import { getRol } from "@/lib/auth";
import { Rol } from "@/types/atencion.types";

export default function DashboardPage() {
  const rol = getRol();

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Dashboard</h2>
      <p className="mb-4 text-serviplus-muted">Rol: {rol ?? "—"}</p>
      <nav className="flex gap-4">
        <Link href="/mis-atenciones" className="text-serviplus-primary underline">
          Mis atenciones
        </Link>
        {rol === Rol.COORDINADOR && (
          <Link href="/coordinador" className="text-serviplus-primary underline">
            Panel coordinador
          </Link>
        )}
      </nav>
    </section>
  );
}
