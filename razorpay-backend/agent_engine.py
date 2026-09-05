import os
import json
import razorpay
from typing import Dict, Any, List
from dotenv import load_dotenv
from groq import Groq
from catalog import search_products

load_dotenv()

razorpay_client = None
if os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"):
    try:
        razorpay_client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RRAZORPAY_KEY_SECRET"))
        )
    except Exception:
        pass

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

def get_catalog(query: str = "") -> str:
    products = search_products(query)
    return json.dumps(products, indent=2) if products else "No products found."

def create_payment_link(amount_inr: int, description: str) -> str:
    if not razorpay_client:
        return f"https://rzp.io/i/mock_{amount_inr} (Configure RAZORPAY keys for real links)"
    
    try:
        response = razorpay_client.payment_link.create({
            "amount": amount_inr * 100,
            "currency": "INR",
            "accept_partial": False,
            "description": description,
            "reference_id": f"order_{amount_inr}",
            "notify": {"sms": False, "email": False}
        })
        return response.get("short_url", "Failed to generate link.")
    except Exception as e:
        return f"Payment link error: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_catalog",
            "description": "Search products by name or category.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_payment_link",
            "description": "Generate a Razorpay payment link for a specific amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_inr": {"type": "integer"},
                    "description": {"type": "string"}
                },
                "required": ["amount_inr", "description"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a store assistant for our online shop. 
Your job is to help users find products and generate Razorpay payment links. 
Keep responses short, direct, and helpful. Do not make up products."""

def get_agent_response(user_message: str, history: List[Dict[str, Any]] = None) -> str:
    if not groq_client:
        return "Please configure GROQ_API_KEY in your .env file."
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])
    messages.append({"role": "user", "content": user_message})

    try:
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        for _ in range(3):
            response = groq_client.chat.completions.create(
                model=model, messages=messages, tools=tools, tool_choice="auto", max_tokens=500
            )
            msg = response.choices[0].message
            
            if not msg.tool_calls:
                return msg.content or "Request processed."
            
            messages.append(msg)
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                if tool_call.function.name == "get_catalog":
                    result = get_catalog(args.get("query", ""))
                elif tool_call.function.name == "create_payment_link":
                    result = create_payment_link(int(args.get("amount_inr", 0)), args.get("description", "Purchase"))
                else:
                    result = "Unknown tool"
                
                messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": tool_call.function.name, "content": result})
        
        final = groq_client.chat.completions.create(model=model, messages=messages, max_tokens=500)
        return final.choices[0].message.content or "Done."
    except Exception as e:
        return f"AI Error: {str(e)}"
