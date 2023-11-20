/** @jsxImportSource solid-js */
import { useStore } from "@nanostores/solid";
import { Show, type Component, type JSX } from "solid-js";
import { data, result } from "../context/store";

export const Submitter: Component = () => {
  let files!: HTMLInputElement;
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

    fetch("http://localhost:8000/api/py/codecheckr", {
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
    <div>
      <input ref={files} type="file" accept=".zip" onChange={handleFileChange} />
      <button onClick={handleSendClick}>Send</button>
    </div>
  );
};
