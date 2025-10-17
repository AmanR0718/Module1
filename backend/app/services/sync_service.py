"""
backend/app/services/sync_service.py
Handles offline → online farmer data synchronization for the mobile app.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException, status
import logging

from app.services.farmer_service import FarmerService
from app.services.qr_service import QRCodeService

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self, db):
        self.db = db

    # ============================================================
    # 🔹 Batch Sync (Offline → Online)
    # ============================================================
    async def batch_sync_farmers(self, farmers_data: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
        """
        Synchronize multiple farmer records received from mobile app.

        Performs:
        - Validation
        - Duplicate detection
        - Create/update operations
        - QR code generation
        Returns detailed results per record.
        """
        successful, failed = [], []

        logger.info(f"📡 Sync initiated by {user_id}: {len(farmers_data)} farmers")

        for idx, farmer_data in enumerate(farmers_data, start=1):
            temp_id = farmer_data.get("temp_id") or f"offline_{idx}"

            try:
                existing = None
                if temp_id:
                    existing = await self.db.farmers.find_one({"temp_id": temp_id})

                if existing:
                    await self._update_farmer_from_sync(existing["farmer_id"], farmer_data)
                    successful.append({
                        "temp_id": temp_id,
                        "farmer_id": existing["farmer_id"],
                        "status": "updated",
                    })
                else:
                    result = await self._create_farmer_from_sync(farmer_data, user_id)
                    successful.append({
                        "temp_id": temp_id,
                        "farmer_id": result["farmer_id"],
                        "status": "created",
                    })

            except HTTPException as e:
                failed.append({
                    "temp_id": temp_id,
                    "error": e.detail,
                })
                logger.warning(f"⚠️ Validation error for temp_id={temp_id}: {e.detail}")

            except Exception as e:
                failed.append({
                    "temp_id": temp_id,
                    "error": str(e),
                })
                logger.error(f"❌ Unexpected sync failure for temp_id={temp_id}: {e}", exc_info=True)

        return {
            "total": len(farmers_data),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": failed,
            "server_timestamp": datetime.utcnow().isoformat(),
        }

    # ============================================================
    # 🔹 Create Farmer from Sync
    # ============================================================
    async def _create_farmer_from_sync(self, farmer_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Insert a new farmer record received from mobile sync."""
        farmer_service = FarmerService(self.db)
        qr_service = QRCodeService()

        # Validate farmer data
        await farmer_service.validate_farmer_data(farmer_data)

        # Generate farmer ID
        farmer_id = await farmer_service.generate_farmer_id()

        # Assign chief based on GPS (if provided)
        gps = farmer_data.get("address", {}).get("gps_coordinates", {})
        assigned_chief = await farmer_service.assign_chief(gps) if gps else None

        # Prepare farmer document
        now = datetime.utcnow()
        farmer_doc = {
            **farmer_data,
            "farmer_id": farmer_id,
            "assigned_chief": assigned_chief,
            "created_at": now,
            "updated_at": now,
            "created_by": user_id,
            "synced_at": now,
            "source": "mobile_app",
        }

        # Generate QR code
        try:
            qr_data = qr_service.generate_qr_data(farmer_id, farmer_doc)
            qr_image_path = qr_service.generate_qr_image(qr_data, farmer_id)
            farmer_doc["qr_code"] = qr_data
            farmer_doc["qr_code_image_path"] = qr_image_path
        except Exception as e:
            logger.warning(f"⚠️ QR code generation failed for {farmer_id}: {e}")

        # Insert farmer
        result = await self.db.farmers.insert_one(farmer_doc)
        logger.info(f"✅ Synced farmer {farmer_id} by user {user_id}")

        return {"farmer_id": farmer_id, "id": str(result.inserted_id)}

    # ============================================================
    # 🔹 Update Farmer from Sync
    # ============================================================
    async def _update_farmer_from_sync(self, farmer_id: str, farmer_data: Dict[str, Any]) -> None:
        """Update an existing farmer record from mobile sync data."""
        now = datetime.utcnow()
        update_data = {
            **farmer_data,
            "updated_at": now,
            "synced_at": now,
        }

        result = await self.db.farmers.update_one(
            {"farmer_id": farmer_id},
            {"$set": update_data},
        )

        if result.modified_count > 0:
            logger.info(f"🔄 Farmer {farmer_id} updated successfully.")
        else:
            logger.warning(f"⚠️ Farmer {farmer_id} update operation had no effect.")

    # ============================================================
    # 🔹 Get Sync Status (Server → Mobile)
    # ============================================================
    async def get_sync_status(self, user_id: str, last_sync: datetime) -> Dict[str, Any]:
        """
        Get all farmer records created or updated since the last sync.
        Used by mobile clients to perform incremental sync.
        """
        if not last_sync:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'last_sync' parameter.",
            )

        query = {
            "created_by": user_id,
            "updated_at": {"$gt": last_sync},
        }

        farmers = await self.db.farmers.find(query, {
            "farmer_id": 1,
            "updated_at": 1,
            "registration_status": 1,
        }).to_list(None)

        logger.info(f"📤 Sync status requested by {user_id}: {len(farmers)} updates since {last_sync}")

        return {
            "user_id": user_id,
            "last_sync": last_sync.isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "updates_count": len(farmers),
            "farmers": [
                {
                    "farmer_id": f.get("farmer_id"),
                    "updated_at": f.get("updated_at").isoformat() if f.get("updated_at") else None,
                    "status": f.get("registration_status", "unknown"),
                }
                for f in farmers
            ],
        }
