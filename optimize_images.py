"""
Script to optimize images for better PageSpeed performance.
- Compresses hero.webp significantly
- Resizes service images to their display dimensions (400x250)
"""

from PIL import Image
import os
import shutil

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images_autoedited")
SERVICES_DIR = os.path.join(IMAGES_DIR, "services")

def backup_file(filepath):
    """Create a backup of the original file"""
    backup_path = filepath + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"  Backup created: {backup_path}")

def get_file_size_kb(filepath):
    """Get file size in KB"""
    return os.path.getsize(filepath) / 1024

def optimize_hero_image():
    """Optimize the hero image with better compression"""
    hero_path = os.path.join(IMAGES_DIR, "hero.webp")
    
    if not os.path.exists(hero_path):
        print(f"Hero image not found: {hero_path}")
        return
    
    original_size = get_file_size_kb(hero_path)
    print(f"\n=== Optimizing Hero Image ===")
    print(f"  Original size: {original_size:.2f} KB")
    
    # Backup original
    backup_file(hero_path)
    
    # Open and get dimensions
    with Image.open(hero_path) as img:
        original_dims = img.size
        print(f"  Original dimensions: {original_dims[0]}x{original_dims[1]}")
        
        # For hero images, we typically want max width of 1920px for full HD
        # and good compression for web
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
            print(f"  Resized to: {max_width}x{new_height}")
        
        # Convert to RGB if necessary (remove alpha channel for better compression)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Save with aggressive compression (quality 60-70 is usually good for web)
        img.save(hero_path, 'WEBP', quality=65, method=6)
    
    new_size = get_file_size_kb(hero_path)
    savings = original_size - new_size
    print(f"  New size: {new_size:.2f} KB")
    print(f"  Savings: {savings:.2f} KB ({(savings/original_size)*100:.1f}%)")

def optimize_service_images():
    """Resize service images to display dimensions (400x250)"""
    print(f"\n=== Optimizing Service Images ===")
    
    # Target dimensions matching the HTML display size
    target_width = 400
    target_height = 250
    
    # List of service images to optimize
    service_images = [
        "framing-structural-carpentry.webp",
        "roof-replacement.webp"
    ]
    
    # Also optimize all other service images if they exist
    if os.path.exists(SERVICES_DIR):
        for filename in os.listdir(SERVICES_DIR):
            if filename.endswith('.webp') and filename not in service_images:
                service_images.append(filename)
    
    total_savings = 0
    
    for filename in service_images:
        filepath = os.path.join(SERVICES_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"  Skipping (not found): {filename}")
            continue
        
        original_size = get_file_size_kb(filepath)
        
        with Image.open(filepath) as img:
            original_dims = img.size
            
            # Only process if image is larger than target
            if img.width > target_width or img.height > target_height:
                print(f"\n  Processing: {filename}")
                print(f"    Original: {original_dims[0]}x{original_dims[1]} ({original_size:.2f} KB)")
                
                # Backup original
                backup_file(filepath)
                
                # Calculate aspect ratio preserving resize, then crop to exact dimensions
                # First resize to cover the target dimensions
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    # Image is wider, fit to height and crop width
                    new_height = target_height
                    new_width = int(new_height * img_ratio)
                else:
                    # Image is taller, fit to width and crop height
                    new_width = target_width
                    new_height = int(new_width / img_ratio)
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Center crop to exact target dimensions
                left = (new_width - target_width) // 2
                top = (new_height - target_height) // 2
                img = img.crop((left, top, left + target_width, top + target_height))
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save with good quality compression
                img.save(filepath, 'WEBP', quality=80, method=6)
                
                new_size = get_file_size_kb(filepath)
                savings = original_size - new_size
                total_savings += savings
                print(f"    New: {target_width}x{target_height} ({new_size:.2f} KB)")
                print(f"    Savings: {savings:.2f} KB ({(savings/original_size)*100:.1f}%)")
    
    print(f"\n  Total service images savings: {total_savings:.2f} KB")

def main():
    print("=" * 50)
    print("Image Optimization for PageSpeed Insights")
    print("=" * 50)
    
    optimize_hero_image()
    optimize_service_images()
    
    print("\n" + "=" * 50)
    print("Optimization complete!")
    print("Backup files created with .backup extension")
    print("=" * 50)

if __name__ == "__main__":
    main()
