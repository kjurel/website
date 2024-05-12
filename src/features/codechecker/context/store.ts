import { atom } from "nanostores";
// import { isServer } from "solid-js/web";
// import { createStore } from "solid-js/store";

export interface Response {
  pairs: [string, string];
  token_overlap: number;
  similarities: [number, number];
}

interface Result {
  result: number;
  averaged: number;
  score: number;
}

export const data = atom<Response[] | null>(null);
export const result = atom<Map<string, Result> | null>(null);

data.subscribe((data) => {
  if (!data) {
    console.warn("Data was null");
    return;
  }
  const newMap = new Map<string, Result>();
  data.map((v) => {
    for (const [idx, key] of v.pairs.entries()) {
      const score = v.similarities[idx]!;
      if (newMap.has(key)) {
        const res = newMap.get(key)!.result;
        const avgd = newMap.get(key)!.averaged;

        const newRes = (res * avgd + score) / (avgd + 1);
        const newAvgd = avgd + 1;

        newMap.set(key, { result: newRes, averaged: newAvgd, score: (1 - newRes) * 10 });
      } else {
        newMap.set(key, { result: score, averaged: 1, score: (1 - score) * 10 });
      }
    }
  });
  result.set(newMap);
});

result.subscribe((v) => console.log(v));
