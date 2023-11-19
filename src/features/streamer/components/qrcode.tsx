import { useStore } from "@nanostores/solid";
import { Component, createEffect, createResource, createSignal, onMount } from "solid-js";
import { Show } from "solid-js/web";
import { localConnectionId } from "../context/store";
import { targetConnectionId } from "../context/store";

export const Scanner: Component = () => {
  let video!: HTMLVideoElement, canvas!: HTMLCanvasElement;
  const [clicked, setClicked] = createSignal(false);
  const [stream$, setStream] = createSignal<MediaStream | null>(null);
  const [device, setDevice] = createSignal<number>(-1);
  const [cameras, { refetch }] = createResource(() =>
    navigator.mediaDevices
      .enumerateDevices()
      .then((devices) => devices.filter((device) => device.kind === "videoinput"))
  );
  onMount(() => navigator.mediaDevices.addEventListener("devicechange", refetch));
  const flushStreams = () => {
    stream$()
      ?.getTracks()
      .forEach((track) => track.stop());
    video.srcObject = null;
    video.load();
  };
  createEffect(() => {
    if (clicked()) {
      video.hidden = true;
    } else {
      video.srcObject = stream$();
      video.load();
    }
  });
  return (
    <>
      <Show
        when={clicked()}
        fallback={
          <>
            <div class="flex justify-center">
              <video ref={video} autoplay playsinline></video>
            </div>
            <div class="btn-group flex justify-center p-2" role="group" aria-label="QR video controls">
              <button
                class="btn btn-outline-primary"
                onclick={() => {
                  const cams = cameras();
                  if (cams != null && cams!.length != 1) {
                    const nextId = device() + 1 <= cams.length - 1 ? device() + 1 : 0;
                    flushStreams();
                    const nextDevice = cams[nextId];
                    if (nextDevice)
                      navigator.mediaDevices
                        .getUserMedia({
                          video: { deviceId: nextDevice.deviceId },
                        })
                        .then((stream) => setStream(stream));
                    setDevice(nextId);
                  } else {
                    navigator.mediaDevices
                      .getUserMedia({
                        video: true,
                      })
                      .then((stream) => setStream(stream));
                  }
                }}
              >
                Switch Camera
              </button>
              <button
                class="btn btn-outline-primary"
                onclick={() => {
                  if (video.srcObject === null) {
                    console.log("video is null");
                    return;
                  }
                  setClicked(true);
                  canvas.width = video.videoWidth;
                  canvas.height = video.videoHeight;
                  canvas.getContext("2d")?.drawImage(video, 0, 0);
                  flushStreams();
                  canvas.toBlob((blob) => {
                    const data = new FormData();
                    if (blob) data.append("file", blob);
                    fetch("/api/qrScanner", {
                      body: data,
                      method: "POST",
                      headers: {
                        "Access-Control-Allow-Origin": "*",
                      },
                    })
                      .then((res) => res.json())
                      .then((json) => {
                        console.log(json[0]["symbol"][0]["error"]);
                        targetConnectionId.set(json[0]["symbol"][0].data ?? null);
                      });
                  }, "image/png");
                }}
              >
                Take a picture
              </button>
            </div>
          </>
        }
      >
        <div class="flex justify-center">
          <canvas ref={canvas}></canvas>
        </div>
        <div class="btn-group flex justify-center p-2" role="group" aria-label="QR video controls">
          <button
            type="button"
            class="btn btn-primary"
            onclick={() => {
              setClicked(false);
            }}
          >
            Retake
          </button>
          <button type="button" class="btn btn-primary">
            Proceed
          </button>
        </div>
      </Show>
    </>
  );
};

export const Generate = () => {
  const id = useStore(localConnectionId);

  return (
    <>
      <Show when={id() != null} fallback={<div>Loading...</div>}>
        <div class="flex justify-center">
          <img src={`https://api.qrserver.com/v1/create-qr-code/?data=${id()}&size=500x500`} alt="" title="" />
        </div>
      </Show>
    </>
  );
};
