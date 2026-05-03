import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type BadgeProps = ComponentPropsWithoutRef<"span"> & {
  readonly variant?:
    | "default"
    | "secondary"
    | "success"
    | "warning"
    | "destructive"
    | "outline";
};

const variantClass: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default: "border-transparent bg-slate-900 text-white",
  secondary: "border-transparent bg-slate-100 text-slate-900",
  success: "border-transparent bg-emerald-100 text-emerald-900",
  warning: "border-transparent bg-amber-100 text-amber-900",
  destructive: "border-transparent bg-red-100 text-red-900",
  outline: "border border-slate-300 bg-transparent text-slate-900",
};

export const Badge = ({
  className,
  variant = "default",
  ...props
}: BadgeProps) => (
  <span
    className={cn(
      "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
      variantClass[variant],
      className,
    )}
    {...props}
  />
);
