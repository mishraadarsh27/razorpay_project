from typing import List, Dict


CATALOG = [
    {
        "id": "p1",
        "name": "Razor T-Shirt",
        "description": "A high-quality cotton t-shirt with the Razorpay logo.",
        "price_inr": 500,
        "category": "Apparel",
        "stock": 50
    },
    {
        "id": "p2",
        "name": "Developer Hoodie",
        "description": "Warm and cozy hoodie for late-night coding sessions.",
        "price_inr": 1500,
        "category": "Apparel",
        "stock": 20
    },
    {
        "id": "p3",
        "name": "Mechanical Keyboard",
        "description": "Clicky blue switches, RGB lighting, perfect for typing.",
        "price_inr": 4500,
        "category": "Electronics",
        "stock": 10
    },
    {
        "id": "p4",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with fast response time.",
        "price_inr": 1200,
        "category": "Electronics",
        "stock": 15
    },
    {
        "id": "p5",
        "name": "Coffee Mug",
        "description": "Ceramic coffee mug to keep you caffeinated.",
        "price_inr": 300,
        "category": "Accessories",
        "stock": 100
    }
]

def search_products(query: str = "") -> List[Dict]:
    """Search products by name or description."""
    if not query:
        return CATALOG
    
    query = query.lower()
    results = []
    for p in CATALOG:
        if query in p["name"].lower() or query in p["description"].lower() or query in p["category"].lower():
            results.append(p)
    return results

def get_product_by_id(product_id: str) -> Dict:
    for p in CATALOG:
        if p["id"] == product_id:
            return p
    return None
