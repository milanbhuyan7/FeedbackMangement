# Milan Backend Deployment Guide for Render

This guide will help you deploy your Django backend to Render using either Docker or native Python deployment.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Options

### Option 1: Native Python Deployment (Recommended)

This is the simpler approach and works well for most Django applications.

#### Step 1: Prepare Your Repository
1. Ensure all the files created in this setup are committed to your repository
2. Push your code to your Git repository

#### Step 2: Create a Web Service on Render
1. Go to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `milan-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `daphne -b 0.0.0.0 -p $PORT core.asgi:application`
   - **Instance Type**: Free (or paid as needed)

#### Step 3: Set Environment Variables
In the Render dashboard, add these environment variables:
- `PYTHON_VERSION`: `3.10.0`
- `SECRET_KEY`: Generate a secure secret key
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com` (replace with your actual Render URL)
- `CORS_ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-frontend.onrender.com`)

#### Step 4: Create a PostgreSQL Database
1. In Render dashboard, click "New +" and select "PostgreSQL"
2. Configure:
   - **Name**: `milan-postgres`
   - **Database**: `milan_db`
   - **User**: `milan_user`
   - **Plan**: Free (or paid as needed)

#### Step 5: Connect Database to Web Service
1. Go back to your web service settings
2. Add environment variable:
   - `DATABASE_URL`: Use the "Internal Database URL" from your PostgreSQL service

### Option 2: Docker Deployment

If you prefer using Docker:

#### Step 1: Prepare Your Repository
Same as Option 1

#### Step 2: Create a Web Service on Render
1. Go to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `milan-backend-docker`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `milan/backend/Dockerfile` (adjust path as needed)
   - **Instance Type**: Free (or paid as needed)

#### Step 3: Set Environment Variables
Same as Option 1, plus:
- `PORT`: This will be automatically set by Render

#### Step 4: Create Database
Same as Option 1

## Post-Deployment Steps

### 1. Run Migrations
After your first deployment, you may need to run migrations manually:
1. Go to your web service in Render dashboard
2. Open the "Shell" tab
3. Run: `python manage.py migrate`

### 2. Create Superuser (Optional)
To access Django admin:
1. In the Render shell, run: `python manage.py createsuperuser`
2. Follow the prompts

### 3. Test Your Deployment
1. Visit your Render URL: `https://your-app-name.onrender.com/health/`
2. You should see: `{"status": "healthy", "message": "Milan Backend is running"}`
3. Test your API endpoints: `https://your-app-name.onrender.com/api/`

## Important Notes

### Free Tier Limitations
- Render's free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30+ seconds
- Database has limited storage and connections

### Production Considerations
1. **Security**: 
   - Use strong SECRET_KEY
   - Set DEBUG=False
   - Configure proper ALLOWED_HOSTS
   - Set up proper CORS origins

2. **Performance**:
   - Consider upgrading to paid plans for better performance
   - Use Redis for channel layers in production (instead of InMemoryChannelLayer)

3. **Monitoring**:
   - Check Render logs regularly
   - Set up error tracking (e.g., Sentry)

### Environment Variables Summary
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://... (provided by Render)
CORS_ALLOWED_ORIGINS=https://your-frontend-url.com
PYTHON_VERSION=3.10.0
```

## Troubleshooting

### Common Issues
1. **Build fails**: Check that all dependencies are in requirements.txt
2. **Database connection fails**: Verify DATABASE_URL is correctly set
3. **Static files not loading**: Ensure WhiteNoise is properly configured
4. **CORS errors**: Check CORS_ALLOWED_ORIGINS includes your frontend URL

### Logs
- Check deployment logs in Render dashboard
- Use `print()` statements for debugging (they'll appear in logs)

## Updating Your Deployment
1. Push changes to your Git repository
2. Render will automatically redeploy
3. Monitor the deployment logs for any issues

## Support
- Render Documentation: https://render.com/docs
- Django Documentation: https://docs.djangoproject.com/