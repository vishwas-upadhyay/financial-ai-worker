# Deployment Guide

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd "Financial AI Worker"
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your broker credentials
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

4. **Access Dashboard**
   - Open http://localhost:8000 in your browser
   - API documentation: http://localhost:8000/docs

## Broker Configuration

### Zerodha Setup

1. **Get API Credentials**
   - Log in to your Zerodha account
   - Go to API section in your profile
   - Create a new API key
   - Note down API Key and API Secret

2. **Generate Access Token**
   - Use the provided redirect URL: `http://localhost:8000/zerodha/callback`
   - Complete the OAuth flow to get access token

3. **Update Environment**
   ```env
   ZERODHA_API_KEY=your_api_key
   ZERODHA_API_SECRET=your_api_secret
   ZERODHA_ACCESS_TOKEN=your_access_token
   ```

### Trading 212 Setup

1. **Get API Credentials**
   - Log in to Trading 212
   - Go to API settings
   - Generate API key

2. **Update Environment**
   ```env
   TRADING212_USERNAME=your_username
   TRADING212_PASSWORD=your_password
   TRADING212_API_KEY=your_api_key
   ```

## Production Deployment

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8000
   
   CMD ["python", "main.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t financial-ai-worker .
   docker run -p 8000:8000 --env-file .env financial-ai-worker
   ```

### Cloud Deployment

#### AWS Deployment

1. **EC2 Instance**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip nginx
   
   # Setup application
   git clone <repository>
   cd "Financial AI Worker"
   pip3 install -r requirements.txt
   
   # Configure nginx
   sudo nano /etc/nginx/sites-available/financial-ai-worker
   ```

2. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### Heroku Deployment

1. **Create Procfile**
   ```
   web: python main.py
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set ZERODHA_API_KEY=your_key
   heroku config:set ZERODHA_API_SECRET=your_secret
   git push heroku main
   ```

## Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use secure secret management in production
- Rotate API keys regularly

### API Security
- Implement rate limiting
- Use HTTPS in production
- Add authentication for API endpoints
- Validate all input data

### Data Protection
- Encrypt sensitive data at rest
- Use secure database connections
- Implement proper backup strategies
- Follow GDPR compliance

## Monitoring and Logging

### Application Monitoring
```python
# Add to main.py
import logging
from prometheus_client import start_http_server, Counter, Histogram

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# Start metrics server
start_http_server(9090)
```

### Logging Configuration
```python
# Enhanced logging setup
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'logs/financial_ai_worker.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
```

## Performance Optimization

### Database Optimization
- Use connection pooling
- Implement caching with Redis
- Optimize database queries
- Use database indexes

### API Optimization
- Implement response caching
- Use async/await patterns
- Add request compression
- Implement pagination

### Frontend Optimization
- Minify CSS/JS files
- Use CDN for static assets
- Implement lazy loading
- Optimize images

## Backup and Recovery

### Database Backup
```bash
# SQLite backup
sqlite3 financial_ai_worker.db ".backup backup.db"

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 financial_ai_worker.db ".backup backup_$DATE.db"
```

### Configuration Backup
- Backup environment files
- Document configuration changes
- Version control configuration templates

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check broker credentials
   - Verify network connectivity
   - Check API rate limits

2. **Portfolio Data Issues**
   - Verify broker permissions
   - Check data format compatibility
   - Review error logs

3. **Performance Issues**
   - Monitor memory usage
   - Check database performance
   - Review API response times

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
python main.py
```

### Log Analysis
```bash
# View recent logs
tail -f logs/financial_ai_worker.log

# Search for errors
grep "ERROR" logs/financial_ai_worker.log

# Monitor real-time logs
tail -f logs/financial_ai_worker.log | grep "ERROR\|WARNING"
```

## Support and Maintenance

### Regular Maintenance
- Update dependencies monthly
- Review security patches
- Monitor performance metrics
- Backup data regularly

### Health Checks
```python
# Add health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "database": "connected",
        "brokers": {
            "zerodha": "connected",
            "trading212": "connected"
        }
    }
```

### Monitoring Alerts
- Set up alerts for errors
- Monitor API response times
- Track portfolio performance
- Alert on security issues

