# Text to Video Application

This application generates personalized videos with text-to-speech capabilities using ElevenLabs and other services.

## Prerequisites

- Docker
- Docker Compose

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key
HEDRA_API_KEY=your_hedra_api_key

# This static text will be used in the greeting and must include the {name} placeholder to replace the name entered in the first html page
STATIC_TEXT="Hello {name} - Add your personal greeting text here..."

# Voice and model to be used from eleven labs
ELEVENLABS_VOICE_NAME=your_voice_name
ELEVENLABS_MODEL=your_model_name

# email settings
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=your_from_email
CC_EMAIL=maya.oberholzer@sanlam.co.za
```

## Running with Docker

1. Build and start the container:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8000`

3. To stop the container:
```bash
docker-compose down
```

## Cloud Deployment

For cloud deployment:

1. Build the Docker image:
```bash
docker build -t text-to-video-app .
```

2. Tag the image for your cloud provider's registry:
```bash
docker tag text-to-video-app [registry-url]/text-to-video-app:latest
```

3. Push the image to your registry:
```bash
docker push [registry-url]/text-to-video-app:latest
```

4. Deploy using your cloud provider's container service (e.g., AWS ECS, Google Cloud Run, Azure Container Instances)

Remember to:
- Set up environment variables in your cloud provider's configuration
- Configure appropriate security groups/firewall rules
- Set up a domain name and SSL certificate if needed

## Cloud Platform Specific Instructions

### AWS Deployment
1. Create an ECR repository
2. Use AWS CLI to authenticate Docker to ECR:
```bash
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [aws-account-id].dkr.ecr.[region].amazonaws.com
```
3. Tag and push the image:
```bash
docker tag text-to-video-app [aws-account-id].dkr.ecr.[region].amazonaws.com/text-to-video-app:latest
docker push [aws-account-id].dkr.ecr.[region].amazonaws.com/text-to-video-app:latest
```
4. Create an ECS cluster and service or use AWS App Runner for simpler deployment

### Google Cloud Deployment
1. Enable Container Registry API
2. Configure Docker authentication:
```bash
gcloud auth configure-docker
```
3. Tag and push the image:
```bash
docker tag text-to-video-app gcr.io/[project-id]/text-to-video-app:latest
docker push gcr.io/[project-id]/text-to-video-app:latest
```
4. Deploy to Cloud Run or GKE

### Azure Deployment
1. Create an Azure Container Registry (ACR)
2. Login to ACR:
```bash
az acr login --name [registry-name]
```
3. Tag and push the image:
```bash
docker tag text-to-video-app [registry-name].azurecr.io/text-to-video-app:latest
docker push [registry-name].azurecr.io/text-to-video-app:latest
```
4. Deploy to Azure Container Instances or AKS
# TextAndImageToVideo
