# AI_SYSTEMS.md

## Current AI Philosophy

CareerOS AI đang dùng explainable AI MVP. Mục tiêu là tạo insight có thể kiểm chứng, không tạo “black box” phức tạp sớm.

AI hiện tập trung vào:

- Resume ↔ JD Matching
- Skill Gap Detection
- Improvement Plan
- Personalized Roadmap
- Mock Interview question generation and scoring

## Current AI Services

### `backend/app/services/resume_job_matcher.py`

Chức năng:

- Extract text từ CV PDF bằng `pypdf`.
- Extract text từ JD TXT bằng decode UTF-8/UTF-8-SIG/latin-1 fallback.
- Detect skills bằng dictionary + aliases.
- Tính keyword overlap.
- Tính length sanity.
- Tính semantic similarity bằng Sentence Transformers nếu model load được.
- Phân loại missing skills theo priority.
- Sinh skill gap summary, improvement plan, suggestions.
- Trả text previews để debug dữ liệu đã đọc.

Current skill matching:

- Case-insensitive.
- Dictionary gồm frontend, backend, fullstack, React, Next.js, Node.js, Express, FastAPI, Django, Flask, Python, Java, C#, ASP.NET Core, .NET, SQL, PostgreSQL, MySQL, MongoDB, Docker, Git, GitHub, REST API, JWT, authentication, TypeScript, JavaScript, HTML, CSS, Tailwind, Flutter, Firebase, Supabase, machine learning, AI, NLP và các skill mở rộng như Redis, GraphQL, OAuth, testing, CI/CD, cloud, SQLAlchemy, etc.
- Aliases hiện có: `js`, `ts`, `dotnet`, `postgres`, `asp net`, `asp.net`, 
extjs`, 
ext js`, 
odejs`, 
ode js`, `tailwind css`.

Scoring hiện tại:

- Nếu Sentence Transformers khả dụng:
  - skill max 45
  - keyword max 20
  - semantic max 25
  - length sanity max 10
- Nếu semantic không khả dụng:
  - skill max 65
  - keyword max 25
  - length sanity max 10
  - semantic_score = 0
- `final_score` capped at 100.

Semantic similarity:

- Model name: `all-MiniLM-L6-v2`.
- Env `SENTENCE_TRANSFORMERS_ENABLED` controls whether semantic matching is allowed. Keep it `false` on Render Free so the backend does not import/load `sentence-transformers` or torch before opening its port.
- Env `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY` mặc định true and only matters when semantic matching is enabled.
- Nếu semantic matching disabled, model không có trong local cache hoặc import/load lỗi, service fallback về rule-based scoring.
- Không download model mặc định trong production/runtime nếu local-only true.

Skill gap priority:

- Role context detect từ JD: backend, frontend, fullstack, AI hoặc general.
- Missing skills được phân loại:
  - `high_priority`
  - `medium_priority`
  - `low_priority`
- Priority dựa trên skill có trong JD, frequency/keyword, và core skills theo role context.

### `backend/app/services/roadmap_generator.py`

Chức năng:

- Tạo roadmap rule-based từ selected analysis hoặc career profile.
- Timeline parser hỗ trợ số tuần/tháng tự nhiên:
  - `1 tuần` -> 1
  - `2 tuần` -> 2
  - `1 tháng` -> 4
  - `2 tháng` -> 8
  - fallback -> 6
- Roadmap item gồm:
  - `week`
  - `focus`
  - `skills`
  - `actions`
  - `expected_output`
- Nếu có analysis, ưu tiên `prioritized_missing_skills` và `improvement_plan`.
- Nếu không có analysis, dùng career profile và core skills theo target role.

### `backend/app/services/interview_generator.py`

Chức năng:

- Tạo 5 câu hỏi MVP.
- Question bank theo role:
  - backend
  - frontend
  - fullstack
  - ai
  - general
- Nếu có analysis, missing skills có thể inject skill-specific questions trước.
- `infer_target_role` ưu tiên target role explicit, sau đó career profile, fallback `General Software Developer`.

### `backend/app/services/interview_evaluator.py`

Chức năng:

- Chấm câu trả lời bằng expected keyword overlap.
- Keyword score tối đa 80.
- Length bonus tối đa 20.
- Feedback gồm điểm mạnh, keyword thiếu, gợi ý cải thiện.
- Session summary lấy average score các câu đã trả lời.

## Currently Used

- Rule-based scoring.
- Keyword overlap.
- Semantic similarity with Sentence Transformers when available.
- Sentence Transformers model `all-MiniLM-L6-v2`.
- Skill dictionary + aliases.
- Prioritized skill gaps.
- Rule-based improvement plan.
- Rule-based roadmap generator.
- Rule-based question bank.
- Rule-based interview scoring.

## Explicitly Not Used

- OpenAI API.
- LLM API.
- Fine-tuning.
- Custom model training.
- Voice AI.
- Video interview.
- OCR phức tạp.
- Agentic workflow.
- Multi-step autonomous AI agents.
- Heavy MLOps pipeline.

## AI Output Principles

- Luôn explainable: phải có breakdown, detected skills, preview text, suggestions.
- Luôn actionable: output cần có bước cải thiện cụ thể.
- Không tuyệt đối hóa score; score là tín hiệu hỗ trợ quyết định.
- Ưu tiên fallback an toàn hơn là làm app crash khi model semantic lỗi.

## Phase 6.5 Matching Scoring V2

Resume/JD matching now adds deterministic, explainable V2 signals on top of the existing rule-based matcher:

- Role-family detection for both CV and JD: backend, frontend, fullstack, ai/data, mobile, devops and general software.
- Stack group detection, for example python_backend, dotnet_backend, react_frontend, angular_frontend, mobile and cloud/devops groups.
- Role alignment scoring to penalize obvious frontend/backend mismatch and partially penalize same-role different-stack mismatch.
- Critical JD skill weighting so role-critical skills such as Python/FastAPI in a Python backend JD matter more than generic skills such as Git.
- Evidence-aware scoring that rewards matched skills appearing near project/experience/action evidence more than one-off keyword mentions.
- Confidence signal: high, medium or low based on CV length, JD length, detected skills and evidence richness.
- Semantic similarity remains optional through Sentence Transformers and is still disabled safely when `SENTENCE_TRANSFORMERS_ENABLED=false`.

Current scoring breakdown includes `skill_score`, `keyword_score`, `semantic_score`, `role_alignment_score`, `evidence_score`, `length_sanity`, `confidence` and `final_score`, plus debug fields for detected role families, role signals, stack groups, critical skills and scoring notes.

## Phase 6.6 CareerOS Benchmark V1

CareerOS AI now has an internal benchmark folder at `docs/benchmark-v1/` for Resume/JD Matching regression review.

Benchmark V1 records 10 beta cases U01-U10 covering exact backend fit, exact frontend fit, same-role different-stack, frontend/backend mismatch, backend/frontend mismatch, cross-domain transferable profiles and non-IT mismatch.

Before changing `backend/app/services/resume_job_matcher.py`, future agents should manually rerun U01-U10 and compare results with:

- V1 baseline scores in `expected_results_v1.md`.
- V2 target ranges in `expected_results_v2.md`.
- Evaluation rules in `evaluation_notes.md`.

This benchmark does not add a new AI module, does not use LLM APIs and does not require fine-tuning. It is a product regression guardrail for the existing deterministic matcher.

## Phase 7.2 Matching Scoring V2.1

Matching V2.1 is the current benchmarked matcher baseline. It keeps the Phase 6.5 deterministic architecture and adds only small calibration:

- Negation-aware skill detection: skill mentions inside short negated clauses such as 
o C#`, 
o React`, `without Docker` or `kh?ng c? backend` do not count as matched skills.
- Negation-aware evidence scoring: negated skill mentions do not increase evidence score.
- Specialized role-family correction: mobile and ai/data profiles can become primary role family when backend signals are only generic API/auth/data overlap and no strong backend stack signal exists.

Benchmark U01-U10 now has V2.1 scores recorded in `docs/benchmark-v1/expected_results_v2.md`. Semantic similarity remains optional and was disabled for the V2.1 benchmark rerun to mirror Render Free production settings.

## Phase 7.3 Resume Feedback Engine MVP

Resume/JD analysis now includes a deterministic `resume_feedback` output. This is not an LLM rewrite system and does not rewrite the full CV.

Current behavior:

- Detects missing critical skills from JD requirements.
- Flags weak project evidence when matched skills appear shallow or keyword-level.
- Highlights missing role-critical keywords and role/stack mismatch.
- Generates safe suggested bullet templates only from evidenced skills.
- Uses conditional wording such as `If you actually used X...` when evidence is missing or uncertain.

Output groups are `critical_gaps`, `cv_wording_improvements`, `suggested_bullet_rewrites`, `missing_evidence_areas` and `recommended_next_edits`. The system remains rule-based, explainable and deterministic.

## Phase 7.4 Roadmap Quality V2

Personalized Roadmap is now an action-plan generator, not only a skill list. It remains deterministic and rule-based.

Each roadmap item can include:

- `learning_focus`
- `practice_task`
- `cv_evidence_output`
- `interview_prep`
- `priority`

When generated from analysis, the roadmap uses prioritized missing skills, critical skills, confidence, resume feedback hints, role family and stack groups. Profile-only roadmap remains supported but is labeled as lower personalization.

Safety remains explicit: no fake metrics, no claim that the user already has a missing skill, no hiring promise and no long curriculum generation.

## Phase 7.5 Mock Interview Question Bank V2

Mock Interview is now an adaptive deterministic question system.

Current behavior:

- Uses role/stack question banks for Backend .NET, Backend Node.js, Backend Python/FastAPI, Frontend React, AI/Data, Mobile Flutter and General software intern.
- Prioritizes missing or critical skills from analysis when available.
- Can use latest roadmap `interview_prep` questions as practice prompts.
- Adds question metadata: reason, related skills, category and better answer hint.
- Feedback classifies answers as too short, missing concept, missing project example, missing tradeoff, too generic or showing correct understanding.

Still not used: LLM API, voice/video interview, fine-tuning or conversational agent workflow.

## Phase 8.1 Career Taxonomy & Skill Graph Foundation

CareerOS AI now has reusable AI taxonomy foundation modules that are intentionally not integrated into production scoring yet:

- `backend/app/ai/role_taxonomy.py`
- `backend/app/ai/skill_graph.py`

Role taxonomy covers Backend Developer, Frontend Developer, Fullstack Developer, Mobile Developer, AI / Machine Learning, Data Analyst, Data Engineer, DevOps, QA / Testing and Cybersecurity. Each role includes a normalized role family, stack groups and common skills.

Skill graph stores canonical skill nodes with aliases, category and related skills. Initial coverage includes JWT, Authentication, Authorization, OAuth2, React, Next.js, TypeScript, FastAPI, REST API, Python Backend and other common CareerOS AI skill families.

Important boundary: Phase 8.1 does not change `resume_job_matcher.py`, roadmap generation, interview generation, database schema, API contract or frontend UI. Future phases should use this taxonomy in read-only/parallel mode before migrating production scoring logic.

## Phase 8.2 Taxonomy Integration Read-only Mode

CareerOS AI now uses taxonomy as a read-only knowledge layer, not as a scoring engine.

Current additions:

- `backend/app/ai/taxonomy_insights.py` normalizes skill aliases from `skill_graph.py`.
- Analysis responses include additive `taxonomy_insights` metadata with role family, stack groups, normalized skills and related skill suggestions.
- Roadmap generator can read taxonomy to normalize aliases, reduce duplicate skills and add lightweight related-skill hints.
- Interview generator normalizes missing/critical skill aliases before selecting deterministic question-bank prompts.

Important boundary:

- `match_score` and `scoring_breakdown` formulas are unchanged.
- Benchmark baseline docs are unchanged.
- Taxonomy is not a model, not an LLM layer and not a training pipeline.
- Future phases should keep taxonomy in parallel-evaluation mode until benchmark automation and real anonymized artifacts are available.

## Phase 8.3 Semantic Matching Foundation

CareerOS AI now has a dedicated semantic foundation module:

- `backend/app/ai/semantic_matcher.py`

Current behavior:

- Semantic model loading remains disabled by default for production/free-tier deploys.
- `SENTENCE_TRANSFORMERS_ENABLED=false` prevents importing/loading `sentence-transformers`.
- `SENTENCE_TRANSFORMERS_MODEL_NAME` defaults to `all-MiniLM-L6-v2` for local/dev evaluation.
- `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true` prevents accidental runtime model downloads.
- Analysis responses include additive `semantic_insights` metadata.
- The semantic insight layer is parallel/evaluation metadata and does not replace the deterministic matcher baseline.
- From Phase 8.3 onward, embedding similarity is exposed through `semantic_insights`; it should not change `match_score` or `final_score` until a future Hybrid Matching phase explicitly calibrates and benchmarks it.

Important boundary:

- No vector database.
- No embedding persistence.
- No LLM API.
- No fine-tuning.
- No benchmark baseline change.
- Hybrid scoring should wait until Phase 8.4 and must be benchmarked before affecting production behavior.
## Phase 8.4 Hybrid Matching V3 Evaluation Mode

CareerOS AI now exposes an evaluation-only hybrid matching candidate:

- `backend/app/ai/hybrid_evaluation.py`

Current behavior:

- Analysis responses include additive `hybrid_evaluation` metadata.
- Hybrid candidate combines rule-based score, semantic insight, taxonomy alignment and confidence adjustment.
- If semantic is disabled, candidate mirrors rule-based score and records the fallback reason.
- `match_score` and `scoring_breakdown.final_score` remain the production source of truth.
- The frontend labels this as `Hybrid evaluation (thử nghiệm)` and explains that it is internal/evaluation-only.

Important boundary:

- No database schema change.
- No vector database.
- No LLM API.
- No fine-tuning.
- No benchmark baseline change.
- Hybrid candidate must be benchmarked before any future phase considers using it as production score.
## Phase 8.5 Real Beta Dataset Foundation

CareerOS AI now has a dataset foundation for future AI Intelligence phases:

- `docs/datasets/` documents benchmark, beta and future training dataset formats.
- `docs/datasets/beta/` contains U011-U013 templates for future anonymized real beta cases.
- `docs/datasets/feedback_label_schema.json` defines minimal human feedback labels.
- `backend/app/ai/dataset_export.py` exports safe JSON payloads for benchmark cases, feedback labels and analysis summaries.

Current dataset export is intentionally lightweight:

- It does not export raw CV text.
- It does not export raw JD text.
- It does not export email or direct PII.
- It does not train a model.
- It does not change matcher scoring.

Founder insights now include aggregate feedback label counts:

- total feedback labels.
- agreed labels.
- disagreed labels.

Important boundary:

- Useful/not useful feedback is only a weak label.
- Human review is required before using beta labels for any trainable model.
- Phase 9.0 should not start model training until anonymized real beta cases and disagreement reviews are available.
## Phase 8.6 Synthetic Dataset Generation Foundation

CareerOS AI now has a controlled synthetic dataset foundation:

- `docs/datasets/synthetic/synthetic_cases.json` contains 70 synthetic CV/JD matching cases.
- `docs/datasets/synthetic/synthetic_case_schema.json` defines the required case format.
- `backend/scripts/generate_synthetic_dataset.py` deterministically regenerates the dataset without external API calls.

Synthetic dataset coverage:

- exact fit.
- same-role different-stack.
- role mismatch.
- cross-domain transferable.
- weak CV.
- keyword stuffing.
- non-IT mismatch.

Important boundary:

- Synthetic dataset is not real beta data.
- It contains no scraped CVs, no copied long JD text and no PII.
- It does not train a model.
- It does not change production matcher scoring.
- Future trainable matching should combine synthetic cases with anonymized real beta cases and human-reviewed disagreement labels.
## Phase 8.7 Synthetic Dataset Quality Review

Synthetic Dataset V1 now has validation and documentation guardrails:

- `backend/scripts/validate_synthetic_dataset.py` validates dataset structure, labels, ranges, group balance, PII signals and mojibake signals.
- `docs/datasets/synthetic/DATASET_CARD.md` documents purpose, generation method, intended use, limitations, privacy policy and known biases.
- `context/PHASE_8_7_DATASET_QUALITY_REPORT.md` records validation result and quality review.

Current validation status:

- 70 cases.
- 7 groups with 10 cases each.
- label distribution: 10 good, 20 medium, 20 weak, 20 mismatch.
- no blocking validation errors.
- no cleanup needed for `synthetic_cases.json` in Phase 8.7.

Important boundary:

- Synthetic dataset is still a QA supplement only.
- It should not be used alone to train or replace production scoring.
- Trainable matching requires real anonymized beta labels and human disagreement review.
## Phase 8.8 Synthetic Dataset Expansion V2

Synthetic Dataset V2 expands the internal dataset foundation:

- `docs/datasets/synthetic/synthetic_cases.json` now contains 300 deterministic synthetic cases.
- Case IDs run from `SYN001` to `SYN300`.
- `docs/datasets/synthetic/STATISTICS.md` records role, label, category and seniority distribution.
- `backend/scripts/validate_synthetic_dataset.py` now checks role and seniority coverage/balance.

Coverage added:

- Seniority: Intern, Fresher, Junior, Mid-level.
- Roles: Backend, Frontend, Fullstack, Mobile, AI, Machine Learning, Data Analyst, Data Engineer, DevOps, QA and Cybersecurity.
- Categories: exact fit, strong evidence, same-role different-stack, role mismatch, cross-domain transferable, weak CV, keyword stuffing, non-IT mismatch, career switch and missing critical skill.

Important boundary:

- Synthetic Dataset V2 is still not real beta data.
- It does not train a model.
- It does not change production matcher scoring.
- Future trainable matching should combine this data with benchmark U01-U10 and real anonymized beta labels.

## Phase 9.0 Trainable Matching Model V1

CareerOS AI now has a first trainable matching prototype in evaluation mode:

- `backend/app/ml/features.py`
- `backend/app/ml/matching_model.py`
- `backend/app/ml/evaluate_model.py`
- `backend/app/ml/matching_predictor.py`
- `backend/scripts/train_matching_model.py`

Model baseline:

- TF-IDF vectorizer.
- Logistic Regression classifier.
- Predicts `fit_label`: `good`, `medium`, `weak`, `mismatch`.
- Trained on `docs/datasets/synthetic/synthetic_cases.json`.
- Artifacts saved under `backend/models/`.

Runtime behavior:

- Analysis responses include additive `ml_evaluation` metadata.
- If artifacts are missing or fail to load, predictor returns `enabled=false` with a safe reason.
- `ml_evaluation.production_safe=false`.
- `match_score` and `scoring_breakdown.final_score` remain unchanged and remain the production source of truth.

Current limitation:

- Dataset is synthetic, not real beta data.
- Model tends to overuse `medium` for some boundary `good` and `mismatch` cases.
- Phase 9.1 should compare ML predictions against U01-U10 and anonymized beta labels before any production scoring discussion.

## Phase 9.1 ML Benchmark & Disagreement Analysis

CareerOS AI now has an evaluation script for comparing ML V1 with the existing deterministic matcher:

- `backend/scripts/run_ml_benchmark_analysis.py`
- `context/PHASE_9_1_ML_BENCHMARK_REPORT.md`
- `docs/datasets/synthetic/ml_error_analysis_v1.md`

Current findings:

- U01-U10 benchmark cases are evaluated with rule-based score, hybrid candidate and ML prediction.
- Existing ML artifacts predict `good` for U01-U10 but with low confidence, so all cases are marked 
eeds_review`.
- Synthetic test-set analysis shows the main error patterns are `good -> medium` and `mismatch -> medium`.

Important boundary:

- Phase 9.1 does not train a new model.
- ML remains an internal evaluation/disagreement signal.
- Production score remains `match_score` from the rule-based matcher.
- Hybrid candidate and ML prediction must not be presented as final user-facing truth.

## Phase 9.2 Feature Engineering & Hybrid Dataset V1

CareerOS AI hiện có hybrid feature dataset và offline hybrid model phục vụ evaluation:

- `backend/scripts/build_hybrid_training_dataset.py`
- `backend/scripts/validate_hybrid_training_dataset.py`
- `backend/scripts/train_matching_model_hybrid.py`
- `docs/datasets/synthetic/hybrid_training_dataset.json`
- `docs/datasets/synthetic/hybrid_feature_schema.json`

Nhóm feature:

- Điểm số và số lượng tín hiệu từ rule-based matcher.
- Tín hiệu taxonomy alignment và skill overlap.
- Tín hiệu semantic/hybrid metadata.
- Metadata từ synthetic dataset như seniority, category, target role và stack.

Hành vi model:

- Hybrid artifact tách riêng khỏi text-only artifact V1.
- Hybrid model dùng TF-IDF text features kết hợp DictVectorizer structured features với RandomForestClassifier baseline.
- Hybrid model chỉ dùng cho offline evaluation và chưa tích hợp vào analysis response.

Nhận định hiện tại:

- Hybrid model cải thiện accuracy và macro F1 trên synthetic test-set so với text-only V1.
- Cải thiện này nhiều khả năng đến từ rule-based teacher signals, nên chưa thể xem là ML intelligence độc lập.
- Production score vẫn là `match_score` từ rule-based matcher.

## Phase 9.3 Hybrid Model Benchmark & Ablation Study

CareerOS AI hiện có ablation study offline cho hybrid matching model:

- `backend/scripts/run_hybrid_ablation_study.py`
- `context/PHASE_9_3_ABLATION_STUDY_REPORT.md`
- `docs/datasets/synthetic/ablation_results_v1.md`
- `backend/models/hybrid_ablation_metadata.json`

Các cấu hình được so sánh:

- Text-only baseline.
- Structured không có `rule_based_score`.
- Structured core only.
- Full hybrid.

Kết quả chính trên synthetic test split:

- Text-only baseline: accuracy 0.867, macro F1 0.868.
- Structured không có `rule_based_score`: accuracy 1.000, macro F1 1.000.
- Structured core only: accuracy 0.560, macro F1 0.536.
- Full hybrid: accuracy 0.947, macro F1 0.947.

Nhận định AI:

- Hybrid model có học từ structured component features, không chỉ từ `rule_based_score`.
- Tuy nhiên synthetic dataset có thể còn quá dễ hoặc chứa leakage từ feature thiết kế.
- Kết quả ablation không đủ để productionize ML/hybrid scoring.
- Production score vẫn là rule-based `match_score`.

## Phase 10.0 AI Training Infrastructure Foundation

CareerOS AI V2 hiện có training infrastructure foundation offline:

- `backend/ml/` làm ML workspace metadata.
- `backend/app/ml/training_infra.py` parse/validate dataset, model registry, experiment và training config metadata.
- `docs/ml/` mô tả dataset versioning, model registry và experiment tracking.

Nền tảng này hỗ trợ vòng đời:

```text
Dataset -> Training -> Evaluation -> Model Registry -> Versioning -> Deployment decision
```

Ranh giới AI:

- Phase 10.0 không train model mới.
- Không thay production scoring.
- Không đưa ML/hybrid model vào runtime.
- Không thêm LLM, fine-tuning hoặc vector database.
- Registry hiện là JSON local để phục vụ quy trình AI startup ở mức MVP.

## Phase 10.1 Dataset Promotion Workflow

CareerOS AI V2 hiện có workflow promote dataset metadata có kiểm soát:

- `backend/ml/configs/dataset_promotion_config.json`
- `backend/scripts/promote_dataset_version.py`
- `docs/ml/dataset_promotion.md`

Workflow hỗ trợ:

- Dry-run để in kế hoạch promote mà không tạo file.
- Write mode tạo dataset metadata draft, không overwrite version cũ.
- Validate source dataset tồn tại và target dataset chưa tồn tại.
- Validate beta source nếu `include_beta=true`.
- Yêu cầu human review metadata nếu `require_human_review=true`.
- Scan PII/mojibake ở beta cases trước khi promotion.

Ranh giới AI:

- Không train model mới.
- Không thay production scoring.
- Không đưa dataset mới vào runtime.
- Không thêm LLM, fine-tuning hoặc vector database.

## Phase 10.2 Label Review & QA Pipeline

CareerOS AI V2 hiện có pipeline QA cho labels trước khi dataset promotion hoặc training offline:

- `backend/ml/configs/label_review_schema.json`
- `backend/ml/reviews/sample_review_cases.json`
- `backend/scripts/validate_label_review_pipeline.py`
- `docs/ml/label_review_schema.md`
- `docs/ml/label_quality.md`

AI training data rule:

- Feedback thô không được dùng trực tiếp làm training label.
- Beta labels phải được ẩn danh trước khi approved.
- Human review metadata là bắt buộc trước khi một case được xem là ready for promotion/training.
- Validator chặn PII, mojibake, status transition không hợp lệ và label confidence ngoài khoảng `0..1`.

Ranh giới AI:

- Không train model mới.
- Không thay production scoring.
- Không đưa ML/hybrid model vào runtime.
- Không thêm LLM, fine-tuning hoặc vector database.

## Phase 10.3 Dataset Assembly Pipeline

CareerOS AI V2 hiện có training dataset artifact offline:

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/datasets/training_dataset_manifest.json`
- `backend/ml/reports/training_dataset_statistics.json`
- `backend/scripts/build_training_dataset.py`

Assembly hiện gom:

- 300 synthetic cases từ Synthetic Dataset V2.
- 10 benchmark cases U01-U10.
- 0 approved beta cases vì chưa có real beta labels đã review.

AI training rule mới:

- Training script tương lai nên đọc từ `training_dataset_v3.json` thay vì đọc trực tiếp nhiều source rời rạc.
- Manifest hash là fingerprint để biết artifact có thay đổi hay không.
- Nếu có duplicate case, duplicate content hash, invalid label, PII hoặc mojibake, assembly phải fail trước khi export.

Ranh giới AI:

- Không train model mới.
- Không thay production scoring.
- Không đưa dataset artifact vào runtime.
- Không thêm LLM, fine-tuning hoặc vector database.

## Phase 10.4 Training Job Contract

CareerOS AI V2 hiện có training job contract offline:

- `docs/ml/training_job_contract.md`
- `backend/scripts/run_training_job.py`
- `backend/ml/configs/training_config.json`

AI training rule mới:

- Training script mới phải đọc từ `backend/ml/datasets/training_dataset_v3.json` và manifest.
- Training script mới không được đọc trực tiếp từ synthetic, benchmark hoặc beta raw sources.
- Manifest hash là gate bắt buộc trước khi train.
- Model version đã tồn tại thì job phải fail, không overwrite.
- Registry draft luôn `production_safe=false`.

Ranh giới AI:

- Không thay production scoring.
- Không đưa model mới vào runtime.
- Không thêm LLM, fine-tuning hoặc vector database.

## Phase 10.5 Model Registry Review Gate

CareerOS AI V2 hiện có review gate offline:

- `backend/app/ml/model_review.py`
- `backend/scripts/review_model_registry.py`
- `backend/ml/configs/model_review_config.json`
- `docs/ml/model_review_gate.md`

Gate kiểm tra:

- Registry và model artifacts.
- Dataset version/hash với manifest.
- Feature version.
- Experiment record và evaluation report.
- Accuracy, macro F1 và benchmark policy.
- Duplicate model version.
- `production_safe=false`.

AI training rule mới:

- Train xong chỉ tạo registry draft.
- Draft phải qua review gate mới được xem là candidate.
- Candidate không được tự động trở thành production.
- Phase 10.5 không train, không inference và không thay production scoring.

## Phase 10.6 Model Comparison & Deployment Decision Record

CareerOS AI V2 hiện có comparison workflow offline:

- Baseline: `rule_based_matcher_v2.1`.
- Candidate: registry có `status=candidate`.
- Evidence: evaluation metrics, benchmark results, model review outcome, dataset version/hash và known limitations.
- Output: comparison status, risk level, recommendation và decision record.

AI governance rule mới:

- Candidate không đồng nghĩa production.
- Metrics classifier không được đánh đồng với production `match_score`.
- Thiếu candidate hoặc thiếu evidence phải giữ baseline/shadow.
- `production_change_allowed` luôn là `false` trong Phase 10.6.
- Không train, inference, deploy hoặc thay runtime matcher.

## Phase 10.7 Release Readiness & Audit Trail

CareerOS AI V2 hiện có audit pipeline offline:

- Xác minh dataset version/hash và approved labels.
- Xác minh training config, experiment, evaluation và model artifacts.
- Xác minh review PASS, registry candidate và deployment decision.
- Xác minh quality evidence, UTF-8, mojibake và PII.
- Xác minh `production_safe=false` và `production_change_allowed=false`.

AI governance rule mới:

- Release Ready chỉ mô tả mức sẵn sàng offline.
- Audit không cấp quyền deploy hoặc thay runtime.
- Audit FAIL vẫn được ghi để giữ lịch sử trung thực.
- Không có model nào được xem là production chỉ vì checklist PASS.

## Phase 11.0 Shadow Evaluation Architecture

CareerOS AI V2 hiện có shadow planning layer offline:

- Config mặc định disabled.
- Safety validator khóa user-facing output và raw text storage.
- Candidate check yêu cầu registry status candidate, version khớp và `production_safe=false`.
- No-candidate behavior hạ plan về disabled với WARNING.
- Future disagreement schema chỉ lưu metadata tối thiểu.

AI runtime boundary:

- Production vẫn dùng `rule_based_matcher_v2.1`.
- Không có shadow inference trong request path.
- Không thay `match_score`, `final_score`, suggestion hoặc generated content.
- `runtime_activation_allowed=false` trong mọi plan Phase 11.0.

## Phase 11.1 Offline Shadow Evaluation Harness

CareerOS AI V2 hiện có offline harness:

- Đọc `training_dataset_v3.json`, gồm synthetic và benchmark cases.
- Chạy rule-based matcher trên summary text offline.
- Chỉ load candidate model từ registry `status=candidate`.
- So sánh expected/rule/hybrid/ML labels.
- Tính agreement, disagreement, confidence, confusion và review-required signals.
- Không lưu raw resume/JD summaries trong report.

AI boundary:

- No-candidate trả `baseline_only` và `keep baseline`.
- Không tự dùng model prototype Phase 9 làm candidate.
- Không thay `match_score`, `final_score` hoặc user-facing response.
- `production_change_allowed=false`.

## Phase 11.2 Shadow Disagreement Review Queue

CareerOS AI V2 hiện có offline disagreement triage:

- Input từ `shadow_summary.json`.
- Chỉ lấy comparison records có `review_required=true`.
- Phân loại disagreement type và severity deterministic.
- Không lưu raw text hoặc PII.
- Queue item bắt đầu ở `pending`.
- Human-reviewed item có thể bàn giao sang Label Review Pipeline.

AI data boundary:

- `approved_for_training=false` trong toàn bộ shadow queue.
- `approved_for_label_review` không đồng nghĩa training approval.
- Disagreement không được dùng trực tiếp làm training label.
- Dataset promotion vẫn phải đi qua label review/anonymization workflow.

## Phase 11.3 Shadow Review Resolution Export

CareerOS AI V2 hiện có offline resolution handoff:

- Input từ `shadow_review_queue.json`.
- Chỉ lấy items đã `promoted_to_label_review`.
- Tạo resolution metadata và Label Review Draft cases.
- Draft dùng transition `ANONYMIZED -> UNDER_REVIEW`.
- Label Review validator hiện có chấp nhận draft output.

AI data boundary:

- `approved_for_label_review=true` chỉ cho phép vào Label Review Pipeline.
- `approved_for_training=false` luôn được giữ.
- Không tự động tạo APPROVED/PROMOTED/TRAINABLE status.
- Không export raw CV/JD text hoặc PII.

## Phase 11.4 Label Review Draft QA Bridge

CareerOS AI V2 hiện có QA bridge:

- Input từ `shadow_label_review_draft.json`.
- Tái sử dụng Label Review validator Phase 10.2.
- Tách rõ ready-for-review và ready-for-promotion.
- Tổng hợp promotion blockers deterministic.
- Kiểm tra input immutability trong CLI.

AI data boundary:

- QA report không sửa label hoặc workflow status.
- `promotion_allowed=false`.
- `training_allowed=false`.
- Không tự động promotion hoặc training.

## Phase 11.5 Dataset Promotion Planning Bridge

CareerOS AI V2 hiện có promotion planning layer:

- Input từ Shadow Label Review Draft QA report.
- Follow `source_draft` để fresh validation.
- Đối chiếu current dataset manifest.
- Sinh target dataset version và estimated size.
- Phân loại ready/blocked cases và blockers.

AI data boundary:

- `promotion_allowed` chỉ là evidence flag.
- `promotion_executed=false`.
- `training_allowed=false`.
- Không tạo dataset version hoặc model artifact.
