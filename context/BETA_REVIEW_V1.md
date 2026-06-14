# Phase 6.4 - Internal Beta Review V1

Date: 2026-06-14

Scope: product evaluation and matching-quality review only. No backend code, frontend code, API contract, database schema or AI feature was changed in this phase.

Note: the repository does not currently contain raw beta artifacts such as screenshots, CSV exports, expected-score notes or the exact 10 production analysis records. This review uses anonymized case slots from the 10-user beta run and product-level patterns observed from the current matcher design. Fill exact `expected_score` and `actual_score` from beta notes or database exports before using this as a final external report.

## 1. Tổng Quan Beta Test

Internal beta V1 covered:

- 10 CV.
- 10 JD.
- Multiple profile types:
  - student / intern-ready candidate
  - fresher backend candidate
  - frontend-focused candidate
  - fullstack learner
  - AI / data-oriented candidate
  - career switcher
  - profile with weak CV evidence
  - profile with strong transferable skills but mismatched role
- Multiple fit/mismatch cases:
  - strong skill overlap
  - partial fit
  - role mismatch
  - weak CV but relevant projects
  - keyword-heavy CV with shallow evidence
  - JD requiring stack not clearly present in CV

Current matcher basis:

- Rule-based skill extraction.
- Skill overlap.
- Keyword overlap.
- Optional semantic similarity when Sentence Transformers is enabled.
- Length sanity.
- Skill gap priority and improvement plan generated from detected missing skills.

Production note:

- On Render Free, `SENTENCE_TRANSFORMERS_ENABLED=false` is recommended for deploy stability, so matching may rely primarily on rule-based scoring.

## 2. Đánh Giá Từng User

Use this table as the internal source of truth for the 10 beta cases. Replace `TBD` with exact values from beta notes or database exports.

| Case | Profile / CV Type | JD Type | Fit Expectation | Expected Score | Actual Score | Điểm Đúng | Vấn Đề Matcher | Action Đề Xuất |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U01 | Backend intern, có Python/FastAPI/PostgreSQL | Backend Intern | High fit | TBD | TBD | Nên nhận diện Python, FastAPI, PostgreSQL, REST API | Có thể over-score nếu CV chỉ liệt kê skill nhưng thiếu project evidence | Tách điểm skill mention và project evidence trong V2 |
| U02 | Frontend React/TypeScript | Frontend Developer | High fit | TBD | TBD | Nên match React, TypeScript, HTML/CSS, Tailwind | Có thể thiếu alias hoặc đánh đồng UI keyword với production frontend skill | Mở rộng skill alias + weighted frontend core skills |
| U03 | Fullstack learner, nhiều keyword nhưng kinh nghiệm mỏng | Fullstack Intern | Medium fit | TBD | TBD | Skill overlap có thể đúng ở React/Node/SQL | Dễ over-score do keyword stuffing | Thêm evidence scoring: project, responsibility, measurable output |
| U04 | Backend CV nhưng JD thiên DevOps/Docker/Cloud | Backend/DevOps hybrid | Partial mismatch | TBD | TBD | Nên phát hiện Docker/Cloud là gap | Nếu có vài backend keyword, final score có thể cao hơn kỳ vọng | Tăng penalty role-critical missing skills |
| U05 | AI/data profile với Python/ML/NLP | AI Intern | High/medium fit | TBD | TBD | Nên match Python, machine learning, AI, NLP | Có thể thiếu nuance giữa ML project và software engineering JD | Tách AI role core skills và software delivery skills |
| U06 | Career switcher có transferable skills, ít tech skill | Junior Developer | Low/medium fit | TBD | TBD | Nên ghi nhận SQL/Git/project nếu có | Transferable skills như analysis/communication chưa được model hóa tốt | Thêm transferable skill layer nhưng không để inflate technical score |
| U07 | CV rất ngắn, thiếu mô tả project | Backend Intern | Low confidence | TBD | TBD | Length sanity nên cảnh báo CV thiếu thông tin | Nếu skill list ngắn nhưng trùng JD, score vẫn có thể nhìn quá tự tin | Thêm confidence score / data completeness warning |
| U08 | CV có Java/.NET nhưng JD yêu cầu Python/FastAPI | Backend Python | Role-stack mismatch | TBD | TBD | Nên match backend/general skill và báo thiếu Python/FastAPI | Có thể score quá cao vì backend/SQL/Git overlap | Phân biệt same-role different-stack mismatch |
| U09 | CV frontend nhưng JD backend | Backend Intern | Low fit | TBD | TBD | Nên phát hiện role mismatch frontend vs backend | Nếu JD/CV đều có Git, REST API, JavaScript có thể false positive | Role mismatch penalty cần mạnh hơn |
| U10 | CV mạnh, nhiều project sát JD | Target role exact match | Very high fit | TBD | TBD | Nên score cao và missing skills ít | Nếu semantic disabled, score có thể chưa phản ánh project quality đầy đủ | Bật semantic khi infra cho phép hoặc thêm project-evidence heuristics |

## 3. Tổng Hợp Pattern

### Matcher Đang Làm Tốt

- Detect tốt các skill explicit trong CV/JD khi skill nằm trong dictionary.
- Explainability tốt cho MVP:
  - matched skills
  - missing skills
  - keyword overlap
  - scoring breakdown
  - preview CV/JD text
- Skill gap output hữu ích cho user mới vì dễ hiểu ngay skill nào còn thiếu.
- Rule-based logic dễ debug, dễ kiểm soát và phù hợp với MVP beta.

### Matcher Đang Fail / Cần Cải Thiện

- Chưa phân biệt tốt giữa:
  - skill được liệt kê trong CV
  - skill được dùng thật trong project
  - skill được dùng ở production context
- Chưa có confidence score rõ ràng khi CV/JD text quá ngắn hoặc extract text kém.
- Chưa có enough role-stack reasoning:
  - Backend Java/.NET vs Backend Python/FastAPI
  - Frontend React vs Backend JD
  - AI/Data role vs Software Engineer JD
- Semantic similarity bị tắt trên Render Free nên quality phụ thuộc nhiều vào rule-based skill/keyword scoring.

### False Positive

Common false-positive sources:

- Generic tech words: `backend`, `frontend`, `API`, `database`, `Git`.
- CV liệt kê nhiều keyword nhưng không chứng minh bằng project.
- JD có nhiều broad keywords làm overlap cao dù role thật sự khác.

Risk:

- User có thể tưởng mình fit hơn thực tế.
- Roadmap/interview có thể ưu tiên sai nếu analysis score quá lạc quan.

### Over-Scoring

Over-scoring likely happens when:

- CV contains many JD keywords but little evidence.
- Role is same family but stack differs significantly.
- Missing role-critical skills are not penalized enough.

Examples:

- Java/.NET backend CV matched against Python/FastAPI JD.
- Frontend CV matched against fullstack/backend JD because both mention REST API, Git, JavaScript.
- Short CV with skill list but no project context.

### Transferable Skill Issue

Current matcher mostly scores technical keywords. It does not model transferable skills well:

- problem solving
- communication
- product thinking
- domain knowledge
- testing mindset
- teamwork

Decision for V2:

- Add transferable skill recognition as a secondary signal.
- Do not let transferable skills inflate technical fit too much.
- Use them mostly in suggestions and improvement plan, not core technical score.

### Role Mismatch Issue

Current role context detection is useful but not strong enough as a scoring gate.

Problem cases:

- frontend CV vs backend JD
- AI/data CV vs fullstack JD
- backend same-role but wrong stack

Decision for V2:

- Add role-family detection for CV and JD.
- Add role mismatch penalty when role families differ strongly.
- Add stack mismatch penalty when same role family but critical stack differs.

## 4. Prioritized Backlog

### P0 - Must Fix Before Wider Beta

1. Add role-family detection for CV and JD.
   - backend
   - frontend
   - fullstack
   - AI/data
   - mobile
   - general software

2. Add role mismatch penalty.
   - Frontend CV vs Backend JD should not score high from generic overlap.

3. Add critical-skill weighting.
   - Missing FastAPI/Python in Python backend JD should hurt more than missing a secondary keyword.

4. Add CV evidence heuristic.
   - Skill in project/experience section should score higher than skill only listed in a skill list.

### P1 - Important For Better Product Trust

1. Add confidence / data quality signal.
   - CV too short.
   - JD too short.
   - PDF extraction likely poor.

2. Add stack mismatch explanation.
   - Example: “Bạn có backend foundation, nhưng JD này yêu cầu Python/FastAPI trong khi CV đang thể hiện Java/.NET.”

3. Improve skill dictionary and aliases from beta cases.
   - framework aliases
   - Vietnamese/English mixed JD terms
   - internship-level requirements

4. Separate scoring from suggestion generation.
   - Score should be stricter.
   - Suggestions can still acknowledge transferable strengths.

### P2 - Later Polish

1. Store richer analysis debug snapshot.
   - Current history recomputes derived fields from latest logic.

2. Add lightweight internal review export.
   - CSV or JSON for founder review.

3. Add optional semantic model deployment path.
   - Keep disabled on Render Free.
   - Enable on stronger backend instance or separate model host later.

4. Add frontend copy explaining score interpretation.
   - Score is not hiring probability.
   - Score is an alignment signal.

## 5. Recommendation Cho Phase 6.5 - Matching Scoring V2

Phase 6.5 should focus on scoring quality, not new AI features.

Recommended scope:

1. Keep rule-based matcher explainable.
2. Add role-family detection for both CV and JD.
3. Add role mismatch and stack mismatch penalties.
4. Weight critical JD skills higher than generic overlap.
5. Add evidence-aware scoring:
   - skill in project/experience text > skill only in skill list
   - repeated meaningful usage > one-off keyword
6. Add confidence signal:
   - high / medium / low confidence
   - based on text length, extraction quality and evidence richness
7. Update scoring breakdown:
   - skill_score
   - keyword_score
   - semantic_score
   - role_alignment_score
   - evidence_score
   - length_sanity
   - confidence
   - final_score
8. Keep semantic similarity optional and fallback-safe.

Non-goals for Phase 6.5:

- No LLM API.
- No fine-tuning.
- No new product module.
- No recruiter dashboard.
- No complex analytics dashboard.

Success criteria:

- Obvious role mismatch should score lower.
- Strong exact-fit CV/JD should remain high.
- Keyword-heavy but shallow CV should not over-score.
- Missing role-critical skills should be reflected clearly.
- User should understand why the score was given and what to improve next.

## Phase 6.5 Implementation Review

Matching Scoring V2 addresses the main P0/P1 beta findings from this review:

- U01/U10 exact backend fit should remain high because role, stack, critical skills and project evidence align.
- U08 same-role different-stack now keeps partial backend credit but penalizes missing Python/FastAPI stack alignment.
- U09 frontend CV vs backend JD now receives strong role alignment penalty and should no longer score high from generic API/Git overlap.
- U07 short CV now returns low confidence and caps overconfident scoring.
- U03 keyword-heavy but shallow CV is moderated by evidence scoring.

The review still needs exact expected and actual beta scores filled from beta notes or production exports before numeric calibration can be finalized.
