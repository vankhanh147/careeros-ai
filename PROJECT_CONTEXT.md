PROJECT_CONTEXT.md
Xây dựng nền tảng AI hỗ trợ định hướng nghề nghiệp trong lĩnh vực công nghệ – CareerOS AI
________________________________________
01. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)
1.1 Giới thiệu dự án
CareerOS AI là nền tảng ứng dụng trí tuệ nhân tạo (AI) nhằm hỗ trợ người dùng trong lĩnh vực công nghệ xác định định hướng nghề nghiệp, đánh giá mức độ phù hợp với công việc, cải thiện kỹ năng và tăng khả năng đạt Internship hoặc Job Offer.
Hệ thống được xây dựng với mục tiêu giải quyết khoảng cách giữa:
Kiến thức học tập
→
Yêu cầu thực tế của thị trường tuyển dụng
CareerOS AI không phải là một website tuyển dụng (job board) hay chỉ là công cụ tạo CV thông thường.
Thay vào đó, hệ thống hoạt động như một:
AI Career Operating System (Hệ điều hành AI cho sự nghiệp)
giúp người dùng:
•	Hiểu năng lực hiện tại
•	Biết mình phù hợp với vị trí nào
•	Xác định kỹ năng còn thiếu
•	Nhận lộ trình học cá nhân hóa
•	Chuẩn bị phỏng vấn kỹ thuật
•	Tăng khả năng được tuyển dụng
Mục tiêu dài hạn là xây dựng một nền tảng AI đồng hành cùng người dùng trong suốt quá trình phát triển nghề nghiệp.
________________________________________
1.2 Bài toán dự án giải quyết
Trong lĩnh vực công nghệ, người học thường gặp các vấn đề sau:
Không biết nên học gì tiếp theo
Người học thường bị quá tải thông tin:
•	Roadmap trên Internet quá nhiều
•	Nội dung học thiếu thứ tự ưu tiên
•	Không biết công nghệ nào thực sự cần thiết
Ví dụ:
Một người muốn trở thành Backend Developer thường không biết:
Học REST API trước hay Docker?
Có cần Redis không?
Có nên học Kubernetes quá sớm?
Điều này dẫn đến:
Học lan man
Không đủ chiều sâu
Mất định hướng
________________________________________
CV không phản ánh đúng năng lực
Nhiều người có project tốt nhưng không biết cách trình bày.
Ví dụ:
CV ghi:
Made booking website
trong khi recruiter mong đợi:
Developed a full-stack booking platform using ASP.NET Core, PostgreSQL, JWT Authentication, and recommendation features.
Điều này làm giảm khả năng vượt qua CV screening.
________________________________________
Apply công việc không phù hợp
Người dùng thường apply theo cảm tính.
Ví dụ:
Apply AI Engineer Intern
nhưng:
Không biết Python
Không có project ML
Không có model training experience
Điều này dẫn đến:
Rejected
Mất tự tin
Không biết nguyên nhân
________________________________________
Không biết chuẩn bị phỏng vấn như thế nào
Nhiều người không biết:
•	Nhà tuyển dụng hỏi gì
•	Độ sâu kiến thức cần tới đâu
•	Điểm yếu của bản thân là gì
CareerOS AI giúp mô phỏng quá trình phỏng vấn kỹ thuật để người dùng chuẩn bị tốt hơn.
________________________________________
1.3 Mục tiêu sản phẩm
CareerOS AI hướng tới các mục tiêu chính:
Mục tiêu ngắn hạn (MVP)
Giúp người dùng:
Hiểu bản thân đang ở đâu
Biết mình thiếu gì
Biết nên học gì tiếp theo
Tăng khả năng có internship/job
________________________________________
Mục tiêu trung hạn
Xây dựng hệ thống có khả năng:
•	Phân tích thị trường tuyển dụng
•	Cá nhân hóa roadmap học tập
•	Theo dõi tiến bộ người dùng
•	Đề xuất career path phù hợp
________________________________________
Mục tiêu dài hạn
CareerOS AI hướng tới trở thành:
AI Operating System for Career Growth
Một nền tảng AI hỗ trợ người dùng trong toàn bộ hành trình nghề nghiệp.
________________________________________
1.4 Định vị sản phẩm (Product Positioning)
CareerOS AI được định vị là:
Nền tảng AI hỗ trợ định hướng và phát triển nghề nghiệp trong lĩnh vực công nghệ.
CareerOS AI không phải là:
1. Website tuyển dụng
Không cạnh tranh trực tiếp với:
LinkedIn Jobs
TopCV
ITviec
VietnamWorks
Giá trị cốt lõi của CareerOS AI là:
Tăng Employability (khả năng được tuyển dụng)
________________________________________
2. CV Builder đơn thuần
CareerOS AI không chỉ tạo CV.
Hệ thống tập trung vào:
Resume Intelligence
Job Matching
Skill Gap Detection
Career Recommendation
Mock Interview
________________________________________
3. Chatbot AI generic
CareerOS AI không phải chatbot tổng quát.
AI của hệ thống được tối ưu riêng cho:
Career Development
Technology Hiring
Developer Skills
Technical Interview
Learning Roadmap
________________________________________
1.5 Đối tượng người dùng mục tiêu (Target Users)
Phiên bản đầu tiên (MVP v1) tập trung vào niche:
Người học và người mới phát triển sự nghiệp trong lĩnh vực công nghệ
Bao gồm:
Nhóm 1 — Sinh viên công nghệ
Ví dụ:
IT Student
Computer Science Student
Software Engineering Student
Mục tiêu:
Internship
Junior Position
________________________________________
Nhóm 2 — Fresher / Junior
Những người:
Mới ra trường
Ít kinh nghiệm
Chưa rõ career direction
________________________________________
Nhóm 3 — Career Switcher
Những người:
Chuyển ngành sang công nghệ
Muốn bắt đầu software engineering
________________________________________
1.6 Tầm nhìn phát triển sản phẩm (Vision)
CareerOS AI được xây dựng theo chiến lược:
Start Small → Dominate Niche → Scale
Giai đoạn 1
Tập trung:
IT Students
Fresher Developers
________________________________________
Giai đoạn 2
Mở rộng:
Junior Engineers
Career Growth
Promotion Readiness
________________________________________
Giai đoạn 3
Mở rộng đa lĩnh vực:
Business
Marketing
Finance
Design
Education
________________________________________
Vision dài hạn
CareerOS AI hướng tới:
“LinkedIn + AI Career Coach + Personalized Learning System”
trong một nền tảng duy nhất.
________________________________________
1.7 Phạm vi sản phẩm giai đoạn đầu (MVP Scope)
CareerOS AI MVP tập trung vào 5 tính năng cốt lõi:
1. Career Diagnosis
Phân tích:
Skill hiện tại
Project đã làm
Mục tiêu nghề nghiệp
Output:
Best-fit role
Strengths
Weaknesses
Readiness score
________________________________________
2. Resume ↔ Job Matching
Input:
CV PDF
Job Description
Output:
Match Score
Missing Skills
Resume Feedback
Optimization Suggestions
________________________________________
3. Skill Gap Detection
AI xác định:
Người dùng đang thiếu kỹ năng gì
Nên học gì tiếp theo
Ưu tiên học cái nào trước
________________________________________
4. Personalized Roadmap
Ví dụ:
Goal:
Backend Intern trong 3 tháng
Output:
Roadmap học tập cá nhân hóa
________________________________________
5. Mock Interview AI
AI mô phỏng:
Technical Interview
Behavioral Interview
Role-specific Interview
và đánh giá mức độ sẵn sàng của người dùng.

02. CORE FEATURES
2.1 Tổng quan tính năng
CareerOS AI tập trung vào việc tăng khả năng được tuyển dụng (Employability) thông qua các hệ thống AI hỗ trợ định hướng nghề nghiệp.
MVP v1 bao gồm 5 tính năng cốt lõi:
1.	Career Diagnosis
2.	Resume ↔ Job Matching
3.	Skill Gap Detection
4.	Personalized Roadmap
5.	Mock Interview AI
Các tính năng được thiết kế theo nguyên tắc:
Actionable AI
Tức là:
AI không chỉ phân tích mà phải đưa ra:
Recommendation
Priority
Improvement Suggestion
Next Action
________________________________________
2.2 Career Diagnosis
Mục tiêu
Giúp người dùng hiểu:
“Hiện tại tôi đang ở đâu?”
và:
“Tôi phù hợp với hướng nào nhất?”
________________________________________
Input
Người dùng cung cấp:
Current Skills
Programming Languages
Frameworks
Projects
Experience Level
Target Role
Timeline
Ví dụ:
C#
ASP.NET Core
Flutter
PostgreSQL
SmartStay Project
Target: Backend Intern
Timeline: 3 months
________________________________________
Output
Hệ thống trả về:
Best-fit role
Readiness score
Strengths
Weaknesses
Suggested direction
Ví dụ:
Best-fit:
Backend Intern (82%)

Alternative:
Fullstack Intern (75%)

Weakness:
Docker
Testing
Redis
________________________________________
Business Value
Giúp người dùng:
•	tránh học lan man
•	chọn đúng direction
•	hiểu điểm mạnh/yếu
________________________________________
2.3 Resume ↔ Job Matching
Mục tiêu
Đánh giá:
CV hiện tại phù hợp với Job Description ở mức nào
________________________________________
Input
Người dùng upload:
Resume PDF
và paste:
Job Description
________________________________________
Output
Hệ thống trả về:
Match Score
Missing Skills
Resume Strength
Resume Weakness
Optimization Suggestions
Ví dụ:
Match Score:
72%

Missing:
Docker
CI/CD
Testing

Strong:
ASP.NET Core
JWT
PostgreSQL
________________________________________
Core Idea
Không chỉ keyword matching.
Hệ thống đánh giá:
Semantic Similarity
Skill Overlap
Project Relevance
Role Alignment
________________________________________
Business Value
Giúp người dùng:
Apply đúng job hơn
Biết lý do bị reject
Tối ưu CV
________________________________________
2.4 Skill Gap Detection
Mục tiêu
Xác định:
Người dùng đang thiếu gì để đạt mục tiêu nghề nghiệp
________________________________________
Input
Current Skill Set
Target Role
Job Market Requirement
________________________________________
Output
Ví dụ:
Target:
Backend Intern
Current Skill:
C#
SQL
Basic API
Result:
Missing Skills:
Docker
Testing
PostgreSQL
Authentication
Priority:
1. REST API
2. PostgreSQL
3. JWT
4. Docker
________________________________________
Business Value
Thay vì học ngẫu nhiên:
Người dùng học:
đúng thứ có impact lớn nhất
________________________________________
2.5 Personalized Roadmap
Mục tiêu
Tạo roadmap học tập cá nhân hóa.
Khác với roadmap chung trên Internet.
________________________________________
Input
Current Skill
Target Role
Available Time
Timeline
Weak Areas
________________________________________
Output
Ví dụ:
Goal:
Backend Intern in 3 months
Roadmap:
Week 1–2:
REST API
HTTP
CRUD

Week 3–4:
PostgreSQL
Database Design

Week 5–6:
JWT
Authentication

Week 7–8:
Docker
Deployment
________________________________________
Business Value
Giúp người dùng:
Không học lan man
Tăng tốc progression
Tối ưu thời gian
________________________________________
2.6 Mock Interview AI
Mục tiêu
Giúp người dùng:
Practice before real interview
________________________________________
Interview Types
Technical Interview
Ví dụ:
JWT là gì?
REST API khác GraphQL thế nào?
SQL JOIN là gì?
________________________________________
Behavioral Interview
Ví dụ:
Giới thiệu bản thân
Điểm mạnh yếu
Conflict resolution
________________________________________
Role-specific Interview
Ví dụ:
Backend Intern
Frontend Intern
AI Engineer Intern
Mobile Developer
________________________________________
Output
Sau mỗi session:
AI đánh giá:
Strength
Weakness
Missing Knowledge
Suggested Improvement
Follow-up Questions
Ví dụ:
Score:
7/10

Weak:
Refresh Token

Recommendation:
Review JWT lifecycle
________________________________________
2.7 Future Features (Không thuộc MVP)
Các tính năng sau chưa thuộc MVP nhưng nằm trong roadmap dài hạn.
Portfolio Intelligence
AI đánh giá:
GitHub
Project Quality
Architecture Readiness
________________________________________
Career Market Intelligence
Phân tích:
Top skills in demand
Salary trend
Role demand
________________________________________
Interview Success Prediction
Ví dụ:
Interview Probability:
68%
________________________________________
AI Career Coach
AI hỗ trợ:
Career planning
Skill prioritization
Long-term strategy
________________________________________
03. AI OVERVIEW
3.1 Vai trò của AI trong hệ thống
AI là phần cốt lõi của CareerOS AI.
Tuy nhiên:
AI chỉ hỗ trợ decision-making, không thay thế hoàn toàn người dùng.
Nguyên tắc:
AI Suggestion
≠
Absolute Truth
________________________________________
3.2 AI dùng để làm gì
Resume Matching
Đánh giá:
CV ↔ Job Fit
________________________________________
Skill Gap Analysis
Phân tích:
Missing Skills
Learning Priority
________________________________________
Roadmap Recommendation
Sinh roadmap cá nhân hóa.
________________________________________
Mock Interview Evaluation
Đánh giá câu trả lời.
________________________________________
Career Recommendation
Đề xuất role phù hợp.
Ví dụ:
Backend Intern
Frontend Intern
AI Developer
________________________________________
3.3 AI Principles
CareerOS AI tuân theo nguyên tắc:
Explainable AI
AI phải giải thích được:
Vì sao đưa ra recommendation.
________________________________________
Actionable AI
AI luôn phải có:
Next Step
Priority
Improvement Suggestion
________________________________________
Domain-Specific AI
AI chỉ tối ưu cho:
Technology Career
Software Engineering
Internship Preparation
Không phải chatbot đa năng.
________________________________________
3.4 AI Evolution Strategy
Phase 1
Pretrained Models
Sentence Transformers
Rule-based Scoring
________________________________________
Phase 2
User Feedback Learning
________________________________________
Phase 3
Ranking Model Training
________________________________________
Phase 4
Personalized Career Intelligence
________________________________________
04. HIGH-LEVEL ARCHITECTURE
System Architecture
Frontend (Next.js)

        ↓

Backend API (FastAPI)

        ↓

AI Engine (Python)

        ↓

Database (PostgreSQL)

        ↓

Storage (Supabase Storage)
________________________________________
Frontend
Responsible for:
User Interface
Dashboard
Upload CV
Roadmap UI
Interview UI
________________________________________
Backend API
Responsible for:
Authentication
Business Logic
API Orchestration
Data Management
________________________________________
AI Engine
Responsible for:
Resume Analysis
Matching
Recommendation
Evaluation
________________________________________
Database
Responsible for:
Users
Resume Data
Interview Session
Career Progress
Feedback
________________________________________
05. TECH STACK
Frontend
Next.js
React
TypeScript
Tailwind CSS
________________________________________
Backend
FastAPI
Python
Pydantic
SQLAlchemy
JWT Authentication
________________________________________
AI / ML
Sentence Transformers
Scikit-learn
LightGBM (future)
Open-source Models
________________________________________
Database
PostgreSQL
Supabase
________________________________________
Storage
Supabase Storage
________________________________________
Deployment
Frontend:
Vercel

Backend:
Render

Database:
Supabase

06. DATA & TRAINING STRATEGY
6.1 Nguyên tắc phát triển AI
CareerOS AI không xây dựng AI theo hướng:
“Train model lớn ngay từ đầu”
Thay vào đó, hệ thống phát triển theo hướng:
MVP First → Real User Data → Continuous Learning
Lý do:
•	Không có dữ liệu thật ở giai đoạn đầu
•	Tránh over-engineering
•	Tối ưu tốc độ build MVP
•	Có thể deploy sớm để lấy user thật
Chiến lược AI:
Version 1:
Pretrained Models

Version 2:
Feedback Collection

Version 3:
Train Ranking Models

Version 4:
Personalized AI
________________________________________
6.2 Nguồn dữ liệu
CareerOS AI sử dụng 3 nguồn dữ liệu chính.
1. User-Generated Data
Dữ liệu do người dùng tạo ra.
Ví dụ:
Resume
Skill Profile
Target Role
Learning Progress
Interview Answers
Feedback
Ví dụ dữ liệu:
User:
Backend Intern

Current Skill:
C#
SQL
Basic API

Target:
Backend Developer
________________________________________
2. Job Market Data
Dữ liệu Job Description.
Nguồn:
LinkedIn
ITviec
TopCV
VietnamWorks
Company Career Page
Dữ liệu thu thập:
Job Title
Required Skills
Preferred Skills
Role Description
Experience Level
Technology Stack
Mục tiêu:
hiểu thị trường tuyển dụng thực tế.
________________________________________
3. Synthetic Data (Initial Stage)
Ở giai đoạn đầu chưa có nhiều user thật.
Cho phép sử dụng:
Synthetic Training Data
Ví dụ:
CV:
ASP.NET Core
JWT
PostgreSQL
JD:
Backend Intern
REST API
PostgreSQL
Docker
Label:
Match:
78%

Missing:
Docker
Mục tiêu:
bootstrap system trước khi có user thật.
________________________________________
6.3 AI Training Strategy
Phase 1 — Pretrained AI
Không tự train model lớn.
Sử dụng:
Sentence Transformers
Scikit-learn
Rule-based scoring
Mục tiêu:
Fast MVP
Deploy quickly
Get user feedback
________________________________________
Phase 2 — Feedback Learning
Hệ thống bắt đầu học từ:
User interaction
User feedback
Resume improvement
Interview result
Ví dụ:
User chọn:
Useful recommendation
Not useful recommendation
________________________________________
Phase 3 — Ranking Model Training
Khi có đủ dữ liệu.
Train:
Ranking Model
Mục tiêu:
CV ↔ Job Matching
Skill Recommendation
Career Recommendation
Roadmap Personalization
________________________________________
Phase 4 — Personalized Career Intelligence
AI học từ:
Behavior
Career progression
Learning outcome
Hiring success
để cá nhân hóa sâu hơn.
________________________________________
6.4 Training Philosophy
Nguyên tắc:
Không train AI chỉ để “cho có AI”
Chỉ train model khi:
Có đủ dữ liệu
Có measurable value
Có business impact
Tránh:
Train model phức tạp nhưng không improve UX
________________________________________
07. DEVELOPMENT PRINCIPLES
7.1 Development Philosophy
CareerOS AI được xây dựng theo mindset:
Startup-ready, production-first
Không phải:
Academic-only project
Không phải:
Demo-only application
Mà là:
Real product for real users
________________________________________
7.2 MVP First
Nguyên tắc quan trọng nhất:
Build MVP first.
Không over-engineer.
Không thêm feature không cần thiết.
Ưu tiên:
Simple
Working
Deployable
Maintainable
________________________________________
7.3 Do Not Over-Engineer
Không xây quá phức tạp sớm.
Ví dụ:
Không cần ngay
Microservices
Kubernetes
Event Streaming
Complex MLOps
Distributed Systems
Ưu tiên
Monolithic FastAPI
Clean Architecture
Modular Design
________________________________________
7.4 Production-Ready Code
Code phải:
Readable
Maintainable
Scalable
Consistent
Ưu tiên:
Clean code
Strong naming
Type safety
Validation
Error handling
________________________________________
7.5 Modular Architecture
Tách module rõ ràng.
Ví dụ:
Auth
Resume
Matching
Roadmap
Interview
AI
Tránh:
God service
Huge files
Messy dependency
________________________________________
7.6 User-Centric Development
Mọi feature phải trả lời:
Feature này giúp user tốt hơn ở đâu?
Nếu không có clear value:
không build.
________________________________________
7.7 AI Explainability
AI phải giải thích được:
Why?
Ví dụ:
Không chỉ:
Match Score:
65%
Mà phải:
Low because:
Missing Docker
Weak Database Experience
Project mismatch
________________________________________
08. MVP SCOPE
Những gì CareerOS AI sẽ làm ở MVP
Included Features
Authentication
Register
Login
JWT Authentication
User Profile
________________________________________
Career Diagnosis
Role recommendation
Readiness score
________________________________________
Resume ↔ Job Matching
Upload Resume PDF
Paste Job Description
AI Analysis
________________________________________
Skill Gap Detection
Missing skill
Priority recommendation
________________________________________
Personalized Roadmap
Goal-based learning roadmap
________________________________________
Mock Interview AI
Question
Answer
Evaluation
Feedback
________________________________________
Dashboard
Career Progress
History
Saved Analysis
________________________________________
MVP Goal
Mục tiêu MVP:
Get real users and validate problem-solution fit
Không phải:
Perfect AI
________________________________________
09. NON-GOALS
Các tính năng sau:
KHÔNG thuộc MVP
Job Marketplace
Không build:
Job board
Recruitment platform
________________________________________
Video Interview
Không build:
Zoom-like interview
Live AI avatar
________________________________________
Complex AI Training
Không build:
LLM fine-tuning
Custom foundation model
________________________________________
Enterprise Features
Không build:
Company dashboard
Recruiter panel
HR management
________________________________________
Payment System
Không build ở phase đầu.
________________________________________
Reason
MVP phải:
Focused
Fast to launch
Easy to validate
________________________________________
10. INSTRUCTIONS FOR CODEX
General Rules
Always prioritize:
Simple
Clean
Maintainable
Production-ready
________________________________________
Architecture Rules
Follow project architecture strictly:
Frontend:
Next.js

Backend:
FastAPI

Database:
PostgreSQL (Supabase)

Storage:
Supabase Storage
Do not change architecture without reason.
________________________________________
AI Rules
Do not overcomplicate AI.
Prefer:
Pretrained models
Sentence Transformers
Scikit-learn
Avoid:
Unnecessary deep learning
Over-engineered ML pipeline
________________________________________
Coding Rules
Prefer:
Clean folder structure
Reusable service
Validation
Error handling
Typed schema
Avoid:
Messy architecture
Duplicate logic
Large files
________________________________________
Product Rules
CareerOS AI is:
Career Intelligence Platform
Not:
Generic chatbot
Job board
Resume builder only
Always prioritize:
Employability improvement
Actionable recommendation
User value
________________________________________
MVP Priority
Always prioritize:
Working MVP
Deployment
Real user feedback
instead of:
Complex architecture
Fancy feature
Premature optimization

