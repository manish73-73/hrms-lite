# HRMS Lite - Deployment Guide

This guide provides step-by-step instructions for deploying the HRMS Lite application to production.

## Prerequisites

Before deploying, ensure you have:
- GitHub account
- Railway account (for backend)
- Vercel account (for frontend)
- Git installed locally

## Step 1: Create GitHub Repository

### 1.1 Create a new repository on GitHub

1. Go to [GitHub.com](https://github.com)
2. Click "New" to create a new repository
3. Name it `hrms-lite`
4. Choose "Public" (for the assignment review)
5. Click "Create repository"

### 1.2 Push code to GitHub

```bash
cd E:\HRMS

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/hrms-lite.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 2: Deploy Backend to Railway

### 2.1 Connect Railway to GitHub

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your GitHub account
6. Select the `hrms-lite` repository

### 2.2 Configure the backend service

1. In Railway, click "Add Service"
2. Select "GitHub repo"
3. Look for the `backend` directory
4. Railway should auto-detect it's a Python project using `requirements.txt`

### 2.3 Set environment variables

In Railway dashboard for the backend:
1. Go to "Variables"
2. Add the following variables:

```
DATABASE_URL=sqlite:///./hrms.db
PYTHONUNBUFFERED=1
```

### 2.4 Deploy

1. Railway will automatically deploy when you push to GitHub
2. In the Railway dashboard, you'll see:
   - Build logs
   - Deployment status
   - Public URL

3. Copy the public URL (e.g., `https://hrms-lite-backend.railway.app`)

**Note:** The URL will include the Railway app name. You'll need this for the frontend.

## Step 3: Deploy Frontend to Vercel

### 3.1 Connect Vercel to GitHub

1. Go to [Vercel.com](https://vercel.com)
2. Sign in with GitHub account
3. Click "Add New" → "Project"
4. Select the `hrms-lite` repository

### 3.2 Configure the project

1. **Project Settings:**
   - Framework: Vite
   - Root Directory: `frontend`

2. **Environment Variables:**
   Click "Environment Variables" and add:
   
   ```
   VITE_API_URL=https://your-railway-backend-url.railway.app
   ```
   
   Replace with the actual Railway backend URL from Step 2

3. **Build Settings:**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### 3.3 Deploy

1. Click "Deploy"
2. Vercel will build and deploy automatically
3. Once complete, you'll get a **Production URL** (e.g., `https://hrms-lite.vercel.app`)

## Step 4: Update API URL and Redeploy

### 4.1 Update frontend environment variable

Now that you have both URLs:

1. Go back to Vercel dashboard
2. Project Settings → Environment Variables
3. Update `VITE_API_URL` with your Railway backend URL
4. Vercel will trigger a new deployment automatically

## Step 5: Test the Deployed Application

### 5.1 Access the live application

1. Open your Vercel frontend URL: `https://your-app.vercel.app`
2. Test Employee Management:
   - Add a new employee
   - View employee list
   - Delete an employee

3. Test Attendance Management:
   - Mark attendance for employees
   - View attendance records
   - Filter by employee

### 5.2 Verify backend connectivity

The application should:
- ✅ Load without errors
- ✅ Submit forms and store data
- ✅ Display employee list
- ✅ Show attendance records

## Troubleshooting

### Backend Not Responding

If you get a CORS error or 404:

1. **Check API URL:**
   - Verify the correct Railway URL is in Vercel environment variables
   - Make sure the URL doesn't have trailing slashes

2. **Check Railway logs:**
   - Go to Railway dashboard
   - View deployment logs for errors
   - Ensure Python dependencies installed correctly

3. **Redeploy backend:**
   ```bash
   git push origin main  # This triggers Railway to redeploy
   ```

### Frontend Build Fails

1. Check Vercel build logs
2. Ensure `frontend/` directory structure is correct
3. Verify `package.json` has correct build command
4. Redeploy: Push changes to GitHub

### Database Issues

If data isn't persisting:

1. Railway uses ephemeral storage by default
2. For production, upgrade to Railway Postgres:
   - Go to Railway dashboard
   - Add "PostgreSQL" service
   - Update `DATABASE_URL` in backend environment variables
   - Update backend `main.py` to use PostgreSQL connection string

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Environment variables configured correctly
- [ ] Live URL test successful
- [ ] Employee management working
- [ ] Attendance management working
- [ ] Error handling working
- [ ] No console errors in browser
- [ ] No errors in Railway logs

## URLs to Submit

After successful deployment, you'll have:

- **Live Frontend URL:** `https://your-app.vercel.app`
- **GitHub Repository:** `https://github.com/YOUR_USERNAME/hrms-lite`
- **Backend API URL:** `https://your-backend.railway.app`

The backend URL should be accessible at `/api/employees` and `/api/attendance` endpoints.

## API Documentation

### Access Swagger UI

Once deployed, you can access the interactive API documentation:
- **Local:** `http://localhost:8000/docs`
- **Production:** `https://your-backend.railway.app/docs`

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://vitejs.dev/guide/build.html)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review deployment logs in Railway/Vercel dashboards
3. Verify all environment variables are set correctly
4. Ensure GitHub repository is public (for deployment services to access)

---

**Version:** 1.0  
**Last Updated:** February 2026
