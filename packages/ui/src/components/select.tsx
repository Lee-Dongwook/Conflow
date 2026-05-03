import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type SelectProps = ComponentPropsWithoutRef<"select">;

export const Select = ({ className, children, ...props }: SelectProps) => (
  <select
    className={cn(
      "block w-full appearance-none rounded-md border border-slate-300 bg-white px-3 py-2 pr-8 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
      className,
    )}
    {...props}
  >
    {children}
  </select>
);
