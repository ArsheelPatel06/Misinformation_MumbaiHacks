# 🚀 Deployment Guide for DeepCheck MH

This guide helps you deploy the DeepCheck MH application to the web.

## 1. Backend Deployment (Render)

We recommend using **Render** for the Python backend as it's free and easy to set up.

1.  Push your code to GitHub.
2.  Sign up at [render.com](https://render.com).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Settings**:
    *   **Name**: `deepcheck-api`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
6.  **Environment Variables**:
    *   Add `GEMINI_API_KEY` (your key)
    *   Add `OPENAI_API_KEY` (your key)
    *   Add `DATABASE_URL` (optional, defaults to local sqlite if not set, but for production use Render's PostgreSQL)

## 2. Frontend Deployment (Netlify - Recommended)

We recommend **Netlify** as it handles React routing automatically with our configuration.

1.  Push your code to GitHub.
2.  Sign up at [netlify.com](https://netlify.com).
3.  Click **Add new site** -> **Import from Git**.
4.  Connect your GitHub repository.
5.  **Settings** (Netlify should detect these automatically from `netlify.toml`):
    *   **Base directory**: `frontend`
    *   **Build command**: `npm run build`
    *   **Publish directory**: `frontend/dist`
6.  **Deploy**.

## 3. Frontend Deployment (GitHub Pages - Alternative)

If you prefer GitHub Pages:

1.  Open `frontend/vite.config.js` and add `base: '/repo-name/',` (replace `repo-name` with your GitHub repo name).
2.  Install `gh-pages`:
    ```bash
    cd frontend
    npm install gh-pages --save-dev
    ```
3.  Add scripts to `frontend/package.json`:
    ```json
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
    ```
4.  Run `npm run deploy`.
5.  **Note**: GitHub Pages does not support SPA routing (e.g., `/dashboard`) natively on refresh without a hack (404.html trick). Netlify is preferred for this reason.

## 4. Connecting Frontend to Backend

## 3. Connecting Frontend to Backend

Once both are deployed:
1.  Get your Backend URL from Render (e.g., `https://deepcheck-api.onrender.com`).
2.  Update `frontend/vercel.json` (or your frontend code) to point to this URL instead of `localhost:8000`.
    *   *Note: The current `vercel.json` has a placeholder `https://your-backend-url.onrender.com`. You should update this before deploying or configure a rewrite rule in Vercel settings.*

## 4. Database (Production)

For a persistent database in production:
1.  Create a **PostgreSQL** database on Render.
2.  Copy the `Internal Database URL`.
3.  Add it as `DATABASE_URL` in your Backend Web Service environment variables.
