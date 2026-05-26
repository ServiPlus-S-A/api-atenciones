import { forwardRef, type ButtonHTMLAttributes } from "react";

type Variant = "primary" | "danger" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary: "bg-serviplus-primary text-white hover:opacity-90",
  danger: "bg-serviplus-danger text-white hover:opacity-90",
  ghost: "bg-transparent hover:bg-gray-100",
  outline: "border border-gray-300 hover:bg-gray-50",
};

const sizes: Record<Size, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2",
  lg: "px-6 py-3 text-lg",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", loading, disabled, children, className = "", ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      className={`rounded-card font-medium transition ${variants[variant]} ${sizes[size]} ${className} disabled:opacity-50`}
      {...props}
    >
      {loading ? "Cargando..." : children}
    </button>
  ),
);
Button.displayName = "Button";
