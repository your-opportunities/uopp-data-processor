# Railway Deployment Guide - UOPP Data Processor

This guide will walk you through deploying your UOPP Data Processor to Railway from your Git repository.

## Prerequisites

Before starting, make sure you have:
1. RabbitMQ service (CloudAMQP free tier recommended)
2. GitHub repository with your code pushed to master/main branch
3. Railway account (sign up at https://railway.app)

## Step 1: Railway Setup

### 1.1 Create Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub if needed
5. Select your repository
6. Click "Deploy"

### 1.2 Configure Environment Variables

In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add the following environment variables:

```env
# Required RabbitMQ Variables
RABBIT_URL=amqps://username:password@host:5671/vhost
RABBIT_PROCESSED_QUEUE_NAME=processed_messages

# Optional Variables
RABBIT_RAW_QUEUE_NAME=telegram_messages
RABBIT_DELIVERY_MODE=2
RABBIT_MAX_RETRIES=5
RABBIT_RETRY_DELAY=5
LOG_LEVEL=INFO
```

**Important**: Replace the `RABBIT_URL` with your actual RabbitMQ connection URL. The format should be:
- For AMQP: `amqp://username:password@host:5672/vhost`
- For AMQPS (SSL): `amqps://username:password@host:5671/vhost`

### 1.3 Configure Build Settings

Railway should automatically detect your Python app, but verify:

1. Go to "Settings" tab
2. Make sure:
   - **Builder**: NIXPACKS (default)
   - **Root Directory**: `/` (default)

### 1.4 Deploy and Monitor

1. Railway will automatically build and deploy your app
2. Check the "Deployments" tab for build logs
3. Monitor the "Logs" tab for runtime logs

## Step 2: Post-Deployment Setup

### 2.1 Verify Deployment

1. **Check Logs**: Ensure no errors in Railway logs
2. **Test Functionality**: Monitor logs for successful RabbitMQ connection and message processing
3. **Verify Models**: Ensure spaCy and Hugging Face models load successfully

### 2.2 Common Success Indicators

Look for these messages in the logs:
- "NLP models loaded successfully"
- "RabbitMQ setup completed successfully"
- "Starting continuous message consumption"
- "Application started successfully"

## Step 3: Continuous Deployment

### 3.1 Automatic Deployments

Once set up, Railway will automatically deploy when you:
- Push to master/main branch
- Create a pull request
- Merge a pull request

### 3.2 Manual Deployments

You can also trigger manual deployments:
1. Go to Railway dashboard
2. Click "Deploy" button
3. Select branch to deploy from

## Step 4: Monitoring and Maintenance

### 4.1 Railway Dashboard Features

- **Deployments**: View deployment history and logs
- **Variables**: Manage environment variables
- **Logs**: Real-time application logs
- **Settings**: Configure build and deployment settings
- **Metrics**: Monitor resource usage (CPU, memory)

### 4.2 Log Monitoring

Key things to watch for in logs:
- "NLP models loaded successfully"
- "RabbitMQ setup completed successfully"
- "Application started successfully"
- Connection errors
- Model loading failures
- Missing environment variables

### 4.3 Scaling and Limits

**Free Tier Limits:**
- **Railway**: 500 hours/month
- **RabbitMQ**: Depends on your provider (CloudAMQP free tier available)
- **Image Size**: 4GB limit (optimized to fit within this limit)

**Upgrading:**
- If you hit limits, consider paid plans
- Railway paid plans start at $5/month

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` exists
   - Verify Python version in `runtime.txt`
   - Check build logs in Railway dashboard

2. **Runtime Errors**
   - Missing environment variables
   - Invalid RabbitMQ URL
   - Model loading failures

3. **Connection Issues**
   - RabbitMQ service down
   - Invalid credentials
   - Network connectivity issues

### Environment Variable Issues

**If environment variables are not being loaded:**

1. **Check Variable Names**: Ensure exact spelling and case
2. **Redeploy After Adding**: Variables require a redeploy to take effect
3. **Check Project**: Make sure you're in the correct Railway project
4. **Verify Format**: No spaces around the `=` sign
5. **Check Quotes**: Don't use quotes unless the value contains spaces

**Common Variable Issues:**
- `RABBIT_URL` not set or malformed
- `RABBIT_PROCESSED_QUEUE_NAME` not set
- Variables set in wrong project

**Debug Steps:**
1. Go to Railway dashboard → Your project → Variables tab
2. Verify all required variables are present
3. Check that values are correct (no extra spaces, quotes, etc.)
4. Redeploy the application
5. Check logs for "Found custom variables" message

### SSL Connection Issues

**If you get "IncompatibleProtocolError" or "StreamLostError":**

1. **Check URL Scheme**: Ensure you're using `amqps://` for SSL connections
2. **Verify Port**: SSL connections typically use port 5671, plain connections use 5672
3. **Check CloudAMQP Settings**: Ensure SSL is enabled in your CloudAMQP dashboard

**Common SSL Issues:**
- Using `amqp://` with port 5671 (should be `amqps://`)
- Using `amqps://` with port 5672 (should be 5671)
- Missing SSL configuration in the client

**Debug Steps:**
1. Check Railway logs for SSL configuration details
2. Verify your RabbitMQ provider supports SSL
3. Ensure the URL format is correct: `amqps://username:password@host:5671/vhost`

### Model Loading Issues

1. **spaCy Model**: Ensure `uk_core_news_sm` is available
2. **Hugging Face Model**: Check internet connectivity for model download
3. **Memory Issues**: Consider using smaller models for free tier

### Getting Help

1. **Railway Documentation**: https://docs.railway.app
2. **Railway Discord**: https://discord.gg/railway

## Security Best Practices

1. **Never commit sensitive data** to Git
2. **Use environment variables** for all secrets
3. **Regularly rotate** API keys and passwords
4. **Monitor logs** for suspicious activity
5. **Use HTTPS** for all external connections

Your app will now automatically deploy from your master/main branch pushes!
