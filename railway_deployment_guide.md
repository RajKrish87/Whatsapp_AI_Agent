# Railway Deployment Guide for WhatsApp AI Agent

This guide will walk you through deploying your WhatsApp AI Agent to Railway, a free hosting platform perfect for beginners.

## Prerequisites

1. **GitHub Account**: You'll need a GitHub account to connect with Railway
2. **Twilio Account**: Your Twilio WhatsApp sandbox should be set up
3. **Project Ready**: Your Flask app should be working locally

## Step 1: Prepare Your Project for Deployment

### 1.1 Create a Procfile (Optional but Recommended)

Create a file named `Procfile` in your project root:

```
web: python src/main.py
```

### 1.2 Update requirements.txt

Make sure your `requirements.txt` is up to date:

```bash
cd whatsapp-ai-agent
source venv/bin/activate
pip freeze > requirements.txt
```

### 1.3 Set Environment Variables

Railway will need your environment variables. You have your `.env.example` file ready, which is good.

## Step 2: Push to GitHub

### 2.1 Initialize Git Repository (if not done)

```bash
cd whatsapp-ai-agent
git init
git add .
git commit -m "Initial commit - WhatsApp AI Agent"
```

### 2.2 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "New Repository"
3. Name it `whatsapp-ai-agent`
4. Don't initialize with README (since you already have files)
5. Click "Create Repository"

### 2.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-ai-agent.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Railway

### 3.1 Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with your GitHub account

### 3.2 Deploy from GitHub

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `whatsapp-ai-agent` repository
4. Railway will automatically detect it's a Python/Flask app

### 3.3 Configure Environment Variables

1. In your Railway project dashboard, go to "Variables" tab
2. Add these environment variables:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token  
   - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number (e.g., whatsapp:+14155238886)
   - `FLASK_ENV`: production
   - `SECRET_KEY`: A secure random string

### 3.4 Deploy

1. Railway will automatically start building and deploying
2. Wait for the deployment to complete (usually 2-3 minutes)
3. You'll get a public URL like `https://your-app-name.railway.app`

## Step 4: Configure Twilio Webhook

### 4.1 Update Twilio Webhook URL

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to Messaging → Settings → WhatsApp sandbox settings
3. Set the webhook URL to: `https://your-app-name.railway.app/api/webhook`
4. Set HTTP method to POST
5. Save the configuration

## Step 5: Test Your Deployment

### 5.1 Test Health Endpoint

Visit `https://your-app-name.railway.app/api/health` in your browser. You should see:

```json
{
  "service": "WhatsApp AI Agent",
  "status": "healthy", 
  "version": "1.0.0"
}
```

### 5.2 Test WhatsApp Integration

1. Send "join [your-sandbox-keyword]" to your Twilio WhatsApp number
2. Send "hello" to test the bot
3. You should receive the welcome message

## Step 6: Monitor and Maintain

### 6.1 View Logs

1. In Railway dashboard, go to "Deployments" tab
2. Click on your latest deployment
3. View logs to debug any issues

### 6.2 Update Your App

To update your app:

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update message"
   git push
   ```
3. Railway will automatically redeploy

## Troubleshooting

### Common Issues

1. **App not starting**: Check logs for Python errors
2. **Webhook not responding**: Verify the webhook URL in Twilio
3. **Environment variables**: Make sure all required variables are set
4. **Port issues**: Railway automatically handles ports, your app should listen on `0.0.0.0:5000`

### Getting Help

- Check Railway documentation: [docs.railway.com](https://docs.railway.com)
- View deployment logs in Railway dashboard
- Test endpoints manually using curl or Postman

## Railway Free Tier Limits

Railway offers a generous free tier:
- $5 credit per month (usually enough for small apps)
- Automatic scaling
- Custom domains
- GitHub integration

## Next Steps

Once deployed successfully:
1. Test all functionality thoroughly
2. Monitor usage and performance
3. Consider upgrading to paid plan if needed
4. Add more features to your AI agent

Your WhatsApp AI Agent is now live and accessible to users worldwide!

