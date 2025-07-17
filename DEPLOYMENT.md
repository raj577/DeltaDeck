# Deployment Guide - Option Spreads Analyzer

## 🚀 Backend Deployment on Render

### Prerequisites
1. Create a [Render](https://render.com) account
2. Have your Angel One API credentials ready

### Step 1: Deploy Backend
1. **Connect Repository**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this project

2. **Configure Service**:
   - **Name**: `option-spreads-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`

3. **Environment Variables**:
   Add these environment variables in Render dashboard:
   ```
   ANGEL_API_KEY=3GhdtVsl
   ANGEL_SECRET_KEY=66e83c38-8d81-4fd0-852b-11ef0abd537f
   ANGEL_CLIENT_CODE=your_client_code_here
   ANGEL_PASSWORD=your_pin_here
   ANGEL_TOTP_TOKEN=your_qr_token_here
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173
   LOG_LEVEL=INFO
   PORT=10000
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL: `https://your-app-name.onrender.com`

### Step 2: Test Backend
Once deployed, test these endpoints:
- `https://your-app-name.onrender.com/health`
- `https://your-app-name.onrender.com/docs` (API documentation)
- `https://your-app-name.onrender.com/api/status`

## 🌐 Frontend Deployment on Vercel

### Prerequisites
1. Create a [Vercel](https://vercel.com) account
2. Have your backend URL from Render

### Step 1: Prepare Frontend
1. **Update Environment Variables**:
   Create `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://your-render-app.onrender.com
   VITE_WS_URL=wss://your-render-app.onrender.com/ws
   VITE_REFRESH_INTERVAL=30000
   ```

### Step 2: Deploy Frontend
1. **Connect Repository**:
   - Go to Vercel Dashboard
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

3. **Environment Variables**:
   Add in Vercel dashboard:
   ```
   VITE_API_BASE_URL=https://your-render-app.onrender.com
   VITE_WS_URL=wss://your-render-app.onrender.com/ws
   VITE_REFRESH_INTERVAL=30000
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Note your frontend URL: `https://your-app.vercel.app`

### Step 3: Update CORS
Update your backend's CORS_ORIGINS environment variable on Render:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

## 🔧 Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

### Available Endpoints
- `GET /health` - Health check
- `GET /api/status` - API status
- `GET /api/prices` - Current NIFTY/BANKNIFTY prices
- `GET /api/recommendations/{symbol}` - Quick recommendations
- `POST /api/recommendations` - Detailed recommendations
- `GET /api/gainers-losers` - Top gainers/losers
- `GET /api/chart-data` - Historical OHLC data
- `GET /docs` - Interactive API documentation

### Example API Calls
```bash
# Get current prices
curl https://your-app.onrender.com/api/prices

# Get NIFTY recommendations
curl https://your-app.onrender.com/api/recommendations/NIFTY

# Get chart data
curl "https://your-app.onrender.com/api/chart-data?symbol=NIFTY"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Backend not starting**:
   - Check environment variables are set correctly
   - Verify Angel One API credentials
   - Check logs in Render dashboard

2. **CORS errors**:
   - Ensure frontend URL is in CORS_ORIGINS
   - Check both HTTP and HTTPS variants

3. **API timeouts**:
   - Angel One API may have rate limits
   - Check authentication status
   - Verify TOTP token is correct

4. **Frontend not loading data**:
   - Check VITE_API_BASE_URL points to correct backend
   - Verify backend is running and accessible
   - Check browser console for errors

### Monitoring
- **Backend logs**: Available in Render dashboard
- **Frontend logs**: Check browser console
- **API status**: Visit `/api/status` endpoint

## 🔐 Security Notes

1. **Environment Variables**:
   - Never commit .env files to git
   - Use Render/Vercel environment variable settings
   - Rotate API keys regularly

2. **CORS Configuration**:
   - Only allow necessary origins
   - Use HTTPS in production

3. **Rate Limiting**:
   - Angel One API has rate limits
   - Implement caching if needed

## 📈 Performance Tips

1. **Backend**:
   - Use single worker on free tier
   - Implement caching for frequent requests
   - Monitor API usage

2. **Frontend**:
   - Enable gzip compression
   - Optimize bundle size
   - Use CDN for static assets

## 🎯 Next Steps

After successful deployment:
1. Test all functionality
2. Monitor performance and errors
3. Set up alerts for downtime
4. Consider upgrading to paid plans for better performance
5. Implement WebSocket for real-time updates