# Deployment Guide for Render & Vercel

## 🚀 Backend Deployment on Render

### Environment Variables to Set on Render:
```
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=feedbackmangement.onrender.com
CORS_ALLOWED_ORIGINS=https://feedback-mangement.vercel.app,http://localhost:3000
DATABASE_URL=postgresql://... (Render provides this automatically)
```

### Build Command:
```
pip install -r requirements.txt
```

### Start Command:
```
python manage.py collectstatic --noinput && python manage.py migrate && daphne -b 0.0.0.0 -p $PORT core.asgi:application
```

## 🌐 Frontend Deployment on Vercel

### Environment Variables to Set on Vercel:
```
NEXT_PUBLIC_API_URL=https://feedbackmangement.onrender.com
```

## 🔧 CORS Configuration Fixed

The following CORS settings have been added/updated:

1. **CORS_ALLOW_METHODS** - Explicitly allows all HTTP methods
2. **CORS_PREFLIGHT_MAX_AGE** - Caches preflight requests for 24 hours
3. **CORS_EXPOSE_HEADERS** - Exposes necessary headers to frontend
4. **Production Security Settings** - Added HTTPS and security headers

## 🐛 Common CORS Issues & Solutions

### Issue 1: "Access-Control-Allow-Origin" error
**Solution**: Make sure your frontend URL is exactly in CORS_ALLOWED_ORIGINS

### Issue 2: Preflight OPTIONS requests failing
**Solution**: Added CORS_ALLOW_METHODS to handle all HTTP methods

### Issue 3: Credentials not being sent
**Solution**: CORS_ALLOW_CREDENTIALS is set to True

### Issue 4: Custom headers being blocked
**Solution**: Added comprehensive CORS_ALLOW_HEADERS list

## 📝 Deployment Checklist

### Backend (Render):
- [ ] Environment variables set correctly
- [ ] Build command configured
- [ ] Start command configured
- [ ] Database connected
- [ ] Static files collected

### Frontend (Vercel):
- [ ] API URL environment variable set
- [ ] Build successful
- [ ] Domain configured

### Testing:
- [ ] API endpoints accessible from frontend
- [ ] Authentication working
- [ ] WebSocket connections working (if applicable)
- [ ] Static files loading

## 🔍 Debugging CORS Issues

1. **Check Browser Console**: Look for specific CORS error messages
2. **Check Network Tab**: See if OPTIONS requests are successful
3. **Verify URLs**: Ensure frontend and backend URLs match exactly
4. **Test API Directly**: Use Postman/curl to test backend endpoints

## 📞 Support

If you're still getting CORS errors after these changes:
1. Check the exact error message in browser console
2. Verify environment variables are set correctly on Render
3. Ensure the frontend is making requests to the correct backend URL