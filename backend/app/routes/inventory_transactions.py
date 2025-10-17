"""
backend/app/routes/inventory_transactions.py
Records all stock movement transactions.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional
from app.routes.auth import require_role, get_current_active_user
from app.models.user import UserRole
from app.database import get_database

router = APIRouter(prefix="/api/inventory/transactions", tags=["Inventory Transactions"])


@router.post("/")
async def record_transaction(
    item_id: str,
    quantity: int,
    transaction_type: str,
    remarks: Optional[str] = None,
    current_user=Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR])),
    db=Depends(get_database)
):
    """Create new inventory transaction record."""
    valid_types = ["issue", "return", "restock"]
    if transaction_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    record = {
        "item_id": item_id,
        "quantity": quantity,
        "transaction_type": transaction_type,
        "remarks": remarks,
        "performed_by": current_user["email"],
        "timestamp": datetime.utcnow()
    }

    await db.inventory_transactions.insert_one(record)
    return {"message": "Transaction recorded successfully"}


@router.get("/")
async def get_transactions(
    item_id: Optional[str] = None,
    db=Depends(get_database),
    current_user=Depends(get_current_active_user)
):
    """Fetch inventory transaction logs."""
    query = {"item_id": item_id} if item_id else {}
    transactions = await db.inventory_transactions.find(query).sort("timestamp", -1).to_list(50)
    return {"transactions": transactions, "count": len(transactions)}
