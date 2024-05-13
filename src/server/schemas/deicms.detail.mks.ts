import { z } from "zod";

// for number -> string
const xmlFix = z.union([z.string(), z.number().transform((num) => num.toString())]);

const componentSchema = z.object({
  evaluationId: z.string(),
  group: z.string(),
  rule: z.string(),
  idType: z.string(),
  displayType: z.string(),
  maximumMarks: z.number(),
  evaluationIdName: z.string(),
  componentType: z.string(),
});

const componentListSchema = z.object({
  component: z.array(componentSchema),
});

export const welcome2Schema = z.object({
  ComponentList: componentListSchema,
});

export enum Attendence {
  Abs = "ABS",
  P = "P",
}

export enum EvaluationID {
  E02 = "E02",
  E03 = "E03",
  E04 = "E04",
  E05 = "E05",
  E06 = "E06",
  E07 = "E07",
}

export enum InternalGrade {
  X = "X",
}

const attendenceSchema = z.nativeEnum(Attendence);

const evaluationIDSchema = z.string();

const internalGradeSchema = z.string();

const marksDetailSchema = z.object({
  rollNumber: z.number(),
  evaluationId: evaluationIDSchema,
  attendence: attendenceSchema,
  marks: z.number(),
  grades: z.string(),
  passFail: z.string(),
  totalInternal: z.number(),
  totalExternal: z.string(),
  totalMarks: xmlFix,
  internalGrade: internalGradeSchema,
  externalGrade: z.string(),
  externalPublishFlag: z.string(),
  highestCrsMarks: z.number(),
  averageCrsMarks: z.number(),
});

const detailsSchema = z.object({
  marksDetail: z.array(marksDetailSchema),
});

export const welcome1Schema = z.object({
  Details: detailsSchema,
});
