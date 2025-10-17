"""
backend/app/routes/inventory_low_stock.py
Returns all items below reorder level.
"""

from fastapi import APIRouter, Depends
from app.routes.auth import get_current_active_user
from app.database import get_database

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/low-stock")
async def get_low_stock_items(db=Depends(get_database), current_user=Depends(get_current_active_user)):
    """List items below reorder level."""
    query = {"$expr": {"$lte": ["$quantity", "$reorder_level"]}}
    items = await db.inventory.find(query).to_list(None)
    return {"low_stock_items": items, "count": len(items)}
