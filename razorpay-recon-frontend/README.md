# 💻 Razorpay AI Reconciliation Engine - Frontend

This is the web dashboard for the **Razorpay AI Reconciliation Engine**, built with **React 18**, **Vite**, **Tailwind CSS**, **Lucide Icons**, and **Recharts**.

## 🚀 Features
- **Executive KPI Cards**: Real-time totals, match rates, settlement variances, and detected leakages.
- **Drag-and-Drop Ingestion**: Upload Payment Gateway, Bank, and OMS CSV files.
- **Interactive Visualizations**: Recharts breakdown of match status and discrepancy distributions.
- **Autonomous GenAI Chatbot Widget**: Floating Copilot powered by Groq Llama 3.3 for conversational financial auditing.
- **Live WebSocket Support**: Real-time progress updates during batch processing.

## 🛠️ Tech Stack
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts
- **Parsing**: PapaParse
- **Markdown Rendering**: React-Markdown

## 🏃 Running Locally

```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The application will run at `http://localhost:5173`. Make sure the FastAPI backend (`http://localhost:8000`) is running concurrently.

For the complete project documentation, see the [Root README](../README.md).
