#!/usr/bin/env python3
"""
Script to update services.html with actual service images.
Replaces image placeholders with real webp images.
"""

import os
import re
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
SERVICES_HTML = BASE_DIR / "services.html"
IMAGES_DIR = BASE_DIR / "images" / "services"

def get_image_files():
    """Get all image files in the services images directory."""
    images = {}
    for img_file in IMAGES_DIR.glob("*.webp"):
        # Create a key from the image filename without extension
        key = img_file.stem.lower()
        images[key] = img_file.name
    return images

def normalize_service_name(name):
    """Convert a service title to a potential image filename."""
    # Convert to lowercase
    name = name.lower()
    # Remove special characters and parentheses
    name = re.sub(r'\([^)]*\)', '', name)
    # Replace spaces and special chars with hyphens
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    # Remove common words that might differ
    name = re.sub(r'^the-', '', name)
    return name

def find_best_image_match(service_title, images):
    """Find the best matching image for a service title."""
    normalized = normalize_service_name(service_title)
    
    # Try direct match
    if normalized in images:
        return images[normalized]
    
    # Try without common suffixes/prefixes
    variations = [
        normalized,
        re.sub(r'-services?$', '', normalized),
        re.sub(r'-installation$', '', normalized),
        re.sub(r'-construction$', '', normalized),
        re.sub(r'-and-', '-', normalized),
        re.sub(r'&', 'and', normalized),
    ]
    
    for var in variations:
        if var in images:
            return images[var]
    
    # Try finding by main keywords
    words = set(normalized.split('-'))
    words.discard('and')
    words.discard('the')
    words.discard('for')
    words.discard('with')
    words.discard('amp')
    
    best_match = None
    best_score = 0
    
    for img_key, img_name in images.items():
        img_words = set(img_key.split('-'))
        common = words & img_words
        
        # Score based on common words
        if len(common) >= 2:
            score = len(common) / max(len(words), len(img_words))
            if score > best_score:
                best_score = score
                best_match = img_name
    
    if best_score >= 0.5:
        return best_match
    
    return None

def update_services_html():
    """Update services.html with actual images."""
    images = get_image_files()
    
    with open(SERVICES_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match service cards with image placeholders
    # <article class="svc-card" role="listitem">
    #   <div class="svc-info">
    #     <h4>Service Name</h4>
    #     <p>Description</p>
    #   </div>
    #   <div class="svc-photo" role="img" aria-label="...">Image placeholder</div>
    # </article>
    
    pattern = r'(<div class="svc-info">\s*<h4>)([^<]+)(</h4>.*?<div class="svc-photo" role="img" aria-label="[^"]*">)Image placeholder(</div>)'
    
    def replace_placeholder(match):
        prefix = match.group(1)
        service_title = match.group(2)
        middle = match.group(3)
        suffix = match.group(4)
        
        image = find_best_image_match(service_title, images)
        
        if image:
            # Replace with actual image
            img_tag = f'<img src="images/services/{image}" alt="{service_title}" loading="lazy" width="300" height="200">'
            return f'{prefix}{service_title}{middle}{img_tag}{suffix}'
        else:
            # Keep placeholder but log it
            print(f"No image found for: {service_title}")
            return match.group(0)
    
    updated_content = re.sub(pattern, replace_placeholder, content, flags=re.DOTALL)
    
    # Count changes
    original_placeholders = content.count('Image placeholder</div>')
    remaining_placeholders = updated_content.count('Image placeholder</div>')
    updated_count = original_placeholders - remaining_placeholders
    
    with open(SERVICES_HTML, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n{'='*60}")
    print(f"Updated {updated_count} service images")
    print(f"Remaining placeholders: {remaining_placeholders}")
    print(f"{'='*60}")

if __name__ == "__main__":
    update_services_html()
