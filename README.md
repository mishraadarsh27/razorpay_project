# Razorpay Storefront Chatbot

A lightweight conversational shopping assistant built with FastAPI, React, and Groq LLM. It helps users search for products and generates instant Razorpay payment links directly within the chat interface.

## Features
- **Natural Language Search:** Users can ask for products in plain text.
- **Live Catalog Matching:** Search logic to find relevant items from local inventory.
- **Instant Checkout:** Automatically triggers Razorpay Payment Link API.

## Tech Stack
- **Backend:** Python, FastAPI, Groq SDK, Razorpay Python SDK
- **Frontend:** React, Vite, Tailwind CSS

## Setup Instructions

### 1. Backend
```bash
cd razorpay-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
