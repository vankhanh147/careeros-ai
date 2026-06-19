# Skill Graph

Skill graph chuẩn hóa kỹ năng, alias và quan hệ giữa các kỹ năng để CareerOS AI có thể hiểu skill gap tốt hơn trong các phase sau.

## Ví dụ nhóm kỹ năng

### Authentication / Security

- JWT
  - aliases: json web token, jwt token, access token
  - related: Authentication, Authorization, OAuth2, REST API, API security
- Authentication
  - aliases: auth, login system, sign in, identity
  - related: JWT, Authorization, OAuth2, password hashing
- Authorization
  - aliases: access control, permission, role-based access, RBAC
  - related: Authentication, JWT, OAuth2, API security
- OAuth2
  - aliases: oauth, oauth 2, social login
  - related: Authentication, Authorization, JWT, OpenID Connect

### Frontend

- React
  - aliases: reactjs, react.js
  - related: Next.js, TypeScript, JavaScript, component state, REST API integration
- Next.js
  - aliases: nextjs, next js
  - related: React, TypeScript, App Router, server rendering, Vercel
- TypeScript
  - aliases: ts
  - related: JavaScript, React, Next.js, type safety

### Backend

- FastAPI
  - aliases: fast api
  - related: Python, REST API, Python Backend, Pydantic, SQLAlchemy
- REST API
  - aliases: rest, restful api, api endpoint, web api
  - related: FastAPI, ASP.NET Core, Node.js, Authentication, API design
- Python Backend
  - aliases: python api, backend python, python web backend
  - related: Python, FastAPI, Django, Flask, SQLAlchemy, REST API

## Ghi chú triển khai

- Source of truth trong code: `backend/app/ai/skill_graph.py`.
- Skill graph chưa được tích hợp vào production matcher.
- Phase 8.2 có thể dùng skill graph để normalize aliases và mở rộng related skills một cách kiểm soát.