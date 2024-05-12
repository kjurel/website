// import type { APIRoute } from "astro";
// import Peer from "peerjs";
// Peer;
//
// export const get: APIRoute = async ({ request }) => {
//   // const data = await request.json();
//   // console.log(typeof data.file, data.file);
//   return { body: "this" };
// };
//
// export const post: APIRoute = async ({ request }) => {
//   // const blob = await request.blob();
//   // console.log(blob.type);
//   // const data = new FormData();
//   // if (blob) data.append("file", blob);
//   console.log(request.headers);
//   return {
//     body: await fetch("http://api.qrserver.com/v1/read-qr-code/", {
//       method: "POST",
//       body: await request.formData(),
//     })
//       .then(async (response) => {
//         console.log(response.status);
//         // console.log(await response.text());
//         return response.json();
//       })
//       .then((json) => json)
//       .then((data) => JSON.stringify(data)),
//   };
// };
