# Razorpay Conversational Storefront

A conversational shopping assistant built with FastAPI, React, and Groq. It allows users to search for products using natural language and generates instant Razorpay payment links directly in the chat.

## Features

- **Natural Language Search**: Query products conversationally (e.g., "Show me electronics under 3000")
- **Catalog Matching**: Searches the local product inventory by name, category, or description
- **Instant Checkout**: Triggers the Razorpay Payment Link API to return a clickable checkout URL in the chat
- **Responsive UI**: Built with React, Vite, and Tailwind CSS

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Groq SDK, Razorpay Python SDK
- **Frontend**: React 18, Vite, Tailwind CSS, React Markdown
- **LLM**: Groq (openai/gpt-oss-20b)

## Installation & Setup

### 1. Clone the Repository

```bash

git clone https://github.com/mishraadarsh27/razorpay_project.git
cd razorpay_project

Backend Setup

cd razorpay-backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload


Frontend Setup

cd razorpay-frontend
npm install
npm run dev

Project Structure

razorpay_project/
├── razorpay-backend/
│   ├── main.py
│   ├── agent_engine.py
│   ├── catalog.py
│   ├── requirements.txt
│   └── .env.example
├── razorpay-frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/AgentChatbot.jsx
│   │   └── index.css
│   └── package.json
└── README.md

