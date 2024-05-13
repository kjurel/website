import { courseName, isLoggedIn } from "@/context/deicmsmarks";
import { Show, createEffect, type Component } from "solid-js";
import autoTable from "jspdf-autotable";
import { client } from "@/utils/trpc";
import jsPDF from "jspdf";

const ViewButton: Component = () => {
  let button!: HTMLButtonElement;
  createEffect(async () => {
    if (courseName() !== "") {
      button.disabled = false;
    }
  });
  const handler = async () => {
    const response = await client.deicms.getStudentMarks.query(courseName());
    const comps: { [key: string]: string } = {};
    response.comps.ComponentList.component.forEach(
      (val, idx) => (comps[val.evaluationId.toString()] = val.evaluationIdName.toString())
    );

    type bodyElem = { roll: string; total: string; grade: string; [key: string]: string };
    const bodyDD: bodyElem[] = [];
    response.marks.Details.marksDetail.forEach((value) => {
      const idx = bodyDD.findIndex((val, idx) => val.roll == value.rollNumber.toString());

      if (idx != -1) {
        // @ts-ignore
        bodyDD[idx][value.evaluationId] = value.marks.toString();
      } else {
        const bdd: bodyElem = {
          roll: value.rollNumber.toString(),
          total: value.totalInternal.toString(),
          grade: value.internalGrade.toString(),
        };
        bdd[value.evaluationId] = value.marks.toString();
        bodyDD.push(bdd);
      }
    });

    const doc = new jsPDF();
    autoTable(doc, {
      theme: "grid",
      head: [{ roll: "Roll Number", ...comps, total: "Total Marks", grade: "Grade" }],
      body: bodyDD,
      styles: { cellPadding: 0.5, fontSize: 8 },
      // tableWidth: "wrap",
    });
    doc.save(
      `${courseName()}-${new Date().toLocaleDateString("en", { day: "numeric", month: "short" }).replace(/\s/g, "").toLowerCase()}.pdf`
    );
  };
  return (
    <Show when={isLoggedIn()}>
      <button
        ref={button}
        type="submit"
        onclick={handler}
        class="w-full bg-blue-500 text-white py-3 rounded-md hover:bg-blue-600 focus:outline-none focus:ring focus:ring-blue-200"
        disabled
      >
        Download
      </button>
    </Show>
  );
};

export default ViewButton;
