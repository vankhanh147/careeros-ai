# DATABASE_CONTEXT.md

Database hiện được định nghĩa bằng SQLAlchemy models trong `backend/app/models`. Backend dùng sync SQLAlchemy Session và PostgreSQL/Supabase qua `DATABASE_URL`.

## Database Setup

File: `backend/app/database.py`

- `engine = create_engine(settings.database_url, pool_pre_ping=True)`
- `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
- `Base` extends `DeclarativeBase`
- `get_db()` yield `Session`

File: `backend/app/main.py`

- `Base.metadata.create_all(bind=engine)` chạy trong lifespan.
- Chưa có Alembic migrations.

## Models

### `User`

File: `backend/app/models/user.py`

Table: `users`

Fields:

- `id`: primary key, indexed.
- `email`: string(255), unique, indexed, required.
- `full_name`: string(255), required.
- `hashed_password`: string(255), required.
- `role`: string(50), default `user`, required.
- `is_active`: boolean, default true.
- `created_at`: timezone DateTime, server default now.
- `updated_at`: timezone DateTime, server default now, onupdate now.

Relationships:

- one-to-one `career_profile`, cascade delete orphan.
- one-to-many `resumes`, cascade delete orphan.
- one-to-many `job_descriptions`, cascade delete orphan.
- one-to-many `match_analyses`, cascade delete orphan.
- one-to-many `learning_roadmaps`, cascade delete orphan.
- one-to-many `interview_sessions`, cascade delete orphan.

### `CareerProfile`

File: `backend/app/models/career_profile.py`

Table: `career_profiles`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, cascade delete, required.
- `target_role`: string(255), default empty.
- `current_level`: string(100), default empty.
- `skills`: text, default empty.
- `experience_summary`: text, default empty.
- `projects_summary`: text, default empty.
- `career_goal`: text, default empty.
- `timeline`: string(255), default empty.
- `created_at`, `updated_at`.

Constraints:

- Unique constraint on `user_id`: one career profile per user.

Relationships:

- many-to-one `user`.

### `Resume`

File: `backend/app/models/resume.py`

Table: `resumes`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, indexed, cascade delete, required.
- `file_name`: string(255), required.
- `storage_path`: string(500), required.
- `file_url`: string(1000), nullable.
- `extracted_text`: text, nullable.
- `created_at`, `updated_at`.

Relationships:

- many-to-one `user`.
- one-to-many `match_analyses`, cascade delete orphan.

Notes:

- File currently stored locally under `uploads/resumes/user_{id}`.
- `file_url` is reserved for future Supabase Storage/public URL integration.

### `JobDescription`

File: `backend/app/models/job_description.py`

Table: `job_descriptions`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, indexed, cascade delete, required.
- `title`: string(255), required.
- `company`: string(255), nullable.
- `content`: text, required.
- `source_url`: string(1000), nullable.
- `created_at`, `updated_at`.

Relationships:

- many-to-one `user`.
- one-to-many `match_analyses`, cascade delete orphan.

Notes:

- JD can be created from pasted content or upload PDF/TXT.
- Uploaded JD files are saved under `uploads/job_descriptions/user_{id}`, but model currently stores only extracted content and metadata, not a JD file path.

### `MatchAnalysis`

File: `backend/app/models/match_analysis.py`

Table: `match_analyses`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, indexed, cascade delete, required.
- `resume_id`: FK `resumes.id`, indexed, cascade delete, required.
- `job_description_id`: FK `job_descriptions.id`, indexed, cascade delete, required.
- `match_score`: float, required.
- `matched_skills`: text, required, JSON-encoded list.
- `missing_skills`: text, required, JSON-encoded list.
- `keyword_overlap`: text, required, JSON-encoded list.
- `summary`: text, required.
- `suggestions`: text, required, JSON-encoded list.
- `created_at`, `updated_at`.

Relationships:

- many-to-one `user`.
- many-to-one `resume`.
- many-to-one `job_description`.
- one-to-many `learning_roadmaps`.
- one-to-many `interview_sessions`.

Notes:

- Debug fields, semantic breakdown, prioritized skill gaps and improvement plan are not persisted directly in the model. They are recomputed in API responses from stored resume/JD text.

### `LearningRoadmap`

File: `backend/app/models/learning_roadmap.py`

Table: `learning_roadmaps`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, indexed, cascade delete, required.
- `analysis_id`: nullable FK `match_analyses.id`, indexed, `ondelete=SET NULL`.
- `title`: string(255), required.
- `target_role`: string(255), default empty.
- `timeline`: string(255), default empty.
- `items`: text, required, JSON-encoded roadmap item list.
- `summary`: text, required.
- `created_at`, `updated_at`.

Relationships:

- many-to-one `user`.
- many-to-one `analysis`.

### `InterviewSession`

File: `backend/app/models/interview.py`

Table: `interview_sessions`

Fields:

- `id`: primary key, indexed.
- `user_id`: FK `users.id`, indexed, cascade delete, required.
- `analysis_id`: nullable FK `match_analyses.id`, indexed, `ondelete=SET NULL`.
- `target_role`: string(255), default empty.
- `status`: string(50), default `in_progress`.
- `score`: float, nullable.
- `summary`: text, nullable.
- `created_at`, `updated_at`.

Relationships:

- many-to-one `user`.
- many-to-one `analysis`.
- one-to-many `answers`, cascade delete orphan, ordered by answer id.

### `InterviewAnswer`

File: `backend/app/models/interview.py`

Table: `interview_answers`

Fields:

- `id`: primary key, indexed.
- `session_id`: FK `interview_sessions.id`, indexed, cascade delete, required.
- `question`: text, required.
- `expected_keywords`: text, required, JSON-encoded list.
- `user_answer`: text, nullable.
- `score`: float, nullable.
- `feedback`: text, nullable.
- `created_at`: timezone DateTime, server default now.

Relationships:

- many-to-one `session`.

## Relationship Summary

- `User` owns all user data.
- `CareerProfile` is one-to-one with `User`.
- `Resume`, `JobDescription`, `MatchAnalysis`, `LearningRoadmap`, `InterviewSession` are user-owned resources.
- `MatchAnalysis` belongs to one resume and one JD.
- `LearningRoadmap` can reference an analysis but survives if analysis is deleted via SET NULL.
- `InterviewSession` can reference an analysis but survives if analysis is deleted via SET NULL.
- `InterviewAnswer` belongs to one `InterviewSession`.

## Persistence Notes

- Several structured fields are stored as JSON strings in text columns for MVP simplicity.
- No migration system yet; adding/changing columns currently relies on `create_all`, which does not handle migrations for existing databases.
- Supabase Storage is planned but not wired; local upload folders are used now.