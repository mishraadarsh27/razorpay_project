from typing import List, Dict

CATALOG = [
    {
        "id": "p1",
        "name": "Wireless Earbuds Pro",
        "description": "Active noise cancellation with 24-hour battery life.",
        "price_inr": 2499,
        "category": "Electronics",
        "stock": 45
    },
    {
        "id": "p2",
        "name": "Ergonomic Laptop Stand",
        "description": "Adjustable aluminum stand for better posture.",
        "price_inr": 1299,
        "category": "Accessories",
        "stock": 30
    },
    {
        "id": "p3",
        "name": "Mechanical Keyboard",
        "description": "RGB backlit keyboard with tactile blue switches.",
        "price_inr": 3999,
        "category": "Electronics",
        "stock": 15
    }
]

def search_products(query: str = "") -> List[Dict]:
    if not query or query.lower() in ["all", "everything", "*", "catalog", "products"]:
        return CATALOG
    q = query.lower().strip()
    results = [p for p in CATALOG if q in p["name"].lower() or q in p["description"].lower() or q in p["category"].lower()]
    return results if results else CATALOG[:3]

def get_product_by_id(product_id: str) -> Dict:
    for p in CATALOG:
        if p["id"] == product_id:
            return p
    return None
