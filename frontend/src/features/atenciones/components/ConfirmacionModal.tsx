"use client";

import FocusTrap from "focus-trap-react";
import { Button } from "@/components/ui/Button";

interface Props {
  accion: "anular" | "finalizar";
  resumen: string;
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function ConfirmacionModal({ accion, resumen, open, onClose, onConfirm }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" role="dialog">
      <FocusTrap>
        <div className="w-full max-w-md rounded-card bg-white p-6 shadow-lg">
          <h3 className="text-lg font-semibold">Confirmar {accion}</h3>
          <p className="mt-2 text-sm text-serviplus-muted">{resumen}</p>
          <div className="mt-4 flex justify-end gap-2">
            <Button variant="ghost" onClick={onClose}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={onConfirm}>
              Confirmar
            </Button>
          </div>
        </div>
      </FocusTrap>
    </div>
  );
}
