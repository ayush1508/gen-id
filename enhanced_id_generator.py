import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import uuid
import random
from typing import Optional, Tuple

class EnhancedIDCardGenerator:
    def __init__(self):
        self.output_dir = "generated_cards"
        self.templates_dir = "templates"
        self.photos_dir = "user_photos"
        self.logos_dir = "college_logos"
        self.ensure_directories()
        
        # Blood group options
        self.blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        # College information with logo paths
        self.colleges = {
            "1": {
                "name": "INDIAN INSTITUTE OF SCIENCE (IISc) BANGALORE",
                "short_name": "IISc Bangalore",
                "logo_path": "college_logos/IISc_Bangalore_logo.png",
                "colors": {"primary": "#1E3A8A", "secondary": "#3B82F6", "text": "#1F2937"},
                "authority": "Academic Office, IISc Bangalore"
            },
            "2": {
                "name": "INDIAN INSTITUTE OF TECHNOLOGY (IIT) MADRAS",
                "short_name": "IIT Madras",
                "logo_path": "college_logos/IIT_Madras_logo.png",
                "colors": {"primary": "#7C2D12", "secondary": "#DC2626", "text": "#1F2937"},
                "authority": "Academic Section, IIT Madras"
            },
            "3": {
                "name": "INDIAN INSTITUTE OF TECHNOLOGY (IIT) BOMBAY",
                "short_name": "IIT Bombay",
                "logo_path": "college_logos/IIT_Bombay_logo.png",
                "colors": {"primary": "#1E40AF", "secondary": "#DC2626", "text": "#1F2937"},
                "authority": "Academic Office, IIT Bombay"
            },
            "4": {
                "name": "INDIAN INSTITUTE OF TECHNOLOGY (IIT) DELHI",
                "short_name": "IIT Delhi",
                "logo_path": "college_logos/IIT_Delhi_logo.png",
                "colors": {"primary": "#DC2626", "secondary": "#FFFFFF", "text": "#1F2937"},
                "authority": "Academic Section, IIT Delhi"
            },
            "5": {
                "name": "JAWAHARLAL NEHRU UNIVERSITY (JNU)",
                "short_name": "JNU",
                "logo_path": "college_logos/JNU_logo.jpg",
                "colors": {"primary": "#1E40AF", "secondary": "#FFFFFF", "text": "#1F2937"},
                "authority": "Academic Branch, JNU"
            }
        }
    
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.photos_dir, exist_ok=True)
        os.makedirs(self.logos_dir, exist_ok=True)
    
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
    
    def load_college_logo(self, college_id: str) -> Optional[Image.Image]:
        """Load college logo if available"""
        try:
            college_info = self.colleges.get(college_id)
            if not college_info:
                return None
            
            logo_path = college_info["logo_path"]
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
                # Convert to RGBA if necessary
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')
                # Resize logo to appropriate size (90x90)
                logo = logo.resize((90, 90), Image.Resampling.LANCZOS)
                return logo
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        return None
    
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
    
    def generate_random_blood_group(self) -> str:
        """Generate random blood group"""
        return random.choice(self.blood_groups)
    
    def create_professional_template(self, college_id: str) -> Image.Image:
        """Create a professional template with logo and enhanced design"""
        college_info = self.colleges[college_id]
        
        # Standard ID card dimensions (CR80 format scaled up)
        width, height = 640, 1000
        
        # Create base image
        card = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(card)
        
        # Colors
        primary_color = college_info["colors"]["primary"]
        secondary_color = college_info["colors"]["secondary"]
        
        # Header section with gradient effect
        header_height = 160
        draw.rectangle([0, 0, width, header_height], fill=primary_color)
        
        # Load and place college logo
        logo = self.load_college_logo(college_id)
        if logo:
            logo_x = 30
            logo_y = 35
            card.paste(logo, (logo_x, logo_y), logo)
            
            # College name positioned next to logo
            college_name = college_info["name"]
            title_font = self.get_font(28, bold=True)
            
            # Calculate text width for underlining
            text_width = draw.textlength(college_name, font=title_font)
            
            # Position for the college name
            text_x = logo_x + 110
            text_y = 60
            
            draw.text((text_x, text_y), college_name, font=title_font, fill="white")
            
            # Underline the text
            underline_y = text_y + title_font.getbbox(college_name)[3] + 5 # Adjust based on font metrics
            draw.line((text_x, underline_y, text_x + text_width, underline_y), fill="white", width=2)
        else:
            # Fallback: center the college name if no logo
            college_name = college_info["name"]
            title_font = self.get_font(30, bold=True)
            
            # Calculate text width for underlining
            text_width = draw.textlength(college_name, font=title_font)
            
            # Position for the college name
            text_x = (width - text_width) // 2
            text_y = 60
            
            draw.text((text_x, text_y), college_name, font=title_font, fill="white")
            
            # Underline the text
            underline_y = text_y + title_font.getbbox(college_name)[3] + 5 # Adjust based on font metrics
            draw.line((text_x, underline_y, text_x + text_width, underline_y), fill="white", width=2)
        
        # Student ID banner
        banner_y = header_height
        banner_height = 60
        draw.rectangle([0, banner_y, width, banner_y + banner_height], fill=secondary_color)
        
        id_font = self.get_font(32, bold=True)
        draw.text((width//2, banner_y + 30), "STUDENT ID", font=id_font, fill="white", anchor="mm")
        
        # Footer with college branding
        footer_height = 50
        draw.rectangle([0, height - footer_height, width, height], fill=primary_color)
        
        return card
    
    async def generate_id_card(self, college_id: str, student_name: str, 
                             father_name: str, phone: str, department: str, 
                             qr_data: str, photo_path: str = None) -> str:
        """Generate ID card with enhanced quality, logo, and blood group"""
        
        college_info = self.colleges.get(college_id)
        if not college_info:
            raise ValueError(f"Invalid college ID: {college_id}")
        
        # Create professional template
        card = self.create_professional_template(college_id)
        draw = ImageDraw.Draw(card)
        
        # Get dimensions
        card_width, card_height = card.size
        
        # Colors
        text_color = college_info["colors"]["text"]
        
        # Fonts with enhanced sizing
        label_font = self.get_font(18, bold=True)
        value_font = self.get_font(22)
        name_font = self.get_font(30, bold=True) # Larger and bolder name
        small_font = self.get_font(16)
        
        # Photo section
        photo_x, photo_y = 50, 240
        photo_width, photo_height = 150, 180
        
        if photo_path and os.path.exists(photo_path):
            # Process and add user photo
            user_photo = self.process_user_photo(photo_path)
            card.paste(user_photo, (photo_x, photo_y))
            
            # Add photo border
            draw.rectangle([photo_x-2, photo_y-2, photo_x + photo_width+2, photo_y + photo_height+2], 
                          outline="black", width=2)
        else:
            # Draw photo placeholder with border
            draw.rectangle([photo_x, photo_y, photo_x + photo_width, photo_y + photo_height], 
                          outline="black", width=3, fill="#F3F4F6")
            photo_font = self.get_font(16)
            draw.text((photo_x + photo_width//2, photo_y + photo_height//2), "PHOTO", 
                     font=photo_font, fill="gray", anchor="mm")
        
        # Information section (right side of photo)
        info_x = photo_x + photo_width + 40
        info_y = photo_y + 10
        line_height = 45
        
        # Student name
        draw.text((info_x, info_y), "STUDENT NAME", font=label_font, fill=text_color)
        draw.text((info_x, info_y + 25), student_name.upper(), font=name_font, fill=text_color)
        
        # Father's name
        draw.text((info_x, info_y + line_height * 2), "FATHER'S NAME", font=label_font, fill=text_color)
        draw.text((info_x, info_y + line_height * 2 + 25), father_name, font=value_font, fill=text_color)
        
        # Student ID Number (generated)
        student_id = f"{college_info['short_name'][:3].upper()}{random.randint(100000, 999999)}"
        draw.text((info_x, info_y + line_height * 4), "STUDENT ID:", font=label_font, fill=text_color)
        draw.text((info_x, info_y + line_height * 4 + 25), student_id, font=value_font, fill=text_color)
        
        # Information below photo, aligned to the left
        below_photo_y = photo_y + photo_height + 40
        left_align_x = 50
        
        # Phone number
        draw.text((left_align_x, below_photo_y), "PHONE:", font=label_font, fill=text_color)
        draw.text((left_align_x, below_photo_y + 25), phone, font=value_font, fill=text_color)
        
        # Department
        draw.text((left_align_x, below_photo_y + line_height), "DEPARTMENT:", font=label_font, fill=text_color)
        
        # Truncate long department names
        if len(department) > 30:
            department = department[:27] + "..."
        
        draw.text((left_align_x, below_photo_y + line_height + 25), department, font=value_font, fill=text_color)
        
        # Blood Group - NEW FIELD
        blood_group = self.generate_random_blood_group()
        draw.text((left_align_x, below_photo_y + line_height * 2), "BLOOD GROUP:", font=label_font, fill=text_color)
        draw.text((left_align_x, below_photo_y + line_height * 2 + 25), blood_group, font=value_font, fill="#DC2626")  # Red color for blood group
        
        # Issue authority
        authority_y = card_height - 220
        draw.text((left_align_x, authority_y), "ISSUED BY:", font=label_font, fill=text_color)
        draw.text((left_align_x, authority_y + 25), college_info["authority"], font=small_font, fill=text_color)
        
        # Issue date
        from datetime import datetime
        issue_date = datetime.now().strftime("%d/%m/%Y")
        draw.text((left_align_x, authority_y + 50), f"ISSUE DATE: {issue_date}", font=small_font, fill=text_color)
        
        # Generate and add QR code
        enhanced_qr_data = f"Name: {student_name}\nFather: {father_name}\nPhone: {phone}\nCollege: {college_info['name']}\nDept: {department}\nBlood Group: {blood_group}\nStudent ID: {student_id}\nIssue Date: {issue_date}"
        qr_img = self.generate_qr_code(enhanced_qr_data, 130)
        
        # Position QR code (bottom right)
        qr_x = card_width - 150
        qr_y = card_height - 170
        
        # Add white background for QR code
        qr_bg = Image.new("RGB", (140, 140), "white")
        card.paste(qr_bg, (qr_x-5, qr_y-5))
        card.paste(qr_img, (qr_x, qr_y))
        
        # Add QR code label
        draw.text((qr_x + 65, qr_y - 25), "SCAN FOR VERIFICATION", 
                 font=self.get_font(10, bold=True), fill=text_color, anchor="mm")
        
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

