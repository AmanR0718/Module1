"""
backend/app/services/qr_service.py
Handles secure QR code generation, verification, and Farmer ID card creation.
"""

import qrcode
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any
from app.config import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


class QRCodeService:
    def __init__(self):
        self.qr_dir = os.path.join(settings.UPLOAD_DIR, "qr_codes")
        os.makedirs(self.qr_dir, exist_ok=True)

    # ============================================================
    # 🔹 QR DATA GENERATION
    # ============================================================
    def generate_qr_data(self, farmer_id: str, farmer_data: Dict[str, Any]) -> str:
        """
        Generate QR payload as signed JSON string for the farmer.
        The payload includes farmer info + timestamp + signature.
        """
        try:
            qr_payload = {
                "farmer_id": farmer_id,
                "nrc": farmer_data.get("nrc_number"),
                "name": f"{farmer_data['personal_info']['first_name']} {farmer_data['personal_info']['last_name']}",
                "phone": farmer_data["personal_info"].get("phone_primary"),
                "province": farmer_data["address"].get("province"),
                "district": farmer_data["address"].get("district"),
                "chiefdom": farmer_data["address"].get("chiefdom"),
                "timestamp": datetime.utcnow().isoformat(),
            }

            qr_string = json.dumps(qr_payload, separators=(",", ":"))
            qr_payload["signature"] = self._generate_signature(qr_string)

            final_payload = json.dumps(qr_payload, separators=(",", ":"))
            logger.info(f"Generated QR data for farmer {farmer_id}")
            return final_payload
        except Exception as e:
            logger.error(f"QR data generation failed: {e}")
            raise

    # ============================================================
    # 🔹 SIGNATURE GENERATION
    # ============================================================
    def _generate_signature(self, data: str) -> str:
        """
        Generate digital signature using a mix of JWT and AES secrets.
        Ensures QR authenticity and tamper resistance.
        """
        try:
            secret_combo = f"{settings.JWT_SECRET_KEY}{settings.AES_ENCRYPTION_KEY}"
            signature_input = f"{data}{secret_combo}"
            return hashlib.sha256(signature_input.encode()).hexdigest()[:16]
        except Exception as e:
            logger.error(f"QR signature generation failed: {e}")
            raise

    def verify_qr_code(self, qr_data: str) -> bool:
        """Verify authenticity of a QR code by revalidating its signature."""
        try:
            data = json.loads(qr_data)
            provided_signature = data.pop("signature", "")
            original_data = json.dumps(data, separators=(",", ":"))
            expected_signature = self._generate_signature(original_data)
            is_valid = provided_signature == expected_signature

            if not is_valid:
                logger.warning("QR signature mismatch detected")
            return is_valid
        except Exception as e:
            logger.error(f"QR verification failed: {e}")
            return False

    # ============================================================
    # 🔹 QR IMAGE CREATION
    # ============================================================
    def generate_qr_image(self, qr_data: str, farmer_id: str) -> str:
        """
        Generate a QR code PNG image from JSON payload.
        """
        try:
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=8,
                border=3,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"{farmer_id}_qr.png"
            filepath = os.path.join(self.qr_dir, filename)
            img.save(filepath, "PNG", quality=95, optimize=True)

            logger.info(f"QR code image generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"QR image generation failed: {e}")
            raise

    # ============================================================
    # 🔹 ID CARD GENERATION
    # ============================================================
    def generate_id_card(self, farmer_data: Dict[str, Any], qr_image_path: str) -> str:
        """
        Generate a printable ID card for a farmer with their QR code.
        Card size: 86x54 mm @ 300 DPI (credit card standard).
        """
        try:
            # Dimensions
            width_px = int(86 * 300 / 25.4)
            height_px = int(54 * 300 / 25.4)

            # Create card base
            card = Image.new("RGB", (width_px, height_px), color="white")
            draw = ImageDraw.Draw(card)

            # Header
            header_height = 100
            draw.rectangle([(0, 0), (width_px, header_height)], fill="#198A48")

            # Load fonts (fallback safe)
            try:
                title_font = ImageFont.truetype("arial.ttf", 42)
                name_font = ImageFont.truetype("arial.ttf", 34)
                info_font = ImageFont.truetype("arial.ttf", 26)
            except Exception:
                title_font = ImageFont.load_default()
                name_font = ImageFont.load_default()
                info_font = ImageFont.load_default()

            # Title
            draw.text((50, 25), "ZAMBIAN FARMER ID", fill="white", font=title_font)

            # Farmer Info
            y_offset = header_height + 30
            full_name = f"{farmer_data['personal_info']['first_name']} {farmer_data['personal_info']['last_name']}"
            draw.text((50, y_offset), f"Name: {full_name}", fill="black", font=name_font)

            y_offset += 50
            draw.text((50, y_offset), f"ID: {farmer_data['farmer_id']}", fill="black", font=info_font)

            y_offset += 40
            draw.text((50, y_offset), f"NRC: {farmer_data['nrc_number']}", fill="black", font=info_font)

            y_offset += 40
            location = f"{farmer_data['address'].get('district', 'N/A')}, {farmer_data['address'].get('province', 'N/A')}"
            draw.text((50, y_offset), f"{location}", fill="black", font=info_font)

            # QR Code placement
            if os.path.exists(qr_image_path):
                qr_img = Image.open(qr_image_path)
                qr_img = qr_img.resize((220, 220))
                card.paste(qr_img, (width_px - 270, height_px - 260))

            # Save ID card
            card_filename = f"{farmer_data['farmer_id']}_id_card.png"
            card_path = os.path.join(self.qr_dir, card_filename)
            card.save(card_path, "PNG", optimize=True, quality=95)

            logger.info(f"ID card generated for {farmer_data['farmer_id']}: {card_path}")
            return card_path

        except Exception as e:
            logger.error(f"Failed to generate ID card: {e}", exc_info=True)
            raise
