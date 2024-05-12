import { z } from "zod"

const loginInfoLoginInfoSchema = z.object({
  universityId: z.number(),
  universityName: z.string(),
  userId: z.string(),
  userName: z.union([z.string(), z.number().transform(num => num.toString())]),
  userGroupId: z.string(),
  userGroupName: z.string(),
  startDate: z.string(),
  endDate: z.string(),
  status: z.string(),
  dummyFlagOne: z.string(),
  value: z.string(),
  componentCode: z.string(),
  password: z.string(),
  newPassword: z.string(),
  OldPassword: z.string(),
  lastLogin: z.string(),
  maxLogins: z.number(),
  token: z.string()
})

const welcome5LoginInfoSchema = z.object({
  loginInfo: loginInfoLoginInfoSchema
})

export const welcome5Schema = z.object({
  loginInfo: welcome5LoginInfoSchema
})

