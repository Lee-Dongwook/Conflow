import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type LabelProps = ComponentPropsWithoutRef<"label">;

export const Label = ({ className, ...props }: LabelProps) => (
  <label
    className={cn(
      "text-sm font-medium leading-none text-slate-900 peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
      className,
    )}
    {...props}
  />
);
