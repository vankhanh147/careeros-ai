# API_CONTRACTS.md

Base backend: FastAPI app in `backend/app/main.py`.

All endpoints under `/api/*` except `/health`. JWT protected endpoints require `Authorization: Bearer <access_token>`.

## Health

### `GET /health`

Public.

Response:

```json
{"status":"ok","service":"career-os-ai-api"}
```

## Auth

Router: `backend/app/routers/auth.py`

### `POST /api/auth/register`

Public.

Request schema: `RegisterRequest`

Fields:

- `email`
- `full_name`
- `password`

Behavior:

- Normalizes email lowercase.
- Rejects duplicated email with 409.
- Hashes password.
- Creates `User`.

Response: `CurrentUserResponse`.

### `POST /api/auth/login`

Public.

Request schema: `LoginRequest`

Fields:

- `email`
- `password`

Behavior:

- Verifies email/password.
- Rejects inactive users.
- Returns JWT access token.

Response: `TokenResponse`.

### `GET /api/auth/me`

JWT protected.

Response: `CurrentUserResponse`.

## Dashboard

Router: `backend/app/routers/dashboard.py`

### `GET /api/dashboard/summary`

JWT protected.

Response: `DashboardSummaryResponse`

Includes:

- `user`
- `has_career_profile`
- `resume_count`
- `job_description_count`
- `latest_analysis`
- `latest_roadmap`
- `latest_interview`
- `recommended_next_actions`

Recommended next actions are rule-based from profile/documents/analysis/roadmap/interview availability.

## Career Profile

Router: `backend/app/routers/career_profile.py`

### `GET /api/career-profile/me`

JWT protected.

Returns current user career profile or null.

### `PUT /api/career-profile/me`

JWT protected.

Request schema: `CareerProfileUpsertRequest`

Fields:

- `target_role`
- `current_level`
- `skills`
- `experience_summary`
- `projects_summary`
- `career_goal`
- `timeline`

Behavior:

- Upserts one profile per user.
- Strips string fields.

Response: `CareerProfileResponse`.

## Resumes

Router: `backend/app/routers/resumes.py`

### `POST /api/resumes/upload`

JWT protected. Multipart file upload.

Validation:

- Only `.pdf`.
- Max size 5MB.

Behavior:

- Stores file locally under `uploads/resumes/user_{id}`.
- Creates `Resume` row with `file_name`, `storage_path`, `file_url=null`, `extracted_text=null`.

Response: `ResumeResponse`.

### `GET /api/resumes/me`

JWT protected.

Returns current user resumes ordered newest first.

### `DELETE /api/resumes/{resume_id}`

JWT protected.

Behavior:

- Only deletes current user's resume.
- Deletes DB row.
- Deletes local file if it exists.

Response: 204 no content.

## Job Descriptions

Router: `backend/app/routers/job_descriptions.py`

### `POST /api/job-descriptions`

JWT protected.

Request schema: `JobDescriptionCreateRequest`

Fields:

- `title`
- `company` optional
- `content`
- `source_url` optional

Response: `JobDescriptionResponse`.

### `POST /api/job-descriptions/upload`

JWT protected. Multipart file upload.

Form fields:

- `file`
- `title` optional
- `company` optional
- `source_url` optional

Validation:

- Supports `.pdf` and `.txt`.
- Max size 5MB.
- Extracted content must be non-empty.

Behavior:

- Saves upload under `uploads/job_descriptions/user_{id}`.
- Extracts PDF/TXT text.
- Creates `JobDescription` with extracted text in `content`.

Response: `JobDescriptionResponse`.

### `GET /api/job-descriptions/me`

JWT protected.

Returns current user JDs ordered newest first.

### `PUT /api/job-descriptions/{job_description_id}`

JWT protected.

Only updates current user's JD.

Request schema: `JobDescriptionCreateRequest`.

Response: `JobDescriptionResponse`.

### `DELETE /api/job-descriptions/{job_description_id}`

JWT protected.

Only deletes current user's JD.

Response: 204 no content.

## Analysis

Router: `backend/app/routers/analysis.py`

### `POST /api/analysis/resume-job-match`

JWT protected.

Request schema: `ResumeJobMatchRequest`

Fields:

- `resume_id`
- `job_description_id`

Behavior:

- Verifies resume and JD belong to current user.
- Extracts resume PDF text if `Resume.extracted_text` is null.
- Runs `analyze_resume_job_match`.
- Stores base result in `MatchAnalysis`.
- Returns full analysis response with debug fields.

Response: `MatchAnalysisResponse`

Includes:

- `match_score`
- `matched_skills`
- `missing_skills`
- `keyword_overlap`
- `summary`
- `suggestions`
- `resume_text_preview`
- `jd_text_preview`
- `resume_detected_skills`
- `jd_detected_skills`
- `scoring_breakdown`
- `skill_gap_summary`
- `prioritized_missing_skills`
- `improvement_plan`

### `GET /api/analysis/history`

JWT protected.

Returns up to 20 latest analyses for current user. Derived/debug fields are recomputed from stored resume/JD content.

## Roadmaps

Router: `backend/app/routers/roadmaps.py`

### `POST /api/roadmaps/generate`

JWT protected.

Request schema: `RoadmapGenerateRequest`

Fields:

- `analysis_id` optional
- `timeline` optional

Behavior:

- If `analysis_id` is provided, uses that analysis if owned by current user.
- If no analysis, uses career profile.
- Requires either profile or selected analysis.
- Generates rule-based roadmap.
- Stores `items` as JSON string.

Response: `LearningRoadmapResponse`.

### `GET /api/roadmaps/me`

JWT protected.

Returns up to 20 latest roadmaps for current user.

### `GET /api/roadmaps/{roadmap_id}`

JWT protected.

Returns one roadmap owned by current user.

## Interviews

Router: `backend/app/routers/interviews.py`

### `POST /api/interviews/start`

JWT protected.

Request schema: `InterviewStartRequest`

Fields:

- `analysis_id` optional
- `target_role` optional

Behavior:

- Uses selected analysis if provided and owned by current user.
- Infers target role from explicit input, profile, or fallback.
- Generates 5 questions.
- Creates `InterviewSession` and `InterviewAnswer` rows.

Response: `InterviewSessionResponse`.

### `GET /api/interviews/me`

JWT protected.

Returns up to 20 latest interview sessions for current user.

### `GET /api/interviews/{session_id}`

JWT protected.

Returns one session owned by current user.

### `POST /api/interviews/{session_id}/answer`

JWT protected.

Request schema: `InterviewAnswerRequest`

Fields:

- `answer_id`
- `user_answer`

Behavior:

- Rejects if session already finished.
- Scores answer by keyword overlap + length bonus.
- Stores user answer, score and feedback.

Response: updated `InterviewSessionResponse`.

### `POST /api/interviews/{session_id}/finish`

JWT protected.

Behavior:

- Requires at least one answered/scored question.
- Sets session average score.
- Builds session summary.
- Sets status to `finished`.

Response: updated `InterviewSessionResponse`.