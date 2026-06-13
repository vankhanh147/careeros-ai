# CareerOS AI Frontend

Next.js frontend scaffold for CareerOS AI.

## Local development

```bash
npm install
npm run dev
```

Frontend URL: `http://localhost:3000`

Create `.env` from `.env.example` and point it to the backend:

```text
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

## Vercel deployment

Use `frontend/` as the Vercel project root.

Build command:

```bash
npm run build
```

Required Vercel environment variable:

```text
NEXT_PUBLIC_API_URL="https://your-render-backend-url.onrender.com"
```

Do not point production frontend builds to `localhost`. The backend URL must be the deployed Render service URL.

## Checks

```bash
npm run lint
npm run build
```
