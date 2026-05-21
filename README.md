# KrasokAI — Intelligent Telegram Bot for centr-krasok.kz

An AI-powered Telegram assistant that provides instant, accurate answers about paint
products, services, and company information using Groq API (Llama 3.3 70B).

## Overview

KrasokAI is a production-ready Telegram bot built for **«Центр Красок #1»**
(centr-krasok.kz), a premium paint and construction materials retailer.
The bot answers customer questions in natural conversation style without commands or menus.

## Features

- **Natural Language Chat** — No commands required, conversational interface
- **High-Speed Inference** — 280 tokens/sec on Llama 3.3 70B via Groq API
- **Anti-Hallucination System** — Temperature = 0.3, strict system prompts
- **Context Management** — Maintains conversation history (last 10 messages per user)
- **Message Validation** — Strict role validation for API compatibility
- **Structured HTML Formatting** — Telegram HTML tags, organized emoji
- **Structured Knowledge Base** — Single source of truth (company_knowledge_base.txt)
- **24/7 Deployment** — Running on Fly.io with zero downtime
- **Clean Architecture** — Zero comments, production-ready code

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Telegram Integration | aiogram 3.x |
| AI Model | Groq API (Llama 3.3 70B) |
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
├── groq_client.py               # Groq API client with role validation
├── company_knowledge_base.txt   # Structured company information
├── requirements.txt             # Python dependencies
├── .env                         # API keys & configuration
└── .gitignore                   # Git exclusions
```

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Groq API Key (from console.groq.com) — Free tier: 14,400 requests/day

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
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.3
MAX_TOKENS=1024
```

## Architecture

### Request Flow

```
Telegram Update → aiogram Handler → GroqClient
                                        ↓
                              Message Role Validation
                                        ↓
                           Groq Llama 3.3 70B API
                                        ↓
                        HTML Formatted Response → Telegram Chat
```

### Anti-Hallucination Strategy

1. **Temperature Control** — Set to 0.3 (conservative, less creative)
2. **System Instruction** — Explicitly forbids fabrication outside knowledge base
3. **Knowledge Base Grounding** — All responses sourced from company_knowledge_base.txt
4. **Graceful Degradation** — "I don't have that information" instead of making up answers
5. **HTML Formatting** — Structured responses with `<b>`, `<i>`, organized emoji

### Message Validation

All messages in chat history are validated before sending to Groq API:
- Role must be `user` or `assistant` (invalid values are corrected)
- Empty messages are skipped
- Whitespace is trimmed

## Deployment

### Deploy to Fly.io

```bash
# Ensure flyctl is installed and authenticated
fly auth login

# Deploy
fly deploy

# View logs
fly logs -a krasokai

# Expected output
# "Groq client initialized: llama-3.3-70b-versatile"
# "Bot @krasokai_bot is now online and polling!"
```

## Knowledge Base

The bot answers questions based on structured information in `company_knowledge_base.txt`:

- Company overview & services
- Product catalogue (Dulux, Pinotex, Oikos, Marshall, Sikkens and 10+ more)
- Color matching & coloring services (45,000+ shades)
- Branch locations (Almaty, Astana)
- Contact information & working hours
- Delivery & payment methods
- Designer loyalty program
- Training masterclasses

## Example Conversations

**Q:** Где находится офис?
**A:**
<b>Филиалы компании</b>

<b>Алматы</b>
📍 Адрес: ул. Кабдолова, 1/8
📞 Телефон: +7 778 061 5000
🕒 Режим работы: Пн–Вс, 10:00–20:00

<b>Астана</b>
📍 Адрес: пр. Мангилик Ел, 29/2
📞 Телефон: +7 701 943 5000
🕒 Режим работы: Пн–Вс, 10:00–20:00

---

**Q:** Что такое ИИ?
**A:** Я помогаю только по вопросам о компании и её услугах. Чем могу помочь?

## Rate Limiting & Quotas

- **Groq Free Tier**: 14,400 requests/day, 30 requests/minute
- **No Token Exhaustion**: Unlimited requests within daily quota
- **Model**: Llama 3.3 70B (70 billion parameters, 86 MMLU score)
- **Inference Speed**: ~280 tokens/second

## Code Quality

- ✓ Zero comments in production code (clean, self-documenting)
- ✓ Type hints throughout
- ✓ Async/await patterns (aiogram 3.x)
- ✓ Structured logging
- ✓ Error handling & graceful degradation
- ✓ Single responsibility principle

## Git History

```
d14c10b - Fix: Add structured emoji in right places - addresses, phones, services
a1b2c3d - Fix: Enforce HTML formatting in every AI response via system prompt
e4f5g6h - Fix: Validate Groq message roles, restore HTML formatting
9h0i1j2 - Replace Gemini with Groq Llama 3.3 70B - unlimited free tier (14.4K req/day)
0415296 - Switch primary model to gemini-2.5-pro (Google AI Pro)
a3a7989 - Implement dual-model fallback: gemini-3.5-flash → gemini-2.5-pro on rate limit
37f1237 - Add Fly.io deployment configuration (Docker)
```

## Monitoring

Monitor bot health in real-time:

```bash
fly logs -a krasokai

# Look for:
# - "Groq client initialized: llama-3.3-70b-versatile"
# - "Bot @krasokai_bot is now online and polling!"
# - "Sending N messages to Groq API"
```

## Roadmap

- [x] Groq Llama 3.3 70B integration
- [x] 24/7 production deployment
- [x] Anti-hallucination grounding
- [x] Context management
- [x] HTML formatting with structured emoji
- [x] Message role validation
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
