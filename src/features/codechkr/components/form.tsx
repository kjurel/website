/** @jsxImportSource solid-js */
import { useStore } from "@nanostores/solid";
import { Show, type Component, type JSX } from "solid-js";
import { data, result } from "../context/store";
import * as XLSX from "xlsx";

function exportTableToExcel(tableID: string, filename = "table.xls"): void {
  const table = document.getElementById(tableID);
  if (!table) return;

  const wb = XLSX.utils.table_to_book(table, { sheet: "SheetJS" });
  const wbout = XLSX.write(wb, { bookType: "xls", bookSST: true, type: "binary" });

  function s2ab(s: string): ArrayBuffer {
    const buf = new ArrayBuffer(s.length);
    const view = new Uint8Array(buf);
    for (let i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
    return buf;
  }

  const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
  const link = document.createElement("a");
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}

export const Submitter: Component = () => {
  let files!: HTMLInputElement;
  const answer = useStore(result);

  const handleFileChange = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (!input || !input.files || input.files.length === 0) {
      console.error("No file selected.");
      return;
    }

    const fileList = input.files;
    // Handle the selected files
    // You can perform actions with the selected files here
    console.log(fileList);
  };

  const handleSendClick = () => {
    const input = files;
    if (!input || !input.files || input.files.length === 0) {
      console.error("No file selected.");
      return;
    }

    const formData = new FormData();
    formData.append("f", input.files[0]);

    fetch("/api/py/codecheckr", {
      method: "POST",
      body: formData,
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      // credentials: "include",
    })
      .then((response) => {
        if (response.ok) {
          console.log("Files uploaded successfully.");
          // Add logic here for successful upload
          response.json().then((v) => {
            console.log(v);
            data.set(v);
          });
        } else {
          console.error("Failed to upload files.");
          // Add logic here for failed upload
        }
      })
      .catch((error) => {
        console.error("Error occurred while uploading files:", error);
        // Add error handling logic here
      });
  };

  return (
    <>
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark" style="background-color: #333;">
        <div class="container">
          <span
            class="navbar-text mx-auto d-block text-center"
            style="font-family: 'Arial', sans-serif; font-weight: bold; font-size: 24px; color: #fff; letter-spacing: 3px;"
          >
            CODE CHECKR
          </span>
        </div>
      </nav>

      <div class="container mt-4">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">Select Code</h4>
            <div class="custom-file mb-3">
              <input
                type="file"
                class="custom-file-input"
                id="customFileInput"
                ref={files}
                accept=".zip"
                onChange={handleFileChange}
              />
              <label class="custom-file-label" for="customFileInput">
                Choose file
              </label>
            </div>
            <button type="submit" class="btn btn-primary" onClick={handleSendClick}>
              SEND
            </button>
          </div>

          <div class="card-body">
            <Show when={answer()} fallback={<h4 class="card-title">Send data to view Table..</h4>}>
              <h2 class="card-title">Marks Data Table</h2>
              <table class="table table-striped" id="maint">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Result</th>
                    <th>Averaged</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.from(answer()!.entries()).map((v) => (
                    <tr>
                      <td>{v[0]}</td>
                      <td>{v[1].result}</td>
                      <td>{v[1].averaged}</td>
                      <td>{v[1].score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button class="btn btn-secondary" onClick={() => exportTableToExcel("maint", "table.xls")}>
                Export to Excel
              </button>
            </Show>
          </div>
        </div>
      </div>
    </>
  );
};
