import { z } from "zod";

export const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_USE_MOCK: z
    .enum(["true", "false"])
    .default("true")
    .transform((value) => value === "true"),
});

export type Env = z.infer<typeof envSchema>;
