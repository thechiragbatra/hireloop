export interface Profile {
  id: string
  user_id?: string
  skills: string[]
  experience: ExperienceItem[]
  education: EducationItem[]
  projects: ProjectItem[]
  contact?: Contact
  raw_text?: string
  created_at?: string
}

export interface Contact {
  email?: string | null
  phone?: string | null
  location?: string | null
  linkedin?: string | null
  github?: string | null
  website?: string | null
}

export interface ExperienceItem {
  id: string
  company: string
  title: string
  start_date?: string | null
  end_date?: string | null
  location?: string | null
  bullets: Bullet[]
}

export interface EducationItem {
  id: string
  institution: string
  degree: string
  field_of_study?: string | null
  start_date?: string | null
  end_date?: string | null
}

export interface ProjectItem {
  id: string
  name: string
  description?: string
  technologies: string[]
  url?: string | null
  bullets: Bullet[]
}

export interface Bullet {
  id: string
  text: string
}

export interface Job {
  id: string
  title: string
  company: string
  location?: string | null
  description: string
  source: string
  url?: string | null
  requirements?: string[]
  match_score?: number
}

export interface MatchResult {
  job_id: string
  score: number
  reasons: string[]
  missing_skills: string[]
}

export interface TailoredBullet {
  text: string
  source_ids: string[]
}

export interface TailoredResume {
  job_id: string
  bullets: TailoredBullet[]
  summary?: string | null
}

export interface FaithfulnessReport {
  overall_score: number
  supported_bullets: number
  total_bullets: number
  unsupported: string[]
}

export interface ApplicationRecord {
  id: string
  user_id?: string
  company: string
  role: string
  url?: string | null
  match_score: number
  status: string
  date: string
  resume_version: string
}

export interface ApplyKit {
  job_id: string
  profile_id: string
  user_id?: string
  tailored_resume: TailoredResume
  cover_letter: string
  cover_letter_path?: string | null
  note: string
}

export interface WakeStatus {
  awake: boolean
  message: string
}
