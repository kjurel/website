import { atom, onMount } from "nanostores";
import type { Peer } from "peerjs";
import { isServer } from "solid-js/web";
import { createStore } from "solid-js/store";

export interface StreamGroup {
  name: string;
  fromId: string;
  stream: MediaStream;
}

export const [streams, setStreams] = createStore<StreamGroup[]>([]);

export const peerConnection = atom<Peer | undefined>();
onMount(peerConnection, () => {
  if (!isServer) {
    import("peerjs")
      .then(({ default: peerjs }) => new peerjs({ debug: 3 }))
      // .then(({ peerjs: { default: peerjs } }) => new peerjs({ debug: 3 }))
      .then((p) => peerConnection.set(p))
      .then(() => {
        peerConnection.get()?.on("open", (id) => localConnectionId.set(id));
        peerConnection.get()?.on("call", (call) => {
          call.on("stream", (stream) =>
            setStreams(0, {
              name: "remote-stream",
              fromId: call.peer,
              stream: stream,
            } satisfies StreamGroup)
          );
          call.answer();

          console.log("Call accepted");
        });
      });
  } else console.info("peerConnection: onMount: server-side");

  return () => peerConnection.get()?.destroy();
});

export const localConnectionId = atom<string>("");
export const targetConnectionId = atom<string>("");
