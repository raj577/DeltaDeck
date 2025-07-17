# Option Spreads Analyzer 📊

A real-time option spreads analysis application for NIFTY and BANKNIFTY indices using Angel One SmartAPI. Built with FastAPI backend and React frontend with WebSocket integration for live market data streaming.

## 🚀 Features

- **Real-time Price Streaming** - Live NIFTY & BANKNIFTY prices via WebSocket
- **Option Spread Analysis** - Bull Call and Bear Put spread recommendations
- **Delta-based Filtering** - Spreads filtered by delta difference (0.15-0.26)
- **Interactive Charts** - Historical OHLC data visualization with Plotly.js
- **Professional UI** - Modern trading interface with responsive design
- **Auto-reconnection** - Robust WebSocket connection management
- **Risk Metrics** - P&L calculations, risk-reward ratios, breakeven analysis

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐    REST API    ┌─────────────────┐
│   React App     │◄──────────────►│   FastAPI        │◄──────────────►│   Angel One     │
│   (Frontend)    │                 │   (Backend)      │                 │   SmartAPI      │
└─────────────────┘                 └──────────────────┘                 └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **WebSocket** - Real-time data streaming
- **Angel One SmartAPI** - Market data integration
- **Pydantic** - Data validation and serialization
- **Asyncio** - Asynchronous programming

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Plotly.js** - Interactive charts and graphs
- **Axios** - HTTP client for API calls

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- Angel One Demat Account
- Angel One API credentials

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/option-spreads-analyzer.git
cd option-spreads-analyzer
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
python -m venv venv
```

#### Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### Configure Environment Variables
```bash
# Copy the template
cp backend/.env.template backend/.env

# Edit backend/.env with your Angel One credentials
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_CODE=your_client_code
ANGEL_PASSWORD=your_password
ANGEL_TOTP_TOKEN=your_totp_secret
```

#### Start Backend Server
```bash
# Using batch file (Windows)
start_backend.bat

# Or manually
cd backend
python main.py
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
# Using batch file (Windows)
start_frontend.bat

# Or manually
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Angel One API Setup

1. **Create Angel One Account** - Sign up at [Angel One](https://angelone.in)
2. **Generate API Key** - Go to API section in your account
3. **Enable TOTP** - Set up 2FA and get TOTP secret
4. **Configure Environment** - Add credentials to `.env` file

### Environment Variables

```bash
# Angel One API Configuration
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_CODE=your_client_code_here
ANGEL_PASSWORD=your_password_here
ANGEL_TOTP_TOKEN=your_totp_secret_here

# Server Configuration
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📊 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - API and Angel One connection status

### Market Data
- `GET /api/prices` - Current NIFTY & BANKNIFTY prices
- `GET /api/chart-data` - Historical OHLC data
- `GET /api/gainers-losers` - Top gainers/losers

### Option Spreads
- `POST /api/recommendations` - Get spread recommendations
- `GET /api/recommendations/{symbol}` - Quick recommendations

### WebSocket
- `WS /ws` - Real-time price streaming
- `GET /api/websocket-info` - WebSocket connection info

## 🔄 Real-time Features

### WebSocket Integration
- **Live Price Updates** - NIFTY & BANKNIFTY prices every 2 seconds
- **Connection Status** - Visual indicators for connection state
- **Auto-reconnection** - Automatic reconnection on connection loss
- **Heartbeat Mechanism** - Keeps connection alive

### Spread Analysis
- **Delta Filtering** - Options filtered by delta difference (0.15-0.26)
- **ATM Buy Legs** - Always uses At-The-Money strikes as buy legs
- **Risk Calculations** - Max profit/loss, breakeven, risk-reward ratios
- **P&L Projections** - Profit/loss per 100 points movement

## 🚀 Deployment

### Backend (Render)
```yaml
# render.yaml
services:
  - type: web
    name: option-spreads-api
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Vercel)
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    }
  ]
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📁 Project Structure

```
option-spreads-analyzer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── angel_api.py         # Angel One API client
│   ├── spreads.py           # Spread analysis engine
│   ├── requirements.txt     # Python dependencies
│   └── .env.template        # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.jsx          # Main application
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── start_backend.bat       # Backend startup script
└── start_frontend.bat      # Frontend startup script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and research purposes only. Trading in financial markets involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software.

## 🙏 Acknowledgments

- [Angel One](https://angelone.in) for providing the SmartAPI
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [React](https://reactjs.org/) for the frontend framework
- [Plotly.js](https://plotly.com/javascript/) for interactive charts

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/option-spreads-analyzer/issues) page
2. Create a new issue with detailed description
3. Include logs and error messages

---

**Happy Trading! 📈**