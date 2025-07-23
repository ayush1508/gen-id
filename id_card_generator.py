import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import uuid
from typing import Optional, Tuple

class ImprovedIDCardGenerator:
    def __init__(self):
        self.output_dir = "generated_cards"
        self.templates_dir = "templates"
        self.photos_dir = "user_photos"
        self.ensure_directories()
        
        # College information
        self.colleges = {
            "1": {
                "name": "Indian Institute of Science (IISc) Bangalore",
                "colors": {"primary": "#1E3A8A", "secondary": "#3B82F6", "text": "#1F2937"},
                "authority": "Academic Office, IISc Bangalore"
            },
            "2": {
                "name": "Indian Institute of Technology (IIT) Madras",
                "colors": {"primary": "#7C2D12", "secondary": "#DC2626", "text": "#1F2937"},
                "authority": "Academic Section, IIT Madras"
            },
            "3": {
                "name": "Indian Institute of Technology (IIT) Bombay",
                "colors": {"primary": "#1E40AF", "secondary": "#DC2626", "text": "#1F2937"},
                "authority": "Academic Office, IIT Bombay"
            },
            "4": {
                "name": "Indian Institute of Technology (IIT) Delhi",
                "colors": {"primary": "#DC2626", "secondary": "#FFFFFF", "text": "#1F2937"},
                "authority": "Academic Section, IIT Delhi"
            },
            "5": {
                "name": "Jawaharlal Nehru University (JNU)",
                "colors": {"primary": "#1E40AF", "secondary": "#FFFFFF", "text": "#1F2937"},
                "authority": "Academic Branch, JNU"
            }
        }
    
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.photos_dir, exist_ok=True)
    
    def generate_qr_code(self, data: str, size: int = 120) -> Image.Image:
        """Generate QR code image with better quality"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
        return qr_img
    
    def get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Get font with better fallback system"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def process_user_photo(self, photo_path: str) -> Image.Image:
        """Process user photo for ID card"""
        try:
            # Open and process the photo
            photo = Image.open(photo_path)
            
            # Convert to RGB if necessary
            if photo.mode != 'RGB':
                photo = photo.convert('RGB')
            
            # Resize to standard ID photo size (150x180 pixels)
            photo_width, photo_height = 150, 180
            
            # Calculate aspect ratio
            original_width, original_height = photo.size
            aspect_ratio = original_width / original_height
            
            # Crop to fit the ID photo dimensions
            if aspect_ratio > (photo_width / photo_height):
                # Photo is wider, crop width
                new_height = original_height
                new_width = int(new_height * (photo_width / photo_height))
                left = (original_width - new_width) // 2
                photo = photo.crop((left, 0, left + new_width, new_height))
            else:
                # Photo is taller, crop height
                new_width = original_width
                new_height = int(new_width * (photo_height / photo_width))
                top = (original_height - new_height) // 2
                photo = photo.crop((0, top, new_width, top + new_height))
            
            # Resize to exact dimensions
            photo = photo.resize((photo_width, photo_height), Image.Resampling.LANCZOS)
            
            return photo
            
        except Exception as e:
            print(f"Error processing photo: {e}")
            # Return a placeholder if photo processing fails
            placeholder = Image.new('RGB', (150, 180), '#F3F4F6')
            draw = ImageDraw.Draw(placeholder)
            font = self.get_font(16)
            draw.text((75, 90), "PHOTO", font=font, fill="gray", anchor="mm")
            return placeholder
    
    def create_clean_template(self, college_id: str) -> Image.Image:
        """Create a clean template without duplicate fields"""
        college_info = self.colleges[college_id]
        
        # Standard ID card dimensions (CR80 format scaled up)
        width, height = 640, 1000
        
        # Create base image
        card = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(card)
        
        # Colors
        primary_color = college_info["colors"]["primary"]
        secondary_color = college_info["colors"]["secondary"]
        
        # Header section
        header_height = 140
        draw.rectangle([0, 0, width, header_height], fill=primary_color)
        
        # College name
        college_name = college_info["name"]
        title_font = self.get_font(22, bold=True)
        
        # Split long college names into multiple lines
        if len(college_name) > 35:
            words = college_name.split()
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            
            draw.text((width//2, 45), line1, font=title_font, fill="white", anchor="mm")
            draw.text((width//2, 75), line2, font=title_font, fill="white", anchor="mm")
        else:
            draw.text((width//2, 60), college_name, font=title_font, fill="white", anchor="mm")
        
        # Student ID banner
        banner_y = header_height
        banner_height = 60
        draw.rectangle([0, banner_y, width, banner_y + banner_height], fill=secondary_color)
        
        id_font = self.get_font(28, bold=True)
        draw.text((width//2, banner_y + 30), "STUDENT ID", font=id_font, fill="white", anchor="mm")
        
        # Footer
        draw.rectangle([0, height - 40, width, height], fill=primary_color)
        
        return card
    
    async def generate_id_card(self, college_id: str, student_name: str, 
                             father_name: str, phone: str, department: str, 
                             qr_data: str, photo_path: str = None) -> str:
        """Generate ID card with enhanced quality and photo support"""
        
        college_info = self.colleges.get(college_id)
        if not college_info:
            raise ValueError(f"Invalid college ID: {college_id}")
        
        # Create clean template
        card = self.create_clean_template(college_id)
        draw = ImageDraw.Draw(card)
        
        # Get dimensions
        card_width, card_height = card.size
        
        # Colors
        text_color = college_info["colors"]["text"]
        
        # Fonts
        name_font = self.get_font(26, bold=True)
        father_font = self.get_font(20)
        info_font = self.get_font(18)
        small_font = self.get_font(16)
        label_font = self.get_font(14, bold=True)
        
        # Photo section
        photo_x, photo_y = 50, 220
        photo_width, photo_height = 150, 180
        
        if photo_path and os.path.exists(photo_path):
            # Process and add user photo
            user_photo = self.process_user_photo(photo_path)
            card.paste(user_photo, (photo_x, photo_y))
        else:
            # Draw photo placeholder
            draw.rectangle([photo_x, photo_y, photo_x + photo_width, photo_y + photo_height], 
                          outline="black", width=3, fill="#F3F4F6")
            photo_font = self.get_font(16)
            draw.text((photo_x + photo_width//2, photo_y + photo_height//2), "PHOTO", 
                     font=photo_font, fill="gray", anchor="mm")
        
        # Information section (right side of photo)
        info_x = photo_x + photo_width + 30
        info_y = photo_y + 20
        
        # Student name
        draw.text((info_x, info_y), "STUDENT NAME:", font=label_font, fill=text_color)
        
        # Handle long names
        if len(student_name) > 18:
            name_font = self.get_font(22, bold=True)
        
        draw.text((info_x, info_y + 25), student_name.upper(), font=name_font, fill=text_color)
        
        # Father's name
        draw.text((info_x, info_y + 70), "FATHER'S NAME:", font=label_font, fill=text_color)
        draw.text((info_x, info_y + 95), father_name, font=father_font, fill=text_color)
        
        # Information below photo
        below_photo_y = photo_y + photo_height + 30
        
        # Phone number (single entry)
        draw.text((50, below_photo_y), "PHONE:", font=label_font, fill=text_color)
        draw.text((50, below_photo_y + 25), phone, font=info_font, fill=text_color)
        
        # Department (single entry)
        draw.text((50, below_photo_y + 65), "DEPARTMENT:", font=label_font, fill=text_color)
        
        # Truncate long department names
        if len(department) > 35:
            department = department[:32] + "..."
        
        draw.text((50, below_photo_y + 90), department, font=info_font, fill=text_color)
        
        # Issue authority
        authority_y = card_height - 200
        draw.text((50, authority_y), "ISSUED BY:", font=label_font, fill=text_color)
        draw.text((50, authority_y + 25), college_info["authority"], font=small_font, fill=text_color)
        
        # Generate and add QR code
        qr_img = self.generate_qr_code(qr_data, 120)
        
        # Position QR code (bottom right)
        qr_x = card_width - 140
        qr_y = card_height - 140
        
        # Add white background for QR code
        qr_bg = Image.new("RGB", (130, 130), "white")
        card.paste(qr_bg, (qr_x-5, qr_y-5))
        card.paste(qr_img, (qr_x, qr_y))
        
        # Add QR code label
        draw.text((qr_x + 60, qr_y - 20), "SCAN FOR VERIFICATION", 
                 font=self.get_font(10), fill=text_color, anchor="mm")
        
        # Generate unique filename
        card_filename = f"id_card_{college_id}_{uuid.uuid4().hex[:8]}.png"
        card_path = os.path.join(self.output_dir, card_filename)
        
        # Save with maximum quality
        card.save(card_path, "PNG", quality=100, optimize=True, dpi=(300, 300))
        
        return card_path
    
    def save_user_photo(self, photo_file_path: str, user_id: int) -> str:
        """Save user photo to photos directory"""
        try:
            # Generate unique filename for user photo
            photo_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            saved_photo_path = os.path.join(self.photos_dir, photo_filename)
            
            # Open and save the photo
            with Image.open(photo_file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save with good quality
                img.save(saved_photo_path, "JPEG", quality=90)
            
            return saved_photo_path
            
        except Exception as e:
            print(f"Error saving user photo: {e}")
            return None
    
    def cleanup_old_cards(self, max_cards: int = 100):
        """Clean up old generated cards to save space"""
        try:
            cards = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith("id_card_") and filename.endswith(".png"):
                    filepath = os.path.join(self.output_dir, filename)
                    cards.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time (oldest first)
            cards.sort(key=lambda x: x[1])
            
            # Remove oldest cards if we exceed the limit
            if len(cards) > max_cards:
                for filepath, _ in cards[:-max_cards]:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
        except Exception:
            pass  # Ignore cleanup errors
    
    def cleanup_old_photos(self, max_photos: int = 200):
        """Clean up old user photos to save space"""
        try:
            photos = []
            for filename in os.listdir(self.photos_dir):
                if filename.startswith("user_") and filename.endswith(".jpg"):
                    filepath = os.path.join(self.photos_dir, filename)
                    photos.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time (oldest first)
            photos.sort(key=lambda x: x[1])
            
            # Remove oldest photos if we exceed the limit
            if len(photos) > max_photos:
                for filepath, _ in photos[:-max_photos]:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
        except Exception:
            pass  # Ignore cleanup errors

