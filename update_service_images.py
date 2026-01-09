#!/usr/bin/env python3
"""
Script to update all service pages with their corresponding images.
This script:
1. Maps image files to service HTML pages
2. Updates the image paths in service pages from .jpg to .webp
3. Updates og:image meta tags
4. Adds images to index.html service cards
"""

import os
import re
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
SERVICES_DIR = BASE_DIR / "services"
IMAGES_DIR = BASE_DIR / "images" / "services"
INDEX_FILE = BASE_DIR / "index.html"

def get_image_files():
    """Get all image files in the services images directory."""
    images = {}
    for img_file in IMAGES_DIR.glob("*.webp"):
        # Create a key from the image filename without extension
        key = img_file.stem
        images[key] = img_file.name
    return images

def normalize_name(name):
    """Normalize a name for matching purposes."""
    # Remove common suffixes and normalize
    name = name.lower()
    name = re.sub(r'-services?$', '', name)
    name = re.sub(r'-installation$', '', name)
    name = re.sub(r'-and-', '-', name)
    name = re.sub(r'-2$', '', name)
    return name

def find_matching_image(html_filename, images):
    """Find the best matching image for a given HTML file."""
    html_stem = Path(html_filename).stem
    
    # Direct match
    if html_stem in images:
        return images[html_stem]
    
    # Try variations
    variations = [
        html_stem,
        html_stem.replace('-and-', '-'),
        re.sub(r'-services?$', '', html_stem),
        re.sub(r'-2$', '', html_stem),
        re.sub(r'-installation-.*$', '-installation', html_stem),
    ]
    
    for var in variations:
        if var in images:
            return images[var]
    
    # Try partial match
    for img_name in images:
        # Check if the main keywords match
        html_parts = set(html_stem.split('-'))
        img_parts = set(img_name.split('-'))
        
        # If most words match
        common = html_parts & img_parts
        if len(common) >= min(len(html_parts), len(img_parts)) - 1 and len(common) >= 2:
            return images[img_name]
    
    return None

def update_service_page(html_file, image_filename):
    """Update a service page with the correct image path."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update the main service image
        # Pattern: <img src="../images/services/something.jpg" or .webp or .png
        img_pattern = r'(<img\s+src=")(\.\./images/services/[^"]+\.(jpg|webp|png))(")'
        new_img_src = f'../images/services/{image_filename}'
        content = re.sub(img_pattern, f'\\1{new_img_src}\\4', content)
        
        # Update og:image meta tag
        og_pattern = r'(<meta\s+property="og:image"\s+content=")[^"]+\.(jpg|webp|png)(")'
        new_og_url = f'https://midwestflipllc.com/images/services/{image_filename}'
        content = re.sub(og_pattern, f'\\1{new_og_url}\\3', content)
        
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {html_file}: {e}")
        return False

def create_image_mapping():
    """Create and print the mapping between HTML files and images."""
    images = get_image_files()
    html_files = list(SERVICES_DIR.glob("*.html"))
    
    mapping = {}
    unmatched_html = []
    matched_images = set()
    
    for html_file in html_files:
        if html_file.name in ['contact-us.html', 'our-services.html', 'service-areas.html']:
            continue
            
        image = find_matching_image(html_file.name, images)
        if image:
            mapping[html_file.name] = image
            matched_images.add(image)
        else:
            unmatched_html.append(html_file.name)
    
    unmatched_images = set(images.values()) - matched_images
    
    return mapping, unmatched_html, unmatched_images

def main():
    print("=" * 60)
    print("Service Page Image Updater")
    print("=" * 60)
    
    # Get mapping
    mapping, unmatched_html, unmatched_images = create_image_mapping()
    
    print(f"\nFound {len(mapping)} matched pairs")
    print(f"Unmatched HTML files: {len(unmatched_html)}")
    print(f"Unmatched images: {len(unmatched_images)}")
    
    # Update service pages
    print("\n" + "-" * 60)
    print("Updating service pages...")
    print("-" * 60)
    
    updated_count = 0
    for html_name, image_name in mapping.items():
        html_path = SERVICES_DIR / html_name
        if update_service_page(html_path, image_name):
            print(f"✓ Updated: {html_name} -> {image_name}")
            updated_count += 1
    
    print(f"\nUpdated {updated_count} files")
    
    # Show unmatched items for manual review
    if unmatched_html:
        print("\n" + "-" * 60)
        print("HTML files without matching images (need manual mapping):")
        print("-" * 60)
        for item in sorted(unmatched_html)[:20]:
            print(f"  - {item}")
        if len(unmatched_html) > 20:
            print(f"  ... and {len(unmatched_html) - 20} more")
    
    if unmatched_images:
        print("\n" + "-" * 60)
        print("Available images without matching HTML:")
        print("-" * 60)
        for item in sorted(unmatched_images)[:20]:
            print(f"  - {item}")
        if len(unmatched_images) > 20:
            print(f"  ... and {len(unmatched_images) - 20} more")
    
    # Generate manual mapping for difficult cases
    print("\n" + "=" * 60)
    print("Generating detailed mapping file...")
    
    with open(BASE_DIR / "image_mapping.txt", "w", encoding="utf-8") as f:
        f.write("Service Page Image Mapping\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("MATCHED:\n")
        for html, img in sorted(mapping.items()):
            f.write(f"{html} -> {img}\n")
        
        f.write(f"\n\nUNMATCHED HTML ({len(unmatched_html)}):\n")
        for item in sorted(unmatched_html):
            f.write(f"  {item}\n")
        
        f.write(f"\n\nUNMATCHED IMAGES ({len(unmatched_images)}):\n")
        for item in sorted(unmatched_images):
            f.write(f"  {item}\n")
    
    print("Saved mapping to image_mapping.txt")
    print("\nDone!")

if __name__ == "__main__":
    main()
