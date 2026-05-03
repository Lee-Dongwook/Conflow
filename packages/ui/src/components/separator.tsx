import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type SeparatorProps = ComponentPropsWithoutRef<"div"> & {
  readonly orientation?: "horizontal" | "vertical";
};

export const Separator = ({
  className,
  orientation = "horizontal",
  ...props
}: SeparatorProps) => (
  <div
    role="separator"
    aria-orientation={orientation}
    className={cn(
      "shrink-0 bg-slate-200",
      orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
      className,
    )}
    {...props}
  />
);
