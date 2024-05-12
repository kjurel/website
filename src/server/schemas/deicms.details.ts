import { z } from "zod"

const courseSchema = z.object({
  courseName: z.string(),
  courseCode: z.string(),
  semesterStartDate: z.string(),
  semesterEndDate: z.string(),
  courseStatus: z.string(),
  studentStatus: z.string(),
  attemptNumber: z.string()
})

const exceptionSchema = z.object({
  message: z.string()
})

const marksSchema = z.object({
  studentLeft: z.string(),
  markSavedDate: z.string(),
  displayStartDate: z.string(),
  displayEndDate: z.string(),
  semesterName: z.string(),
  evaluationId: z.string(),
  mark: z.string(),
  status: z.string(),
  semesterStartDate: z.string(),
  semesterEndDate: z.string(),
  totalInternal: z.string(),
  totalExternal: z.string(),
  totalMarks: z.string(),
  internalGrade: z.string(),
  externalGrade: z.string(),
  finalGradePoint: z.string(),
  displayType: z.string(),
  evaluationIdName: z.string()
})

const rollNumberSchema = z.object({
  rollNo: z.number(),
  programId: z.number(),
  programName: z.string(),
  branchId: z.string(),
  branchName: z.string(),
  specializationId: z.number(),
  specialization: z.string()
})

const semesterSchema = z.object({
  programCourseKey: z.string(),
  semesterCode: z.string(),
  semesterName: z.string(),
  semesterStartDate: z.string(),
  semesterEndDate: z.string(),
  name: z.string()
})

const semesterSummarySchema = z.object({
  semesterStartDate: z.string(),
  semesterEndDate: z.string(),
  sgpa: z.string(),
  cgpa: z.string(),
  theoryCgpa: z.string(),
  theorySgpa: z.string(),
  practicalCgpa: z.string(),
  practicalSgpa: z.string()
})

const studentMarksSummarySchema = z.object({
  rollNumber: rollNumberSchema,
  course: courseSchema,
  marks: marksSchema,
  semester: semesterSchema,
  exception: exceptionSchema,
  semesterSummary: semesterSummarySchema
})

export const welcome4Schema = z.object({
  StudentMarksSummary: studentMarksSummarySchema
})


