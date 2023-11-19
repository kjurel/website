/** @jsxImportSource solid-js */
import { createSignal, createEffect, For, Show } from "solid-js";
import type { JSX, Component } from "solid-js";
import { streams, StreamGroup } from "../context/store";

export const StreamBox: Component<{ children?: JSX.Element }> = () => {
  createEffect(() => {
    console.log(streams);
  });

  return (
    <div>
      <For each={streams}>{(stream) => <StreamVideo stream={stream} />}</For>
    </div>
  );
};

export const StreamVideo: Component<{ stream: StreamGroup } & JSX.HTMLAttributes<HTMLVideoElement>> = (props) => {
  let canvas!: HTMLCanvasElement;
  let video!: HTMLVideoElement;
  const [stream] = createSignal(props.stream);
  const [clicked, setClicked] = createSignal(false);

  const ID = "video" + props.stream.fromId;
  createEffect(() => {
    video.srcObject = stream().stream;
    video.load();
  });
  return (
    <>
      <div class="hstsack gap-3">
        <div class="float-left">
          <label for={ID}>StreamName: {props.stream.name}</label>
          <video ref={video} id={ID} class="rounded m-1" autoplay playsinline controls={false}></video>
          <button
            class="btn btn-outline-primary m-2"
            onclick={() => {
              setClicked(true);
              canvas.height = video.videoHeight;
              canvas.width = video.videoWidth;
              canvas.getContext("2d")?.drawImage(video, 0, 0);
            }}
          >
            Capture
          </button>
        </div>
        <div class="float-right">
          <label for="cpimage">Captured image will be shown here</label>
          <Show when={clicked()}>
            <canvas ref={canvas} id="cpimage" class="rounded m-1"></canvas>
            <button class="btn btn-outline-danger m-2" onclick={() => setClicked(false)}>
              Delete
            </button>
          </Show>
        </div>
      </div>
    </>
  );
};
