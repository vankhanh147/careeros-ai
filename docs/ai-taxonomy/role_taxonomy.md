# Role Taxonomy

Role taxonomy chuẩn hóa các nhóm nghề nghiệp công nghệ mà CareerOS AI cần hiểu trong các phase AI Intelligence tiếp theo.

| Role | Role family | Stack groups | Common skills |
| --- | --- | --- | --- |
| Backend Developer | backend | dotnet_backend, python_backend, node_backend, java_backend, database_backend | REST API, authentication, JWT, OAuth2, SQL, PostgreSQL, FastAPI, Node.js, ASP.NET Core, Docker |
| Frontend Developer | frontend | react_frontend, nextjs_frontend, angular_frontend, vue_frontend, web_ui | HTML, CSS, JavaScript, TypeScript, React, Next.js, Tailwind CSS, REST API integration |
| Fullstack Developer | fullstack | frontend + backend stacks | React, Next.js, Node.js, FastAPI, REST API, authentication, SQL, PostgreSQL, Docker |
| Mobile Developer | mobile | flutter_mobile, react_native_mobile, android_native, ios_native | Flutter, Dart, React Native, Kotlin, Swift, Firebase, mobile UI, REST API integration |
| AI / Machine Learning | ai/data | python_ml, nlp, computer_vision, data_science | Python, machine learning, scikit-learn, pandas, NumPy, PyTorch, TensorFlow, NLP |
| Data Analyst | data | analytics_sql, bi_reporting, python_analysis | SQL, Excel, Power BI, Tableau, pandas, data cleaning, data visualization |
| Data Engineer | data | data_pipeline, warehouse, cloud_data | SQL, Python, ETL, data pipeline, data warehouse, Spark, Airflow, dbt |
| DevOps | devops | container_platform, cloud_infra, ci_cd, linux_ops | Linux, Docker, Kubernetes, CI/CD, Terraform, AWS, Azure, GCP |
| QA / Testing | qa/testing | manual_testing, automation_testing, api_testing | test case design, manual testing, API testing, Postman, pytest, Playwright, Cypress |
| Cybersecurity | cybersecurity | application_security, network_security, security_operations | OWASP Top 10, authentication, authorization, network security, Linux, vulnerability assessment |

## Ghi chú triển khai

- Source of truth trong code: `backend/app/ai/role_taxonomy.py`.
- Role taxonomy chưa được tích hợp vào matcher hiện tại.
- Future phases có thể dùng taxonomy này để giảm trùng lặp giữa matching, roadmap và interview.