# WhatsApp AI Agent

An intelligent WhatsApp bot that helps users with various tasks including train ticket booking assistance (IRCTC), bus ticket booking assistance (Redbus), and other travel-related services.

## Features

- 🚂 **Train Booking Assistance**: Help with IRCTC train searches, fare information, and booking guidance
- 🚌 **Bus Booking Assistance**: Help with Redbus bus searches and booking guidance  
- 💬 **Natural Language Processing**: Understand user requests in natural language
- 🔒 **Secure**: Built with security and privacy in mind
- 🆓 **Free Hosting**: Designed to work on free hosting platforms

## Architecture

The system follows a modular architecture with these key components:

1. **Webhook Receiver**: Handles incoming WhatsApp messages from Twilio
2. **Message Parser**: Processes and understands user messages
3. **AI Agent Core**: Makes decisions and routes requests
4. **Task Modules**: Specialized modules for different services (IRCTC, Redbus, etc.)
5. **Response Generator**: Creates and sends responses back to users

## Setup Instructions

### Prerequisites

- Python 3.8+
- Twilio Account with WhatsApp Sandbox
- (Optional) OpenAI API key for advanced AI features

### Local Development

1. **Clone and setup the project:**
   ```bash
   cd whatsapp-ai-agent
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

The application will start on `http://0.0.0.0:5000`

### Twilio WhatsApp Setup

1. **Create a Twilio Account:**
   - Go to [twilio.com](https://twilio.com) and sign up
   - Navigate to Console > Messaging > Try it out > Send a WhatsApp message

2. **Configure WhatsApp Sandbox:**
   - In Twilio Console, go to Messaging > Settings > WhatsApp sandbox settings
   - Set the webhook URL to: `https://your-app-url.com/api/webhook`
   - Set HTTP method to POST

3. **Test the connection:**
   - Send "join [your-sandbox-keyword]" to your Twilio WhatsApp number
   - Send "hello" to test the bot

### Deployment Options

#### Option 1: Railway (Recommended)
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy with automatic builds

#### Option 2: Render
1. Create account at [render.com](https://render.com)
2. Create new Web Service from GitHub
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python src/main.py`

#### Option 3: Fly.io
1. Install Fly CLI
2. Run `fly launch` in project directory
3. Deploy with `fly deploy`

## API Endpoints

- `POST /api/webhook` - Twilio WhatsApp webhook
- `GET /api/webhook` - Webhook verification
- `GET /api/health` - Health check endpoint

## Usage Examples

### Basic Conversation
```
User: "Hello"
Bot: "Hi! I'm your AI assistant. I can help you with:
🚂 Train ticket booking (IRCTC)
🚌 Bus ticket booking (Redbus)
📋 General travel assistance
Just tell me what you need help with!"
```

### Train Booking Assistance
```
User: "I need to book a train from Delhi to Mumbai"
Bot: "🚂 I can help you with train bookings! Please tell me:
1. From which city? Delhi ✓
2. To which city? Mumbai ✓  
3. Travel date?
4. Preferred class (AC/Non-AC)?
I'll help you find the best trains and guide you through the booking process."
```

## Project Structure

```
whatsapp-ai-agent/
├── src/
│   ├── models/          # Database models
│   ├── routes/          # Flask routes
│   │   ├── webhook.py   # WhatsApp webhook handler
│   │   └── user.py      # User management routes
│   ├── static/          # Static files
│   ├── database/        # SQLite database
│   └── main.py          # Main Flask application
├── venv/                # Virtual environment
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Legal Notice

This bot provides assistance and guidance for booking tickets on IRCTC and Redbus platforms. It does not perform automated booking that might violate platform terms of service. Users are responsible for completing their own bookings through official channels.

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## Version History

- v1.0.0 - Initial release with basic WhatsApp integration and travel assistance

