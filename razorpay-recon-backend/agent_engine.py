import os
from dotenv import load_dotenv
load_dotenv()

import json
import razorpay
from typing import Dict, Any, List
from groq import Groq
from catalog import search_products


razorpay_client = None
if os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"):
    try:
        razorpay_client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )
    except Exception as e:
        print(f"Failed to initialize Razorpay: {e}")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

def get_catalog(query: str = "") -> str:
    """Returns products matching the search query from the catalog."""
    products = search_products(query)
    if not products:
        return "No products found for that query."
    return json.dumps(products, indent=2)

def create_payment_link(amount_inr: int, description: str, reference_id: str = "order_123") -> str:
    """Creates a Razorpay payment link for the given amount in INR."""
    print(f"Creating payment link for {amount_inr} INR: {description}")
    if not razorpay_client:
        return f"https://rzp.io/i/mock_link_for_{amount_inr}_inr (MOCK - Configure Razorpay Keys to see real link)"
    
    try:
        payment_link_data = {
            "amount": amount_inr * 100,
            "currency": "INR",
            "accept_partial": False,
            "description": description,
            "reference_id": reference_id,
            "notify": {"sms": False, "email": False},
            "reminder_enable": False
        }
        
        response = razorpay_client.payment_link.create(payment_link_data)
        return response.get("short_url", "Failed to get short URL.")
    except Exception as e:
        return f"Error creating payment link: {str(e)}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_catalog",
            "description": "Returns products matching the search query from the catalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term, e.g. 'hoodie' or 'electronics'."
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_payment_link",
            "description": "Creates a Razorpay payment link for the given amount in INR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_inr": {
                        "type": "integer",
                        "description": "The amount to charge in INR."
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the items being purchased."
                    }
                },
                "required": ["amount_inr", "description"],
            },
        },
    }
]

system_instruction = """
You are a helpful, enthusiastic, and persuasive AI sales assistant for a Razorpay-powered online store.
Your goal is to help customers find products, answer their questions, and subtly upsell related items.
When a customer is ready to buy, use the `create_payment_link` tool to generate a checkout link.

Guidelines:
1. Always be polite and helpful.
2. Use the `get_catalog` tool to look up product information. Don't make up products.
3. If a customer wants to buy something, suggest ONE related upsell item before generating the link. For example, if they buy a laptop, suggest a mouse.
4. When generating a payment link, calculate the total amount correctly in INR. Provide a clear description of what they are buying.
5. Present the payment link nicely to the user using Markdown.
"""

def get_agent_response(user_message: str, history: List[Dict[str, Any]] = None) -> str:
    """
    Sends a message to Groq and returns the text response.
    Requires GROQ_API_KEY in the environment.
    """
    if not groq_client:
         return "Hello! I am the Agentic Commerce assistant. To make me smart, please add GROQ_API_KEY to your backend .env file."
    
    messages = [{"role": "system", "content": system_instruction}]
    
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})

    try:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "get_catalog":
                    function_response = get_catalog(
                        query=function_args.get("query", "")
                    )
                elif function_name == "create_payment_link":
                    function_response = create_payment_link(
                        amount_inr=function_args.get("amount_inr"),
                        description=function_args.get("description")
                    )
                else:
                    function_response = "Unknown tool"
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            
            second_response = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=messages
            )
            return second_response.choices[0].message.content
        else:
            return response_message.content
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
