import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type SkeletonProps = ComponentPropsWithoutRef<"div">;

/** Decorative loading placeholder; pair with live regions or labels in the parent widget. */
export const Skeleton = ({ className, ...props }: SkeletonProps) => (
  <div
    role="presentation"
    className={cn("animate-pulse rounded-md bg-slate-200", className)}
    {...props}
  />
);
