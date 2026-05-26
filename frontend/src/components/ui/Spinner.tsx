export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "h-4 w-4", md: "h-8 w-8", lg: "h-12 w-12" };
  return (
    <div
      role="status"
      aria-busy="true"
      aria-label="Cargando..."
      className={`animate-spin rounded-full border-2 border-gray-300 border-t-serviplus-primary ${sizes[size]}`}
    />
  );
}
