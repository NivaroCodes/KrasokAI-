# KrasokAI — Intelligent Telegram Bot for centr-krasok.kz

An AI-powered Telegram assistant that provides instant, accurate answers about paint products, services, and company information using Gemini API with intelligent fallback routing.

## Overview

KrasokAI is a production-ready Telegram bot built for **«Центр Красок #1»** (centr-krasok.kz), a premium paint and construction materials retailer. The bot answers customer questions in natural conversation style without commands or menus.

## Features

- **Natural Language Chat** — No commands required, conversational interface
- **Dual-Model Architecture** — Primary: Gemini 2.5 Pro (Google AI Pro) → Fallback: Gemini 3.5 Flash
- **Anti-Hallucination System** — Temperature = 0.3, strict system prompts limit fabrication
- **Intelligent Fallback** — Auto-switches to secondary model on rate limits (429 errors)
- **Context Management** — Maintains conversation history (last 10 messages per user)
- **Structured Knowledge Base** — Single source of truth (company_knowledge_base.txt)
- **24/7 Deployment** — Running on Fly.io with zero downtime
- **Clean Architecture** — Zero comments, production-ready code

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Telegram Integration | aiogram 3.x |
| AI Models | Google Gemini API |
| Deployment | Fly.io |
| Container | Docker |
| Language | Python 3.11+ |
| Configuration | python-dotenv |

## Project Structure

```
krasok_bot/
├── main.py                      # Bot initialization & polling
├── config.py                    # Environment & knowledge base loading
├── handlers.py                  # Message routing & responses
├── gemini_client.py             # Dual-model Gemini client with fallback
├── company_knowledge_base.txt   # Structured company information
├── requirements.txt             # Python dependencies
├── .env                         # API keys & configuration
└── .gitignore                   # Git exclusions
```

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Google Gemini API Keys (2 recommended for fallback)
- Google AI Pro subscription (optional, for higher rate limits)

### Local Development

```bash
# Clone repository
git clone https://github.com/NivaroCodes/KrasokAI-.git
cd KrasokAI-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run bot
cd krasok_bot
python main.py
```

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_API_KEY_FALLBACK=your_fallback_key

GEMINI_MODEL=gemini-2.5-pro
GEMINI_MODEL_FALLBACK=gemini-3.5-flash

TEMPERATURE=0.3
MAX_TOKENS=2048
```

## Architecture

### Dual-Model Fallback System

```
User Message
    ↓
Primary Model (Gemini 2.5 Pro)
    ↓ [Success] → Response sent
    ↓ [Rate limit (429)]
    ↓
Fallback Model (Gemini 3.5 Flash)
    ↓ [Success] → Response sent
    ↓ [Failure] → Error message
```

### Anti-Hallucination Strategy

1. **Temperature Control**: Set to 0.3 (conservative, less creative)
2. **System Instruction**: Explicitly forbids fabrication outside knowledge base
3. **Knowledge Base Grounding**: All responses sourced from company_knowledge_base.txt
4. **Graceful Degradation**: "I don't have that information" instead of making up answers

### Request Flow

```
Telegram Update → aiogram Handler → DualModelGeminiClient
                                    ↓
                            Primary Model (Gemini 2.5 Pro)
                                    ↓ [429 error detected]
                            Fallback Model (Gemini 3.5 Flash)
                                    ↓
                            Response → Telegram Chat
```

## Deployment

### Deploy to Fly.io

```bash
# Ensure flyctl is installed and authenticated
fly auth login

# Deploy
fly deploy

# View logs
fly logs

# Expected output
# "Primary Gemini model initialized: gemini-2.5-pro"
# "Bot @krasokai_bot is now online and polling!"
```

The bot runs 24/7 on Fly.io's free tier with Gemini API backend.

## Knowledge Base

The bot answers questions based on structured information in `company_knowledge_base.txt`:

- Company overview & history
- Product catalogue (Dulux, Pinotex, Oikos, etc.)
- Services (color matching, delivery, consultations)
- Branch locations (Almaty, Astana)
- Contact information & hours
- Payment & delivery methods

## Example Conversations

**Q:** Где находится офис?  
**A:** У компании «Центр Красок #1» есть два филиала:
- Алматы: ул. Кабдолова, 1/8 | +7 778 061 5000
- Астана: пр. Мангилик Ел, 29/2 | +7 701 943 5000

**Q:** Какие услуги предоставляете?  
**A:** [Lists: color matching, consultations, delivery, designer support, training]

**Q:** Что такое ИИ?  
**A:** Я помогаю только по вопросам о компании и её услугах. Чем я могу помочь в рамках нашей продукции?

## Rate Limiting & Quotas

- **Google AI Pro**: Higher quotas for Gemini 2.5 Pro (primary)
- **Free Tier Fallback**: Gemini 3.5 Flash (20 requests/day limit)
- **Automatic Switching**: If primary hits limit → fallback activates silently

To increase quotas: Enable billing in Google Cloud Console ($300 trial credit available).

## Code Quality

- ✓ Zero comments in production code (clean, self-documenting)
- ✓ Type hints throughout
- ✓ Async/await patterns (aiogram 3.x)
- ✓ Structured logging
- ✓ Error handling & graceful degradation
- ✓ Single responsibility principle

## Git History

```
a3a7989 - Implement dual-model fallback: gemini-3.5-flash → gemini-2.5-pro on rate limit
0415296 - Switch primary model to gemini-2.5-pro (Google AI Pro)
58dcd68 - Add Railway deployment configuration
37f1237 - Add Fly.io deployment configuration (Docker)
```

## Monitoring

Monitor bot health in real-time:

```bash
# Live logs
fly logs -f

# Look for:
# - "Bot @krasokai_bot is now online and polling!"
# - "Fallback model activated:" (if rate limit triggered)
# - Error messages (if API fails)
```

## Roadmap

- [x] Dual-model fallback system
- [x] 24/7 production deployment
- [x] Anti-hallucination grounding
- [x] Context management
- [ ] Redis persistence for context
- [ ] Lead capture (phone, email collection)
- [ ] Live product catalogue API integration
- [ ] Analytics & conversation logging

## License

MIT — Open for modification and distribution.

## Contact

- **Project**: github.com/NivaroCodes/KrasokAI-
- **Bot**: @krasokai_bot (Telegram)
- **Company**: centr-krasok.kz
```
