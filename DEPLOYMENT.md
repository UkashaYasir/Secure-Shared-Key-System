# Deploying Secure Shared Key System to Render

This guide will walk you through deploying your Flask application to Render.com for free.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account to host your code.
2.  **Render Account**: Sign up at [render.com](https://render.com) (you can sign up with GitHub).
3.  **Supabase Project**: You should already have this from development. You will need your `SUPABASE_URL` and `SUPABASE_KEY`.

## Step 1: Push Code to GitHub

If you haven't already, push your code to a new GitHub repository.

1.  Create a new repository on GitHub.
2.  Open your terminal in the project folder and run:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git push -u origin main
    ```
    *(Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual details)*

## Step 2: Create a Web Service on Render

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click the "New +" button and select **Web Service**.
3.  Connect your GitHub account if prompted.
4.  Search for your repository and click **Connect**.

## Step 3: Configure the Service

Fill in the details:

*   **Name**: `secure-shared-key-system` (or any name you like)
*   **Region**: Choose the one closest to you.
*   **Branch**: `main`
*   **Root Directory**: Leave blank (it's in the root).
*   **Runtime**: **Python 3**
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `gunicorn app:app`
*   **Instance Type**: **Free**

## Step 4: Environment Variables

**Crucial Step**: You need to add your Supabase credentials so the app can connect to the database.

1.  Scroll down to the **Environment Variables** section on the setup page (or go to the "Environment" tab later).
2.  Add the following variables (copy values from your local `.env` file):

    *   **Key**: `SUPABASE_URL`
    *   **Value**: `your_supabase_url_here`

    *   **Key**: `SUPABASE_KEY`
    *   **Value**: `your_supabase_key_here`

    *   **Key**: `SECRET_KEY`
    *   **Value**: `generate_a_random_string_here` (You can mash your keyboard for this one, e.g., `hj89d7s89f7s89df7s89d`)

## Step 5: Deploy

1.  Click **Create Web Service**.
2.  Render will start building your app. You can watch the logs in the dashboard.
3.  Once the build finishes, you'll see a green "Live" badge.
4.  Click the URL at the top (e.g., `https://secure-shared-key-system.onrender.com`) to visit your live app!

## Troubleshooting

*   **Build Failed**: Check the logs. Did you forget to update `requirements.txt`?
*   **App Crashes**: Check the logs. Did you set the Environment Variables correctly?
*   **Depencency Error**: Ensure `gunicorn` is in your `requirements.txt`.

Success! Your app is now online and ready to present.
