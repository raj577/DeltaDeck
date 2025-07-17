# Deployment Guide 🚀

This guide will help you deploy the Option Spreads Analyzer to production using Render (backend) and Vercel (frontend).

## 📋 Prerequisites

- GitHub account
- Render account (free tier available)
- Vercel account (free tier available)
- Angel One API credentials
- Gemini AI API key

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Your Repository

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### Step 2: Deploy to Render

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `option-spreads-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

In Render dashboard, add these environment variables:

```bash
# Angel One API Configuration
ANGEL_API_KEY=3GhdtVsl
ANGEL_SECRET_KEY=66e83c38-8d81-4fd0-852b-11ef0abd537f
ANGEL_CLIENT_CODE=S1968092
ANGEL_PASSWORD=1425
ANGEL_TOTP_TOKEN=U3U5MXCKROK2WV4FFXYK3CN3OY

# Gemini AI Configuration
GEMINI_API_KEY=AIzaSyA6cZxMuNGLQkOvFcY4hff2d7BSmtmAA8c

# Application Configuration
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000,http://localhost:5173
PORT=10000
LOG_LEVEL=INFO
```

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Your API will be available** at: `https://option-spreads-api.onrender.com`

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Production

1. **Update API base URL** in frontend:
   ```bash
   # Create frontend/.env.production
   VITE_API_BASE_URL=https://option-spreads-api.onrender.com
   VITE_WS_URL=wss://option-spreads-api.onrender.com/ws
   ```

### Step 2: Deploy to Vercel

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure the project:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Set Environment Variables

In Vercel dashboard, add:

```bash
VITE_API_BASE_URL=https://option-spreads-api.onrender.com
VITE_WS_URL=wss://option-spreads-api.onrender.com/ws
```

### Step 4: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (2-3 minutes)
3. **Your app will be available** at: `https://your-project-name.vercel.app`

## 🔄 Update CORS Origins

After frontend deployment, update the backend CORS_ORIGINS:

1. **Go to Render dashboard**
2. **Update CORS_ORIGINS** environment variable:
   ```
   https://your-actual-vercel-domain.vercel.app,http://localhost:3000,http://localhost:5173
   ```
3. **Redeploy the backend**

## ✅ Verification Checklist

### Backend Health Check
- [ ] Visit `https://option-spreads-api.onrender.com/health`
- [ ] Should return: `{"status":"healthy","message":"Option Spreads Analyzer API is running",...}`

### API Endpoints Test
- [ ] `GET /api/status` - Check Angel One connection
- [ ] `GET /api/prices` - Get current NIFTY/BANKNIFTY prices
- [ ] `GET /api/recommendations/NIFTY` - Get spread recommendations
- [ ] `POST /api/gemini-chat` - Test AI chat functionality

### Frontend Functionality
- [ ] Real-time price updates working
- [ ] WebSocket connection established
- [ ] Spread recommendations loading
- [ ] AI chat responding to questions
- [ ] Mobile responsive design

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues:
1. **Build Failures**:
   - Check `requirements.txt` is in backend folder
   - Verify Python version compatibility

2. **Angel One API Errors**:
   - Verify all API credentials are correct
   - Check if TOTP token is valid

3. **WebSocket Issues**:
   - Ensure WebSocket URL uses `wss://` for HTTPS
   - Check CORS configuration

#### Frontend Issues:
1. **API Connection Errors**:
   - Verify VITE_API_BASE_URL is correct
   - Check CORS origins in backend

2. **Build Failures**:
   - Ensure all dependencies are in package.json
   - Check for TypeScript errors

### Performance Optimization

#### Backend:
- **Free tier limitations**: 512MB RAM, sleeps after 15min inactivity
- **Upgrade to paid plan** for better performance
- **Add Redis caching** for frequently accessed data

#### Frontend:
- **Vercel automatically optimizes** builds
- **Enable compression** for static assets
- **Use CDN** for better global performance

## 📊 Monitoring

### Backend Monitoring:
- **Render Dashboard**: View logs, metrics, and deployment status
- **Health endpoint**: Monitor API availability
- **Error tracking**: Check logs for API errors

### Frontend Monitoring:
- **Vercel Analytics**: Track page views and performance
- **Browser DevTools**: Monitor WebSocket connections
- **User feedback**: Monitor chat functionality

## 🔒 Security Best Practices

### Environment Variables:
- ✅ Never commit API keys to Git
- ✅ Use environment variables for all secrets
- ✅ Rotate API keys regularly

### CORS Configuration:
- ✅ Restrict origins to your domains only
- ✅ Don't use wildcard (*) in production
- ✅ Update origins when domains change

### API Security:
- ✅ Implement rate limiting
- ✅ Add request validation
- ✅ Monitor for unusual activity

## 🚀 Going Live

### Final Steps:
1. **Test all functionality** in production
2. **Update README.md** with live URLs
3. **Share your app** with users
4. **Monitor performance** and user feedback

### Live URLs:
- **Backend API**: `https://option-spreads-api.onrender.com`
- **Frontend App**: `https://your-project-name.vercel.app`
- **API Documentation**: `https://option-spreads-api.onrender.com/docs`

## 🎉 Congratulations!

Your Option Spreads Analyzer is now live and accessible to users worldwide! 

### Features Available:
- ✅ Real-time NIFTY & BANKNIFTY price streaming
- ✅ AI-powered option spread recommendations
- ✅ Interactive chat for trading education
- ✅ Professional trading interface
- ✅ Mobile-responsive design

---

**Need help?** Check the troubleshooting section or create an issue in the GitHub repository.