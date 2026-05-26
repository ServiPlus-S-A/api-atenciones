"use client";

import { useNotificaciones } from "@/features/notificaciones/hooks/useNotificaciones";

export function NotificacionBell() {
  const { notificaciones, noLeidas, error } = useNotificaciones();

  return (
    <div className="relative" aria-live="polite">
      <button type="button" className="relative rounded p-2 hover:bg-gray-100" aria-label="Notificaciones">
        🔔
        {noLeidas > 0 && (
          <span className="absolute -right-1 -top-1 rounded-full bg-serviplus-danger px-1.5 text-xs text-white">
            {noLeidas}
          </span>
        )}
      </button>
      {error && <span className="sr-only">{error}</span>}
      <ul className="absolute right-0 mt-2 hidden w-64 rounded-card border bg-white shadow-lg group-hover:block">
        {notificaciones.slice(0, 5).map((n) => (
          <li key={n.id} className="border-b p-2 text-sm last:border-0">
            {n.mensaje}
          </li>
        ))}
      </ul>
    </div>
  );
}
