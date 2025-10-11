from typing import List, Dict, Any
from datetime import datetime
from app.database import get_database
from fastapi import HTTPException, status

class SyncService:
    def __init__(self, db):
        self.db = db
    
    async def batch_sync_farmers(self, farmers_data: List[Dict[str, Any]], user_id: str) -> Dict:
        """Sync multiple farmers from offline mobile app"""
        successful = []
        failed = []
        
        for farmer_data in farmers_data:
            try:
                # Check if farmer already exists (by temporary mobile ID)
                temp_id = farmer_data.get("temp_id")
                existing = None
                
                if temp_id:
                    existing = await self.db.farmers.find_one({"temp_id": temp_id})
                
                if existing:
                    # Update existing farmer
                    await self._update_farmer_from_sync(existing["farmer_id"], farmer_data)
                    successful.append({
                        "temp_id": temp_id,
                        "farmer_id": existing["farmer_id"],
                        "status": "updated"
                    })
                else:
                    # Create new farmer
                    result = await self._create_farmer_from_sync(farmer_data, user_id)
                    successful.append({
                        "temp_id": temp_id,
                        "farmer_id": result["farmer_id"],
                        "status": "created"
                    })
                    
            except Exception as e:
                failed.append({
                    "temp_id": farmer_data.get("temp_id"),
                    "error": str(e)
                })
        
        return {
            "total": len(farmers_data),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": failed
        }
    
    async def _create_farmer_from_sync(self, farmer_data: Dict, user_id: str) -> Dict:
        """Create new farmer from sync data"""
        from app.services.farmer_service import FarmerService
        from app.services.qr_service import QRCodeService
        
        farmer_service = FarmerService(self.db)
        qr_service = QRCodeService()
        
        # Validate data
        await farmer_service.validate_farmer_data(farmer_data)
        
        # Generate farmer ID
        farmer_id = await farmer_service.generate_farmer_id()
        
        # Prepare farmer document
        farmer_doc = {
            **farmer_data,
            "farmer_id": farmer_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": user_id,
            "synced_at": datetime.utcnow()
        }
        
        # Generate QR code
        qr_data = qr_service.generate_qr_data(farmer_id, farmer_doc)
        qr_image_path = qr_service.generate_qr_image(qr_data, farmer_id)
        
        farmer_doc["qr_code"] = qr_data
        farmer_doc["qr_code_image_path"] = qr_image_path
        
        # Insert into database
        result = await self.db.farmers.insert_one(farmer_doc)
        
        return {
            "farmer_id": farmer_id,
            "id": str(result.inserted_id)
        }
    
    async def _update_farmer_from_sync(self, farmer_id: str, farmer_data: Dict) -> None:
        """Update existing farmer from sync data"""
        update_data = {
            **farmer_data,
            "updated_at": datetime.utcnow(),
            "synced_at": datetime.utcnow()
        }
        
        await self.db.farmers.update_one(
            {"farmer_id": farmer_id},
            {"$set": update_data}
        )
    
    async def get_sync_status(self, user_id: str, last_sync: datetime) -> Dict:
        """Get data changes since last sync for mobile app"""
        # Get farmers created/updated since last sync
        query = {
            "created_by": user_id,
            "updated_at": {"$gt": last_sync}
        }
        
        farmers = await self.db.farmers.find(query).to_list(None)
        
        return {
            "last_sync": last_sync.isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "updates_count": len(farmers),
            "farmers": [
                {
                    "farmer_id": f["farmer_id"],
                    "updated_at": f["updated_at"].isoformat(),
                    "status": f.get("registration_status")
                }
                for f in farmers
            ]
        }