from PIL import Image, ImageDraw, ImageFont
import os
import math

def draw_text_right(draw, y_pos, text, font, image_width, margin_right=50, text_color=(255,255,255), shadow_color=(0,0,0)):
    """
    Menggambar teks rata kanan (kompatibel dengan PIL terbaru)
    """
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_pos = image_width - margin_right - text_width
    # Shadow
    draw.text((x_pos+2, y_pos+2), text, font=font, fill=shadow_color)
    # Text
    draw.text((x_pos, y_pos), text, font=font, fill=text_color)
    return y_pos + text_height + 5  # kembalikan y_pos berikutnya

def add_timestamp_location(image_path, output_path, location_info, map_path="map.jpg"):
    img = Image.open(image_path)
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    # FONT
    font_size_main = 32
    font_size_secondary = 28
    try:
        font_main = ImageFont.truetype("arial.ttf", font_size_main)
        font_secondary = ImageFont.truetype("arial.ttf", font_size_secondary)
        font_compass = ImageFont.truetype("arial.ttf", 18)
    except:
        font_main = ImageFont.load_default()
        font_secondary = ImageFont.load_default()
        font_compass = ImageFont.load_default()
    
    text_color = (255, 255, 255)
    shadow_color = (0, 0, 0)
    
    # === KOMPAS di kiri atas ===
    compass_size = 120
    compass_x = 30
    compass_y = 30
    draw.ellipse(
        [compass_x, compass_y, compass_x + compass_size, compass_y + compass_size],
        outline=(100, 100, 100),
        fill=(230, 230, 200),
        width=4
    )
    
    center_x = compass_x + compass_size // 2
    center_y = compass_y + compass_size // 2
    needle_length = compass_size // 2 - 10
    
    # === JARUM FLEKSIBEL ===
    angle_deg = location_info.get('compass_angle', 0)  # default utara
    angle_rad = math.radians(angle_deg)
    
    x_tip = center_x + needle_length * math.sin(angle_rad)
    y_tip = center_y - needle_length * math.cos(angle_rad)
    
    x_left = center_x - 5 * math.cos(angle_rad)
    y_left = center_y - 5 * math.sin(angle_rad)
    x_right = center_x + 5 * math.cos(angle_rad)
    y_right = center_y + 5 * math.sin(angle_rad)
    
    draw.polygon(
        [(x_tip, y_tip), (x_left, y_left), (x_right, y_right)],
        fill=(100, 180, 255)
    )
    
    # Label N S E W
    draw.text((center_x - 8, compass_y - 2), "N", font=font_compass, fill=(60, 60, 60))
    draw.text((center_x - 8, compass_y + compass_size - 20), "S", font=font_compass, fill=(60, 60, 60))
    draw.text((compass_x + compass_size + 5, center_y - 10), "E", font=font_compass, fill=(60, 60, 60))
    draw.text((compass_x - 20, center_y - 10), "W", font=font_compass, fill=(60, 60, 60))
    
    # === PETA MINI dari file lokal ===
    map_width = 250
    map_height = 180
    map_x = 30
    map_y = height - map_height - 30
    
    if os.path.exists(map_path):
        map_img = Image.open(map_path).resize((map_width, map_height))
    else:
        map_img = Image.new('RGB', (map_width, map_height), color=(200, 220, 200))
    
    img.paste(map_img, (map_x, map_y))
    draw.rectangle([map_x-2, map_y-2, map_x+map_width+2, map_y+map_height+2], outline=(255,255,255), width=3)
    
    # === TEKS RATA KANAN di kanan bawah ===
    y_start = height - 350
    y_pos = y_start
    
    y_pos = draw_text_right(draw, y_pos, f"{location_info.get('date','')} {location_info.get('time','')}", font_main, width)
    if 'direction' in location_info:
        y_pos = draw_text_right(draw, y_pos, location_info['direction'], font_main, width)
    
    for key in ['location','district','regency','province','altitude','speed','index']:
        if key in location_info:
            text = f"{location_info[key]}" if key != 'index' else f"Index number: {location_info[key]}"
            y_pos = draw_text_right(draw, y_pos, text, font_secondary, width)
    
    img.save(output_path, quality=95)
    print(f"Gambar berhasil disimpan di {output_path}")

# === Contoh penggunaan ===
if __name__ == "__main__":
    location_data = {
        'date': '2 Okt 2025',
        'time': '10.53.31',
        'direction': '279° W',
        'location': 'SMKN 1 Maja',
        'district': 'Kecamatan Maja',
        'regency': 'Kabupaten Majalengka',
        'province': 'Jawa Barat',
        'altitude': '610.0msnm',
        'speed': '0.7km/h',
        'index': '8',
        'latitude': -6.889678868870827,
        'longitude': 108.30611937791178,
        'compass_angle': 189  # <-- ganti ini untuk arah jarum
    }
    
    input_image = "1.jpeg"  # ganti dengan foto Anda
    output_image = "output_photo.jpg"
    
    if os.path.exists(input_image):
        add_timestamp_location(input_image, output_image, location_data, map_path="map.jpg")
    else:
        print(f"File {input_image} tidak ditemukan!")
