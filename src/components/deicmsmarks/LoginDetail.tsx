import { isLoggedIn, setLoggedIn, setPassword, setUsername, username } from "@/context/deicmsmarks";
import { Show, createSignal, type Component, type JSX } from "solid-js";
import { useStore } from "@nanostores/solid";
import { client } from "@/utils/trpc";

export const UsernameBox: Component = () => {
  return (
    <>
      <input
        type="text"
        placeholder="Username"
        onchange={(e) => setUsername(e.target.value)}
        class="block w-full px-4 py-3 rounded-md bg-gray-100 placeholder-gray-400 focus:outline-none focus:ring focus:ring-blue-200"
      />
      <Show when={isLoggedIn() && username() === "2201860"}>
        <div class="label">
          <span class="label-text-alt"></span>
          <span class="label-text-alt text-error">Is your name Megha by any chance :P</span>
        </div>
      </Show>
    </>
  );
};

export const PasswordBox: Component = () => {
  return (
    <input
      type="password"
      placeholder="Password"
      onchange={(e) => setPassword(e.target.value)}
      class="block w-full px-4 py-3 rounded-md bg-gray-100 placeholder-gray-400 focus:outline-none focus:ring focus:ring-blue-200"
    />
  );
};
