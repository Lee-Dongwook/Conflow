import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type SpinnerProps = ComponentPropsWithoutRef<"svg"> & {
  readonly size?: "sm" | "md";
};

const sizePx: Record<NonNullable<SpinnerProps["size"]>, number> = {
  sm: 16,
  md: 24,
};

/** Inline loading indicator; pair with `aria-busy` / live regions on the parent when blocking UI. */
export const Spinner = ({ className, size = "md", ...props }: SpinnerProps) => {
  const px = sizePx[size];
  return (
    <svg
      role="status"
      aria-hidden="true"
      width={px}
      height={px}
      viewBox="0 0 24 24"
      fill="none"
      className={cn("animate-spin text-slate-900", className)}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};
