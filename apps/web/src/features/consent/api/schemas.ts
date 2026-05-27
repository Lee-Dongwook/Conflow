import { z } from 'zod'

export const ConsentType = z.enum(['terms', 'privacy', 'third_party', 'marketing'])
export type ConsentType = z.infer<typeof ConsentType>

export const ConsentReadSchema = z.object({
  uuid: z.string(),
  userUuid: z.string(),
  consentType: ConsentType,
  version: z.string(),
  acceptedAt: z.string(),
  revokedAt: z.string().nullable(),
})
export type ConsentRead = z.infer<typeof ConsentReadSchema>

export const ConsentStatusReadSchema = z.object({
  terms: ConsentReadSchema.nullable(),
  privacy: ConsentReadSchema.nullable(),
  thirdParty: ConsentReadSchema.nullable(),
  marketing: ConsentReadSchema.nullable(),
  allRequiredAccepted: z.boolean(),
})
export type ConsentStatusRead = z.infer<typeof ConsentStatusReadSchema>

export const ConsentAcceptSchema = z.object({
  consentType: ConsentType,
  version: z.string(),
})
export type ConsentAccept = z.infer<typeof ConsentAcceptSchema>

export const ConsentBatchAcceptSchema = z.object({
  consents: z.array(ConsentAcceptSchema),
})
export type ConsentBatchAccept = z.infer<typeof ConsentBatchAcceptSchema>
