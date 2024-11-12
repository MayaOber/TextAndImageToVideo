# Hosting Requirements

## System Requirements
- Python 3.x runtime environment
- Sufficient CPU and RAM for video generation tasks
- Storage space for temporary video and audio files
- HTTPS support for secure API communication

## Dependencies
The following Python packages are required:
- elevenlabs: For text-to-speech conversion
- python-dotenv==1.0.0: For environment variable management
- pyshorteners==1.0.1: For URL shortening functionality
- requests==2.31.0: For making HTTP requests
- gunicorn==20.1.0: For production server deployment

## Environment Variables
The following environment variables must be configured:

### API Keys
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
HEDRA_API_KEY=your_hedra_api_key
```

### Text Configuration
```
STATIC_TEXT="Hello {name} - Add your personal greeting text here."
```

### Voice Configuration
```
ELEVENLABS_VOICE_NAME=your_voice_name
ELEVENLABS_MODEL=your_model_name
```

### Email Configuration
```
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=your_from_email
```

## API Requirements
- ElevenLabs API access for text-to-speech conversion
- Hedra API access for video processing
- SMTP server access for email functionality

## Server Configuration
- Port configuration through environment variable (PORT)
- Support for handling concurrent requests
- CORS enabled for cross-origin requests
- Support for multipart/form-data for file uploads

## Storage Requirements
- Write access to an 'assets' directory for storing:
  - Temporary audio files (MP3)
  - Image files (JPG)
  - Generated video files
- Sufficient disk space for temporary file storage during video generation

## Email Configuration
- SMTP server access with authentication
- Support for TLS/SSL
- Ability to send emails with attachments and HTML content

## Deployment Considerations
1. **Server Setup**
   - Production-grade WSGI server (Gunicorn)
   - Reverse proxy setup recommended (e.g., Nginx)
   - SSL/TLS certificates for HTTPS

2. **Scaling**
   - Consider containerization for easy deployment
   - Load balancing for handling multiple requests
   - Memory management for concurrent video generation

3. **Monitoring**
   - System resource monitoring
   - API rate limit monitoring
   - Error logging and tracking

4. **Security**
   - Secure environment variable management
   - API key protection
   - CORS policy configuration
   - Input validation and sanitization

5. **Backup**
   - Regular backup of configuration files
   - Backup strategy for generated content
   - Database backup if implemented in future

## Minimum Hardware Recommendations
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Storage: 20GB minimum for application and temporary files
- Network: Stable internet connection with good bandwidth for API calls

## Optional Enhancements
- CDN integration for serving static files
- Redis/Memcached for caching
- Queue system for video generation tasks
- Automated backup system
- Health check endpoints
- Rate limiting implementation
