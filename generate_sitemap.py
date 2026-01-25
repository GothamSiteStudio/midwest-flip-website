#!/usr/bin/env python3
"""
Script to generate an updated sitemap.xml for the Midwest Flip website.
Includes all HTML files with proper priorities and dates.
"""

import os
from pathlib import Path
from datetime import datetime

# Base directory and domain
BASE_DIR = Path(__file__).parent
DOMAIN = "https://midwestflipllc.com"

# Today's date
TODAY = datetime.now().strftime("%Y-%m-%d")

# Priority mapping based on page type/depth
def get_priority(rel_path):
    """Determine priority based on page location"""
    path_str = str(rel_path).replace("\\", "/").lower()
    
    # Homepage - highest priority
    if path_str == "index.html":
        return "1.0"
    
    # Main pages - very high priority
    if path_str in ["services.html", "service-areas.html", "blog.html"]:
        return "0.9"
    
    # Skip internal/utility pages
    if "receipt" in path_str:
        return None  # Don't include
    
    # Service area pages - high priority
    if path_str.startswith("service-areas/"):
        return "0.7"
    
    # Individual service pages - high priority
    if path_str.startswith("services/"):
        # Key services get higher priority
        key_services = [
            "kitchen-remodeling", "bathroom-remodeling", "basement-finishing",
            "new-home-construction", "custom-home-building", "room-additions",
            "roofing", "siding", "deck-construction", "foundation-repair",
            "whole-home-renovation"
        ]
        for key in key_services:
            if key in path_str:
                return "0.8"
        return "0.7"
    
    # Blog posts
    if path_str.startswith("blog/"):
        return "0.6"
    
    # Default
    return "0.5"

def get_changefreq(rel_path):
    """Determine change frequency based on page type"""
    path_str = str(rel_path).lower()
    
    if path_str == "index.html":
        return "weekly"
    if path_str in ["services.html", "service-areas.html"]:
        return "weekly"
    if path_str.startswith("blog"):
        return "monthly"
    return "monthly"

def generate_sitemap():
    """Generate sitemap XML content"""
    
    # Find all HTML files
    html_files = list(BASE_DIR.rglob("*.html"))
    
    # Filter and sort
    urls = []
    for file_path in html_files:
        rel_path = file_path.relative_to(BASE_DIR)
        path_str = str(rel_path).replace("\\", "/")
        
        # Skip utility files
        if any(skip in path_str.lower() for skip in ["receipt", "test", "backup"]):
            continue
        
        priority = get_priority(rel_path)
        if priority is None:
            continue
            
        changefreq = get_changefreq(rel_path)
        
        # Build URL
        if path_str == "index.html":
            url = f"{DOMAIN}/"
        else:
            url = f"{DOMAIN}/{path_str}"
        
        urls.append({
            "loc": url,
            "lastmod": TODAY,
            "changefreq": changefreq,
            "priority": priority
        })
    
    # Sort URLs: homepage first, then by priority, then alphabetically
    urls.sort(key=lambda x: (-float(x["priority"]), x["loc"]))
    
    # Generate XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    for url_data in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url_data['loc']}</loc>")
        xml_lines.append(f"    <lastmod>{url_data['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{url_data['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{url_data['priority']}</priority>")
        xml_lines.append("  </url>")
    
    xml_lines.append("</urlset>")
    
    return "\n".join(xml_lines), len(urls)

def main():
    print("=" * 60)
    print("Sitemap Generator for Midwest Flip Website")
    print("=" * 60)
    
    # Generate sitemap
    xml_content, url_count = generate_sitemap()
    
    # Write to file
    sitemap_path = BASE_DIR / "sitemap.xml"
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"\n✓ Generated sitemap with {url_count} URLs")
    print(f"✓ Saved to: {sitemap_path}")
    print("=" * 60)
    
    # Show breakdown
    print("\nURL Breakdown:")
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    homepage = content.count('priority>1.0<')
    high_priority = content.count('priority>0.9<')
    medium_high = content.count('priority>0.8<')
    medium = content.count('priority>0.7<')
    low = content.count('priority>0.6<') + content.count('priority>0.5<')
    
    print(f"  Homepage (1.0):      {homepage}")
    print(f"  Main pages (0.9):    {high_priority}")
    print(f"  Key services (0.8):  {medium_high}")
    print(f"  Other pages (0.7):   {medium}")
    print(f"  Blog/other (0.5-0.6): {low}")
    print("=" * 60)

if __name__ == "__main__":
    main()
