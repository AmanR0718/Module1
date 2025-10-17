"""
backend/app/routes/reports.py
Reporting Endpoints for Zambian Farmer Support System.
Generates summaries, analytics, and exportable reports for admin dashboards.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Response,
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook

from app.models.user import UserInDB, UserRole
from app.routes.auth import require_role
from app.core.database import get_database

router = APIRouter(prefix="/api/reports", tags=["Reports"])


# ============================================================
# 🔹 Farmer Reports
# ============================================================
@router.get("/farmers/summary", status_code=status.HTTP_200_OK)
async def farmer_summary_report(
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    province: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.EXTENSION_OFFICER])),
):
    """
    Generate summary statistics of farmer registrations by date range and region.
    """
    query = {}
    if start_date and end_date:
        query["created_at"] = {"$gte": start_date, "$lte": end_date}
    if province:
        query["address.province"] = province
    if district:
        query["address.district"] = district

    total = await db.farmers.count_documents(query)
    active = await db.farmers.count_documents({**query, "registration_status": "active"})
    pending = await db.farmers.count_documents({**query, "registration_status": "pending"})

    province_group = await db.farmers.aggregate([
        {"$match": query},
        {"$group": {"_id": "$address.province", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(length=None)

    return {
        "total_farmers": total,
        "active_farmers": active,
        "pending_farmers": pending,
        "by_province": province_group,
    }


# ============================================================
# 🔹 Inventory Reports
# ============================================================
@router.get("/inventory/status", status_code=status.HTTP_200_OK)
async def inventory_status_report(
    category: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.EXTENSION_OFFICER])),
):
    """
    Get inventory report by category or stock level.
    """
    query = {}
    if category:
        query["category"] = category
    if low_stock_only:
        query["$expr"] = {"$lte": ["$quantity", "$reorder_level"]}

    items = await db.inventory.find(query).to_list(length=1000)
    total_value = sum((item.get("quantity", 0) or 0) * (item.get("unit_price", 0) or 0) for item in items)
    total_items = len(items)

    return {
        "total_items": total_items,
        "total_value": total_value,
        "low_stock_items": [i for i in items if i["quantity"] <= i["reorder_level"]],
    }


# ============================================================
# 🔹 Generate PDF Report
# ============================================================
@router.get("/export/pdf", response_description="Generate PDF summary report")
async def export_report_pdf(
    report_type: str = Query(..., description="Type of report: farmers/inventory"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN])),
):
    """
    Export summary reports as downloadable PDF files.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Zambian Farmer Support System Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Report Type: {report_type.title()}")
    c.drawString(50, height - 100, f"Generated On: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    if report_type == "farmers":
        total = await db.farmers.count_documents({})
        active = await db.farmers.count_documents({"registration_status": "active"})
        c.drawString(50, height - 140, f"Total Farmers: {total}")
        c.drawString(50, height - 160, f"Active Farmers: {active}")
    elif report_type == "inventory":
        total = await db.inventory.count_documents({})
        low_stock = await db.inventory.count_documents({"$expr": {"$lte": ["$quantity", "$reorder_level"]}})
        c.drawString(50, height - 140, f"Total Inventory Items: {total}")
        c.drawString(50, height - 160, f"Low Stock Items: {low_stock}")
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    c.showPage()
    c.save()
    buffer.seek(0)

    headers = {"Content-Disposition": f"attachment; filename={report_type}_report.pdf"}
    return Response(buffer.getvalue(), media_type="application/pdf", headers=headers)


# ============================================================
# 🔹 Generate Excel Report
# ============================================================
@router.get("/export/excel", response_description="Generate Excel report")
async def export_report_excel(
    report_type: str = Query(..., description="Type of report: farmers/inventory"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN])),
):
    """
    Export summary reports as Excel (.xlsx) files.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = f"{report_type.capitalize()} Report"
    ws.append(["Zambian Farmer Support System - Summary Report"])
    ws.append(["Generated On", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
    ws.append([])

    if report_type == "farmers":
        ws.append(["Province", "Total Farmers"])
        pipeline = [
            {"$group": {"_id": "$address.province", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        data = await db.farmers.aggregate(pipeline).to_list(length=None)
        for item in data:
            ws.append([item["_id"], item["count"]])
    elif report_type == "inventory":
        ws.append(["Category", "Total Items", "Low Stock"])
        pipeline = [
            {"$group": {"_id": "$category", "total": {"$sum": 1}}},
        ]
        data = await db.inventory.aggregate(pipeline).to_list(length=None)
        for item in data:
            low_stock = await db.inventory.count_documents(
                {"category": item["_id"], "$expr": {"$lte": ["$quantity", "$reorder_level"]}}
            )
            ws.append([item["_id"], item["total"], low_stock])
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    # Save workbook to memory
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    headers = {"Content-Disposition": f"attachment; filename={report_type}_report.xlsx"}
    return Response(
        output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
