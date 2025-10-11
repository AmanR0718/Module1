import qrcode
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any
from app.config import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class QRCodeService:
    def __init__(self):
        self.qr_dir = os.path.join(settings.UPLOAD_DIR, "qr_codes")
        os.makedirs(self.qr_dir, exist_ok=True)
    
    def generate_qr_data(self, farmer_id: str, farmer_data: Dict[str, Any]) -> str:
        """Generate QR code data string"""
        qr_payload = {
            "farmer_id": farmer_id,
            "nrc": farmer_data.get("nrc_number"),
            "name": f"{farmer_data['personal_info']['first_name']} {farmer_data['personal_info']['last_name']}",
            "phone": farmer_data['personal_info'].get('phone_primary'),
            "province": farmer_data['address'].get('province'),
            "district": farmer_data['address'].get('district'),
            "chiefdom": farmer_data['address'].get('chiefdom'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create JSON string
        qr_string = json.dumps(qr_payload, separators=(',', ':'))
        
        # Add digital signature
        signature = self._generate_signature(qr_string)
        qr_payload["signature"] = signature
        
        return json.dumps(qr_payload, separators=(',', ':'))
    
    def _generate_signature(self, data: str) -> str:
        """Generate digital signature for QR code"""
        signature_string = f"{data}{settings.JWT_SECRET_KEY}"
        return hashlib.sha256(signature_string.encode()).hexdigest()[:16]
    
    def verify_qr_code(self, qr_data: str) -> bool:
        """Verify QR code authenticity"""
        try:
            data = json.loads(qr_data)
            provided_signature = data.pop("signature", "")
            
            # Recreate data without signature
            original_data = json.dumps(data, separators=(',', ':'))
            expected_signature = self._generate_signature(original_data)
            
            return provided_signature == expected_signature
        except:
            return False
    
    def generate_qr_image(self, qr_data: str, farmer_id: str) -> str:
        """Generate QR code image file"""
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image
        filename = f"{farmer_id}_qr.png"
        filepath = os.path.join(self.qr_dir, filename)
        img.save(filepath)
        
        return filepath
    
    def generate_id_card(self, farmer_data: Dict[str, Any], qr_image_path: str) -> str:
        """Generate farmer ID card with QR code"""
        # Standard credit card size: 86mm x 54mm at 300 DPI
        width_px = int(86 * 300 / 25.4)  # ~1016px
        height_px = int(54 * 300 / 25.4)  # ~638px
        
        # Create blank card
        card = Image.new('RGB', (width_px, height_px), color='white')
        draw = ImageDraw.Draw(card)
        
        # Add Zambian flag colors (header)
        header_height = 100
        draw.rectangle([(0, 0), (width_px, header_height)], fill='#198A48')
        
        # Add title
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            name_font = ImageFont.truetype("arial.ttf", 32)
            info_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
        
        draw.text((50, 30), "ZAMBIAN FARMER ID", fill='white', font=title_font)
        
        # Add farmer information
        y_offset = header_height + 40
        name = f"{farmer_data['personal_info']['first_name']} {farmer_data['personal_info']['last_name']}"
        draw.text((50, y_offset), f"Name: {name}", fill='black', font=name_font)
        
        y_offset += 50
        draw.text((50, y_offset), f"ID: {farmer_data['farmer_id']}", fill='black', font=info_font)
        
        y_offset += 40
        draw.text((50, y_offset), f"NRC: {farmer_data['nrc_number']}", fill='black', font=info_font)
        
        y_offset += 40
        district = farmer_data['address'].get('district', 'N/A')
        province = farmer_data['address'].get('province', 'N/A')
        draw.text((50, y_offset), f"{district}, {province}", fill='black', font=info_font)
        
        # Add QR code
        if os.path.exists(qr_image_path):
            qr_img = Image.open(qr_image_path)
            qr_img = qr_img.resize((200, 200))
            card.paste(qr_img, (width_px - 250, height_px - 250))
        
        # Save ID card
        card_filename = f"{farmer_data['farmer_id']}_id_card.png"
        card_path = os.path.join(self.qr_dir, card_filename)
        card.save(card_path, 'PNG', quality=95)
        
        return card_path