/** @jsxImportSource solid-js */
import { useStore } from "@nanostores/solid";
import type { Component, JSX } from "solid-js";
import {
  localConnectionId,
  peerConnection,
  targetConnectionId,
} from "../shared/stores";
import type { StreamGroup } from "../shared/stores";
import { setStreams } from "../shared/stores";

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

              const call = peer$()?.call(
                targetConnectionId.get() ?? "",
                stream
              );
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

export const SwitchCamera: Component = (
  props: JSX.HTMLAttributes<HTMLButtonElement> & { stream?: MediaStream }
) => {
  return <button></button>;
};
