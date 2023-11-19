/** @jsxImportSource solid-js */
import { useStore } from "@nanostores/solid";
import type { Component, JSX } from "solid-js";
import { localConnectionId, peerConnection, targetConnectionId } from "../context/store";
import type { StreamGroup } from "../context/store";
import { setStreams } from "../context/store";

export const Connect: Component = () => {
  const peer$ = useStore(peerConnection);

  return (
    <>
      <button
        class="btn btn-outline-secondary"
        onclick={() => {
          navigator.mediaDevices
            .getUserMedia({
              video: { facingMode: "environment" },
              audio: false,
            })
            .then((stream) => {
              setStreams(0, {
                name: "local-stream",
                fromId: peer$()?.id ?? localConnectionId.get(),
                stream: stream,
              } satisfies StreamGroup);

              const call = peer$()?.call(targetConnectionId.get() ?? "", stream);
              call?.on("stream", () => console.log("Not Implemented yet"));
            });
        }}
      >
        Connect
      </button>
      {}
      {/* <Show when={}></Show> */}
    </>
  );
};

export const SwitchCamera: Component = (props: JSX.HTMLAttributes<HTMLButtonElement> & { stream?: MediaStream }) => {
  return <button></button>;
};
