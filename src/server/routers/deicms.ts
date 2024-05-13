import { welcome3Schema, courseDetailSchema } from "@server/schemas/deicms.detail.sem";
import { welcome1Schema, welcome2Schema } from "@server/schemas/deicms.detail.mks";
import { welcome5Schema } from "@server/schemas/deicms.login.ts";
import { welcome4Schema } from "@server/schemas/deicms.details";
import { router, publicProcedure } from "@server/trpc";
import { XMLParser } from "fast-xml-parser";
import fetch from "node-fetch";
import https from "https";
import { z } from "zod";

const sessionCookie = z.object({
  JSESSIONID: z.string(),
  Path: z.string(),
});

type sessionCookieType = z.infer<typeof sessionCookie>;

type deicmsState = {
  username: string | null;
  semesterName: string | null;
  semesterData: z.infer<typeof courseDetailSchema> | null;
  courseName: string | null;
};

let session: sessionCookieType;
const state: deicmsState = {
  username: null,
  semesterName: null,
  semesterData: null,
  courseName: null,
};

const fetchM = (
  url: string,
  params: { [key: string]: string },
  fromDashboard: boolean = false,
  attachSemesterParams: boolean = false,
  debug: boolean = false,
  cookieFalse: boolean = false
) => {
  const headers: { [key: string]: string } = {
    "Access-Control-Allow-Origin": "*",
    Accept: "application/json, text/plain, */*",
    Referer: !fromDashboard
      ? "http://admission.dei.ac.in:8085/cms_new/login"
      : "https://admission.dei.ac.in:8085/cms_new/dashboard/student_marks",
    Connection: "keep-alive",
  };
  if (session != undefined && !cookieFalse)
    headers["Cookie"] = `${encodeURIComponent("JSESSIONID")}=${encodeURIComponent(session.JSESSIONID)}`;
  debug && console.log(params);
  if (state.semesterName != null)
    params = {
      rollNumber: state.username!,
      semesterStartDate: state.semesterData!.semesterStartDate,
      semesterEndDate: state.semesterData!.semesterEndDate,
      semesterCode: state.semesterData!.semesterCode,
      programId: "000" + state.semesterData!.programId,
      branchId: state.semesterData!.branchId,
      specializationId: "0" + state.semesterData!.specializationId,
      programCourseKey: "000" + state.semesterData!.programCourseKey,
      entityId: "000" + state.semesterData!.entityId,
      universityId: "0001",
      ...params,
    };
  debug && console.log(params, headers);
  return fetch(
    `${url}?${new URLSearchParams({
      application: "CMS",
      ...params,
    }).toString()}`,
    {
      method: "GET",
      agent: new https.Agent({ rejectUnauthorized: false }), // Ignore SSL certificate errors
      headers: headers,
    }
  );
};

export const deicmsLoginRouter = router({
  login: publicProcedure
    .input(z.object({ username: z.string(), password: z.string() }))
    .query(async ({ ctx, input: { username, password } }) => {
      const [jsonD, data] = await fetchM("https://admission.dei.ac.in:8085/CMS/login/loginProcedureStart.htm", {
        angular_application: "ANG",
        requestFrom: "ANGULAR",
        userName: Buffer.from(username).toString("base64"),
        password: Buffer.from(password).toString("base64"),
      })
        .then((response) => {
          // Get the "Set-Cookie" header from the response headers
          console.log(session);
          if (response.headers.has("Set-Cookie"))
            session = sessionCookie.parse(
              Object.fromEntries(
                response.headers
                  .get("Set-Cookie")!
                  .split(";")
                  .map((cookie) => cookie.split("=").map((part) => decodeURIComponent(part.trim())))
              )
            );
          return response.text();
        })
        .then((txt) => {
          const jsonD = new XMLParser().parse(txt);
          return [jsonD, welcome5Schema.parse(jsonD)];
        });

      const currentDate = new Date();
      const dateString = [
        `${currentDate.toDateString()}`,
        `${currentDate.toTimeString().split(" ")[0]}`,
        `GMT${currentDate.toTimeString().split(" ")[5]}`,
        `${currentDate.toTimeString().split(" ")[6]}`,
      ].join(" ");

      await fetchM("https://admission.dei.ac.in:8085/CMS/login/getLoginDetails.htm", {
        angular_application: "ANG",
        requestFrom: "ANGULAR",
        maxLogins: "5",
        date: dateString,
        userName: Buffer.from(username).toString("base64"),
        password: Buffer.from(password).toString("base64"),
        userGroupId: data!.loginInfo.loginInfo.userGroupId,
      })
        .then((response) => response.text())
        .then((txt) => {
          const newJson = new XMLParser().parse(txt);

          interface NestedObject {
            [key: string]: string | NestedObject;
          }

          const updateObjectsInPlace = (obj1: NestedObject, obj2: NestedObject): void => {
            Object.entries(obj2).forEach(([key, value]) => {
              if (typeof value === "object" && typeof obj1[key] === "object") {
                updateObjectsInPlace(obj1[key] as NestedObject, value as NestedObject);
              } else if (value !== "") {
                obj1[key] = value;
              }
            });
          };
          updateObjectsInPlace(jsonD, newJson);
        });
      const rData = welcome5Schema.parse(jsonD);

      state.username = username;
      if (rData.loginInfo.loginInfo.userName == username) return { login: true, data: rData };
      return { login: false, data: rData };
    }),
  getStudentRollNumber: publicProcedure.query(async () => {
    const url = "https://admission.dei.ac.in:8085/CMS/studentMarksSummary/getStudentRollNumber.htm";
    const data = await fetchM(url, {}, true)
      .then((response) => response.text())
      .then((txt) => welcome4Schema.parse(new XMLParser().parse(txt)));
    return { data: data };
  }),
  getRegisteredSemesterCourseList: publicProcedure.input(z.number().gte(0).lte(8)).query(async ({ input }) => {
    const semData = await fetchM(
      "https://admission.dei.ac.in:8085/CMS/marksInfo/getRegisteredSemesterList.htm",
      { rollNumber: state.username! },
      true
    )
      .then((response) => response.text())
      .then((txt) => welcome3Schema.parse(new XMLParser().parse(txt)));
    if (input == 0) return { data: semData };
    state.semesterName = input.toString();
    const sem = semData.Details.courseDetail.filter((val) => val.semesterName == state.semesterName).at(0);
    state.semesterData = sem!;
    const courseURL = "https://admission.dei.ac.in:8085/CMS/marksInfo/getRegisteredCourseList.htm";
    const courseData = await fetchM(courseURL, {}, true, true)
      .then((response) => response.text())
      .then((txt) => welcome3Schema.parse(new XMLParser().parse(txt)));
    return { data: courseData };
  }),
  getStudentMarks: publicProcedure.input(z.string()).query(async ({ input }) => {
    const evaluationData = await fetchM(
      "https://admission.dei.ac.in:8085/CMS/awardsheet/getEvaluationComponents.htm",
      { courseCode: input, displayType: "I" },
      true,
      true
    )
      .then((response) => response.text())
      .then((txt) => {
        return welcome2Schema.parse(new XMLParser().parse(txt));
      });

    const marksData = await fetchM(
      "https://admission.dei.ac.in:8085/CMS/marksInfo/getStudentMarks.htm",
      { courseCode: input, displayType: "I" },
      true,
      true
    )
      .then((response) => response.text())
      .then((txt) => {
        return welcome1Schema.parse(new XMLParser().parse(txt));
      });

    return { comps: evaluationData, marks: marksData };
  }),
  magic: publicProcedure.query((opts) => {
    console.log(opts.ctx.user);
    return 1;
  }),
});
