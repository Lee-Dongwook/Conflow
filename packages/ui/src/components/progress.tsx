import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type ProgressProps = Omit<
  ComponentPropsWithoutRef<"div">,
  "children"
> & {
  readonly value: number;
  readonly max?: number;
};

export const Progress = ({
  className,
  value,
  max = 100,
  ...props
}: ProgressProps) => {
  const safeMax = max <= 0 ? 1 : max;
  const ratio = Math.min(100, Math.max(0, (value / safeMax) * 100));
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={safeMax}
      aria-valuenow={value}
      className={cn(
        "h-2 w-full overflow-hidden rounded-full bg-slate-100",
        className,
      )}
      {...props}
    >
      <div
        className="h-full rounded-full bg-slate-900 transition-[width] duration-300 ease-out"
        style={{ width: `${String(ratio)}%` }}
      />
    </div>
  );
};
