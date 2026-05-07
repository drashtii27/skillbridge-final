export interface User {
  id: number;
  email: string;
  name: string;
  xp: number;
  badges: string[];
  avatar_color: string;
}

export interface SkillItem {
  skill: string;
  category: "Critical" | "Important" | "Emerging";
  importance_score: number;
}

export interface SkillGapResult {
  role: string;
  readiness_pct: number;
  gap_pct: number;
  matched: SkillItem[];
  gaps: SkillItem[];
  category_chart: { categories: string[]; have: number[]; need: number[] };
  market_insight: string;
  months: number;
}

export interface Resource {
  type: "youtube" | "course" | "docs" | "practice";
  title: string;
  url: string;
  channel?: string;
  platform?: string;
  free?: boolean;
}

export interface Project {
  title: string;
  description: string;
  tech_stack: string[];
  time_estimate: string;
  one_liner?: string;
  difficulty?: string;
  recruiter_appeal?: string;
}

export interface Week {
  week: number;
  month: number;
  skills_focus: string[];
  daily_plan: string;
  resources: Resource[];
  project: Project;
  checkpoint: string;
  practice_platforms: { name: string; url: string; focus: string }[];
  car_position_pct: number;
}

export interface Phase {
  month: number;
  title: string;
  weeks: Week[];
}

export interface DiscordServer {
  name: string;
  url: string;
  members?: string;
}

export interface CollabPlatform {
  name: string;
  url: string;
  desc: string;
}

export interface RoadmapData {
  roadmap_id?: number;
  role: string;
  months: number;
  user_skills: string[];
  missing_skills: string[];
  readiness_pct: number;
  phases: Phase[];
  portfolio_projects: Project[];
  interview_prep: {
    start_month: number;
    platforms: { name: string; url: string; focus: string }[];
    focus_skills: string[];
  };
  networking: {
    communities: { name: string; url: string }[];
    discord_servers: DiscordServer[];
    collab_platforms: CollabPlatform[];
    opennote?: { title: string; url: string; description: string };
  };
  milestones: { month: number; description: string }[];
  export: { opennote_markdown: string; created_at: string };
}

export interface InterviewQuestion {
  question: string;
  difficulty: "Easy" | "Medium" | "Hard";
  category: string;
  skills_tested: string[];
  answer_outline: string[];
  source?: string;
}

export interface Job {
  title: string;
  company: string;
  location: string;
  salary_min: number;
  salary_max: number;
  url: string;
  description_snippet: string;
  source: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_index: number;
  skill_tag: string;
  difficulty: string;
  explanation?: string;
}

export interface Badge {
  id: string;
  title: string;
  icon: string;
  xp: number;
  desc: string;
  earned?: boolean;
}

export interface AppState {
  user: User | null;
  accessToken: string | null;
  resumeSkills: string[];
  gapResult: SkillGapResult | null;
  roadmap: RoadmapData | null;
  jobs: Job[];
  interviewQuestions: InterviewQuestion[];
  quizScore: number | null;
  completedSteps: string[];
  completedStepsRoadmapKey: string | null;
  targetRole: string;
  targetMonths: number;
  isLoading: boolean;
  setUser: (u: User | null) => void;
  setAccessToken: (t: string | null) => void;
  setResumeSkills: (s: string[]) => void;
  setGapResult: (r: SkillGapResult | null) => void;
  setRoadmap: (r: RoadmapData | null) => void;
  setJobs: (j: Job[]) => void;
  setInterviewQuestions: (q: InterviewQuestion[]) => void;
  setQuizScore: (s: number | null) => void;
  setCompletedSteps: (steps: string[]) => void;
  setTargetRole: (r: string) => void;
  setTargetMonths: (m: number) => void;
  setLoading: (l: boolean) => void;
}
