import { create } from "zustand";

interface GenerateStore {
  prompt: string;
  setPrompt: (p: string) => void;
}

export const useGenerateStore = create<GenerateStore>((set) => ({
  prompt: "",
  setPrompt: (p) => set({ prompt: p }),
}));
