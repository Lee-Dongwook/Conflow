import type { ComponentPropsWithoutRef } from "react";

import { cn } from "../cn";

export type CardProps = ComponentPropsWithoutRef<"div">;

export const Card = ({ className, ...props }: CardProps) => (
  <div
    className={cn(
      "rounded-lg border border-slate-200 bg-white text-slate-950 shadow-sm",
      className,
    )}
    {...props}
  />
);

export type CardHeaderProps = ComponentPropsWithoutRef<"div">;

export const CardHeader = ({ className, ...props }: CardHeaderProps) => (
  <div
    className={cn(
      "flex flex-col gap-1.5 border-b border-slate-100 p-4",
      className,
    )}
    {...props}
  />
);

export type CardTitleProps = ComponentPropsWithoutRef<"h3">;

export const CardTitle = ({ className, ...props }: CardTitleProps) => (
  <h3
    className={cn(
      "text-base font-semibold leading-none tracking-tight",
      className,
    )}
    {...props}
  />
);

export type CardDescriptionProps = ComponentPropsWithoutRef<"p">;

export const CardDescription = ({
  className,
  ...props
}: CardDescriptionProps) => (
  <p className={cn("text-sm text-slate-500", className)} {...props} />
);

export type CardContentProps = ComponentPropsWithoutRef<"div">;

export const CardContent = ({ className, ...props }: CardContentProps) => (
  <div className={cn("p-4", className)} {...props} />
);

export type CardFooterProps = ComponentPropsWithoutRef<"div">;

export const CardFooter = ({ className, ...props }: CardFooterProps) => (
  <div
    className={cn("flex items-center border-t border-slate-100 p-4", className)}
    {...props}
  />
);
