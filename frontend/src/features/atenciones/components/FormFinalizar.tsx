"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";

interface Props {
  onSubmit: (notas: string) => void;
}

export function FormFinalizar({ onSubmit }: Props) {
  const [notas, setNotas] = useState("");
  const valid = notas.trim().length >= 20;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (valid) onSubmit(notas);
      }}
      className="space-y-3"
    >
      <label className="block">
        <span className="text-sm">Notas finales (mín. 20 caracteres)</span>
        <textarea
          className="mt-1 w-full rounded border p-2"
          rows={4}
          value={notas}
          onChange={(e) => setNotas(e.target.value)}
        />
        <span className="text-xs text-serviplus-muted">{notas.length}/2000</span>
      </label>
      <Button type="submit" disabled={!valid}>
        Finalizar
      </Button>
    </form>
  );
}
