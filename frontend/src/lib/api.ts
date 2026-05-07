import axios from "axios";

// All requests go through Next.js rewrites (same origin → no cross-origin errors).
// next.config.ts proxies /api/* → FastAPI backend automatically.
export const api = axios.create({
  baseURL: "/api",
  timeout: 120_000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("skillbridge-store");
    if (stored) {
      try {
        const { state } = JSON.parse(stored);
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
      } catch {}
    }
  }
  return config;
});

// ─── Auth ────────────────────────────────────────────────
export const register = (email: string, password: string, name: string) =>
  api.post("/auth/register", { email, password, name });

export const login = (email: string, password: string) =>
  api.post("/auth/login", { email, password });

export const getMe = () => api.get("/me");

// ─── Resume ──────────────────────────────────────────────
export const uploadResume = (file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return api.post("/resume/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
};

// ─── Skills ──────────────────────────────────────────────
export const analyzeSkills = (role: string, user_skills: string[], months: number) =>
  api.post("/skills/analyze", { role, user_skills, months });

export const suggestRoles = (user_skills: string[]) =>
  api.post("/skills/suggest-roles", { user_skills });

// ─── Roadmap ─────────────────────────────────────────────
export const generateRoadmap = (payload: {
  role: string;
  user_skills: string[];
  missing_skills: string[];
  readiness_pct: number;
  months: number;
}) => api.post("/roadmap/generate", payload);

export const getRoadmap = (id: number) => api.get(`/roadmap/${id}`);

export const updateProgress = (roadmapId: number, stepId: string) =>
  api.post(`/roadmap/${roadmapId}/progress?step_id=${stepId}`);

// ─── Interview ───────────────────────────────────────────
export const getInterviewQuestions = (role: string, skills: string[], count = 10) =>
  api.post("/interview/questions", { role, skills_to_test: skills, count });

export const getAdaptiveQuestion = (role: string, skills: string[], step: number) =>
  api.post("/interview/adaptive", { role, skills, step });

// ─── Jobs ────────────────────────────────────────────────
export const searchJobs = (role: string, location = "us", count = 8) =>
  api.get("/jobs/search", { params: { role, location, count } });

export const trackJobClick = (job_url: string, job_title: string) =>
  api.post("/jobs/click", null, { params: { job_url, job_title } });

// ─── Quiz ────────────────────────────────────────────────
export const getQuizQuestions = (role: string, skills: string, count = 5) =>
  api.get("/quiz/questions", { params: { role, skills, count } });

export const submitQuiz = (answers: object[], role: string) =>
  api.post("/quiz/submit", { answers, role });

// ─── Misc ────────────────────────────────────────────────
export const getRoles = () => api.get("/roles");
