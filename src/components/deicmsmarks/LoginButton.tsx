import { isLoggedIn, password, semName, setCourseName, setLoggedIn, setSemName, username } from "@/context/deicmsmarks";
import { Index, Show, createEffect, createSignal, type Component, type JSX } from "solid-js";
import type { courseDetailSchema } from "@server/schemas/deicms.detail.sem";
import { useStore } from "@nanostores/solid";
import { createStore } from "solid-js/store";
import { client } from "@/utils/trpc";
import { z } from "zod";

const LoginButton: Component = () => {
  let button!: HTMLButtonElement;
  let semEle!: HTMLSelectElement;
  let courseEle!: HTMLSelectElement;

  const [semList, setSemList] = createStore<z.infer<typeof courseDetailSchema>[]>([]);
  const [courseList, setCourseList] = createStore<z.infer<typeof courseDetailSchema>[]>([]);

  const handler = async () => {
    const res = await client.deicms.login.query({ username: username(), password: password() });
    if (res.login) setLoggedIn(true);
    const sem = await client.deicms.getRegisteredSemesterCourseList.query(semName());
    setSemList(sem.data.Details.courseDetail);
  };

  createEffect(async () => {
    if (semName() !== 0) {
      courseEle.disabled = false;
      const courses = await client.deicms.getRegisteredSemesterCourseList.query(semName());
      setCourseList(courses.data.Details.courseDetail);
    }
  });
  return (
    <Show
      when={isLoggedIn()}
      fallback={
        <button
          ref={button}
          type="submit"
          class="w-full bg-blue-500 text-white py-3 rounded-md hover:bg-blue-600 focus:outline-none focus:ring focus:ring-blue-200"
          onclick={handler}
        >
          Login
        </button>
      }
    >
      <div class="join w-full">
        <select
          ref={semEle}
          class="select select-bordered join-item w-full"
          onchange={(e) => {
            setSemName(Number(e.target.value));
            setCourseName(false);
          }}
        >
          <option disabled selected>
            Semester
          </option>
          <Index each={semList}>
            {(item, index) => <option value={item().semesterName}>{item().semesterCode}</option>}
          </Index>
        </select>
        <select
          ref={courseEle}
          class="select select-bordered join-item w-full"
          onchange={(e) => setCourseName(e.target.value)}
          disabled
        >
          <option disabled selected>
            Course
          </option>
          <Index each={courseList}>
            {(item, index) => <option value={item().courseCode}>{item().courseCode}</option>}
          </Index>
        </select>
      </div>
    </Show>
  );
};

export default LoginButton;
