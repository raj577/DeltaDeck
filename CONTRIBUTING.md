# Contributing to Option Spreads Analyzer

Thank you for your interest in contributing to the Option Spreads Analyzer! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Angel One Demat Account (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/option-spreads-analyzer.git
   cd option-spreads-analyzer
   ```

2. **Backend Setup**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp backend/.env.template backend/.env
   # Edit backend/.env with your credentials
   ```

## 🛠️ Development Workflow

### Branch Naming Convention
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical fixes
- `docs/documentation-update` - Documentation updates

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(websocket): add real-time price streaming
fix(api): handle authentication timeout
docs(readme): update installation instructions
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=. --cov-report=html  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Manual Testing
1. Start both backend and frontend
2. Test WebSocket connection
3. Verify real-time price updates
4. Test error handling scenarios

## 📝 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Add docstrings for functions and classes
- Maximum line length: 88 characters (Black formatter)

```python
async def get_current_price(self, symbol: str) -> float:
    """Get current market price for a symbol.
    
    Args:
        symbol: The symbol to get price for (NIFTY or BANKNIFTY)
        
    Returns:
        Current price as float
        
    Raises:
        AngelOneError: If API call fails
    """
```

### JavaScript/React (Frontend)
- Use ES6+ features
- Prefer functional components with hooks
- Use meaningful variable names
- Add JSDoc comments for complex functions

```javascript
/**
 * Connects to WebSocket and handles real-time price updates
 * @param {string} url - WebSocket URL
 * @param {Function} onMessage - Message handler callback
 */
const connectWebSocket = (url, onMessage) => {
  // Implementation
}
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - OS and version
   - Python version
   - Node.js version
   - Browser (for frontend issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Error Messages**
   - Full error messages
   - Stack traces
   - Console logs

4. **Additional Context**
   - Configuration details
   - Recent changes made

## ✨ Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and explain why your approach is best
5. **Provide mockups** for UI changes

## 🔍 Code Review Process

### For Contributors
1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Follow the style guide
5. Keep PRs focused and small

### Review Criteria
- Code quality and readability
- Test coverage
- Documentation updates
- Performance impact
- Security considerations
- Backward compatibility

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints in Python code
- Comment complex business logic
- Update API documentation

### User Documentation
- Update README.md for new features
- Add examples for new API endpoints
- Update deployment instructions
- Create tutorials for complex features

## 🚀 Deployment

### Testing Deployment
1. Test locally with production settings
2. Verify environment variables
3. Check database migrations
4. Test WebSocket connections

### Production Deployment
- Backend: Render or similar platform
- Frontend: Vercel or Netlify
- Environment variables properly configured
- SSL certificates in place

## 🤝 Community Guidelines

### Be Respectful
- Use inclusive language
- Be constructive in feedback
- Help newcomers
- Respect different perspectives

### Communication
- Use GitHub issues for bugs and features
- Join discussions in a constructive manner
- Ask questions if something is unclear
- Share knowledge and help others

## 📞 Getting Help

If you need help:

1. **Check Documentation** - README.md and code comments
2. **Search Issues** - Someone might have faced the same problem
3. **Create an Issue** - Describe your problem clearly
4. **Join Discussions** - Participate in GitHub discussions

## 🎯 Areas for Contribution

### High Priority
- [ ] Option chain data integration
- [ ] Advanced charting features
- [ ] Performance optimizations
- [ ] Mobile responsiveness
- [ ] Error handling improvements

### Medium Priority
- [ ] Additional technical indicators
- [ ] Export functionality
- [ ] User preferences
- [ ] Notification system
- [ ] Historical data analysis

### Low Priority
- [ ] Dark mode theme
- [ ] Multiple language support
- [ ] Advanced filtering options
- [ ] Social features
- [ ] Integration with other brokers

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Option Spreads Analyzer! 🚀