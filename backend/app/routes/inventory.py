from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.routes.auth import get_current_active_user, require_role
from app.models.user import UserRole
from app.database import get_database

router = APIRouter()

class InventoryItem(BaseModel):
    item_id: str
    item_name: str
    category: str
    quantity: int
    unit: str
    reorder_level: int
    supplier: Optional[str] = None
    unit_price: Optional[float] = None
    
class InventoryCreate(BaseModel):
    item_name: str
    category: str
    quantity: int
    unit: str
    reorder_level: int
    supplier: Optional[str] = None
    unit_price: Optional[float] = None

@router.post("/", response_model=InventoryItem)
async def create_inventory_item(
    item: InventoryCreate,
    current_user = Depends(require_role([UserRole.ADMIN]))
):
    """Create new inventory item"""
    db = get_database()
    
    # Generate item ID
    count = await db.inventory.count_documents({})
    item_id = f"INV{count + 1:05d}"
    
    item_dict = item.dict()
    item_dict.update({
        "item_id": item_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db.inventory.insert_one(item_dict)
    return InventoryItem(**item_dict)

@router.get("/", response_model=List[InventoryItem])
async def get_inventory(
    category: Optional[str] = None,
    low_stock: bool = False,
    current_user = Depends(get_current_active_user)
):
    """Get inventory items"""
    db = get_database()
    query = {}
    
    if category:
        query["category"] = category
    if low_stock:
        query["$expr"] = {"$lte": ["$quantity", "$reorder_level"]}
    
    items = await db.inventory.find(query).to_list(length=1000)
    return [InventoryItem(**item) for item in items]

@router.put("/{item_id}/stock")
async def update_stock(
    item_id: str,
    quantity_change: int,
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Update inventory stock"""
    db = get_database()
    
    result = await db.inventory.update_one(
        {"item_id": item_id},
        {
            "$inc": {"quantity": quantity_change},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return {"message": "Stock updated successfully"}