"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useCallback, useMemo, useState } from "react";

export function useFiltros() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [filtros, setFiltros] = useState<Record<string, string>>({});

  const buildQueryParams = useCallback(() => {
    const params: Record<string, string> = { ...filtros };
    searchParams.forEach((value, key) => {
      if (value) params[key] = value;
    });
    return params;
  }, [filtros, searchParams]);

  const persistToUrl = useCallback(
    (next: Record<string, string>) => {
      const qs = new URLSearchParams(next);
      router.replace(`${pathname}?${qs.toString()}`);
    },
    [pathname, router],
  );

  const onChange = useCallback(
    (key: string, value: string) => {
      setFiltros((prev) => {
        const next = { ...prev, [key]: value };
        persistToUrl(next);
        return next;
      });
    },
    [persistToUrl],
  );

  const reset = useCallback(() => {
    setFiltros({});
    router.replace(pathname);
  }, [pathname, router]);

  return { filtros, onChange, buildQueryParams, reset };
}
