"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AppState } from "@/types";

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      resumeSkills: [],
      gapResult: null,
      roadmap: null,
      jobs: [],
      interviewQuestions: [],
      quizScore: null,
      completedSteps: [],
      completedStepsRoadmapKey: null,
      targetRole: "",
      targetMonths: 3,
      isLoading: false,
      setUser: (u) => set({ user: u }),
      setAccessToken: (t) => set({ accessToken: t }),
      setResumeSkills: (s) => set({ resumeSkills: s }),
      setGapResult: (r) => set({ gapResult: r }),
      setRoadmap: (r) => set((state) => {
        const newKey = r ? `${r.role}__${r.roadmap_id ?? "0"}` : null;
        const isSame = newKey !== null && newKey === state.completedStepsRoadmapKey;
        return {
          roadmap: r,
          completedSteps: isSame ? state.completedSteps : [],
          completedStepsRoadmapKey: newKey,
        };
      }),
      setJobs: (j) => set({ jobs: j }),
      setInterviewQuestions: (q) => set({ interviewQuestions: q }),
      setQuizScore: (s) => set({ quizScore: s }),
      setCompletedSteps: (steps) => set({ completedSteps: steps }),
      setTargetRole: (r) => set({ targetRole: r }),
      setTargetMonths: (m) => set({ targetMonths: m }),
      setLoading: (l) => set({ isLoading: l }),
    }),
    {
      name: "skillbridge-store",
      partialize: (s) => ({
        accessToken: s.accessToken,
        user: s.user,
        completedSteps: s.completedSteps,
        completedStepsRoadmapKey: s.completedStepsRoadmapKey,
      }),
    }
  )
);
