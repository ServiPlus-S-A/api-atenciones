import type { Metadata } from "next";
import "./globals.css";
import { NotificacionBell } from "@/features/notificaciones/components/NotificacionBell";

export const metadata: Metadata = {
  title: "ServiPlus Atenciones",
  description: "Módulo de Atenciones — ServiPlus S.A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50 font-sans text-gray-900">
        <header className="flex items-center justify-between border-b bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-serviplus-primary">ServiPlus Atenciones</h1>
          <NotificacionBell />
        </header>
        <main className="mx-auto max-w-6xl p-6">{children}</main>
      </body>
    </html>
  );
}
