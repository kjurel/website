import { z } from "zod";

// for number -> string
const xmlFix = z.union([z.string(), z.number().transform((num) => num.toString())]);

export const courseDetailSchema = z.object({
  programId: xmlFix,
  programName: z.string(),
  entityId: xmlFix,
  entityName: z.string(),
  branchId: z.string(),
  branchName: z.string(),
  specializationId: xmlFix,
  specializationName: z.string(),
  semesterCode: z.string(),
  semesterName: xmlFix,
  semesterStartDate: z.string(),
  semesterEndDate: z.string(),
  courseCode: z.string(),
  courseName: z.string(),
  programCourseKey: xmlFix,
  externalFlag: z.string(),
});

const detailsSchema = z.object({
  courseDetail: z.array(courseDetailSchema),
});

export const welcome3Schema = z.object({
  Details: detailsSchema,
});
