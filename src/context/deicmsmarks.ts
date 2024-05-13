import { createStore } from "solid-js/store";
import { createSignal } from "solid-js";

export const [isLoggedIn, setLoggedIn] = createSignal(false);
export const [username, setUsername] = createSignal("2201854");
export const [password, setPassword] = createSignal("14112003");
export const [semName, setSemName] = createSignal(0);
export const [courseName, setCourseName] = createSignal<string | boolean>(false);
