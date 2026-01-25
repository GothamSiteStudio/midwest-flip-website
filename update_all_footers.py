#!/usr/bin/env python3
"""
Script to update all HTML files with a consistent footer from index.html.
Adjusts relative paths based on directory depth.
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# The canonical footer from index.html (will be loaded)
FOOTER_TEMPLATE = None

def get_footer_from_index():
    """Extract footer from index.html"""
    index_path = BASE_DIR / "index.html"
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract footer section
    match = re.search(r'(<footer class="footer".*?</footer>)', content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def get_relative_prefix(file_path):
    """Calculate the relative path prefix based on file depth"""
    rel_path = file_path.relative_to(BASE_DIR)
    depth = len(rel_path.parts) - 1  # -1 for the file itself
    
    if depth == 0:
        return ""
    else:
        return "../" * depth

def adjust_paths(footer_html, prefix):
    """Adjust paths in footer HTML based on directory depth"""
    if not prefix:
        return footer_html
    
    adjusted = footer_html
    
    # Adjust image paths
    adjusted = re.sub(r'src="images/', f'src="{prefix}images/', adjusted)
    adjusted = re.sub(r"src='images/", f"src='{prefix}images/", adjusted)
    
    # Adjust href paths for internal pages (not starting with http, #, tel:, mailto:)
    # Handle services.html, index.html, etc.
    adjusted = re.sub(r'href="((?!http|#|tel:|mailto:|javascript:)[a-zA-Z0-9_-]+\.html)', f'href="{prefix}\\1', adjusted)
    adjusted = re.sub(r"href='((?!http|#|tel:|mailto:|javascript:)[a-zA-Z0-9_-]+\.html)", f"href='{prefix}\\1", adjusted)
    
    # Adjust anchor links that reference index.html sections
    adjusted = re.sub(r'href="#contact"', f'href="{prefix}index.html#contact"', adjusted)
    adjusted = re.sub(r'href="#process"', f'href="{prefix}index.html#process"', adjusted)
    adjusted = re.sub(r'href="#areas"', f'href="{prefix}index.html#areas"', adjusted)
    adjusted = re.sub(r'href="#reviews"', f'href="{prefix}index.html#reviews"', adjusted)
    
    return adjusted

def update_file_footer(file_path, new_footer):
    """Update the footer in a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has a footer
        if '<footer' not in content.lower():
            return False, "No footer found"
        
        # Calculate prefix for this file
        prefix = get_relative_prefix(file_path)
        adjusted_footer = adjust_paths(new_footer, prefix)
        
        # Replace footer (match from <footer to </footer>)
        new_content = re.sub(
            r'<footer[^>]*class="footer"[^>]*>.*?</footer>',
            adjusted_footer,
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # If no match with class="footer", try any footer
        if new_content == content:
            new_content = re.sub(
                r'<footer[^>]*>.*?</footer>',
                adjusted_footer,
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Updated"
        else:
            return False, "No changes made"
            
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Footer Update Script for Midwest Flip Website")
    print("=" * 60)
    
    # Get the canonical footer
    footer = get_footer_from_index()
    if not footer:
        print("ERROR: Could not extract footer from index.html")
        return
    
    print(f"\n✓ Extracted footer from index.html ({len(footer)} characters)")
    
    # Find all HTML files
    html_files = list(BASE_DIR.rglob("*.html"))
    print(f"✓ Found {len(html_files)} HTML files\n")
    
    # Skip index.html since it's the source
    html_files = [f for f in html_files if f.name != "index.html"]
    
    # Process files
    updated = 0
    skipped = 0
    errors = 0
    
    for file_path in html_files:
        rel_path = file_path.relative_to(BASE_DIR)
        success, message = update_file_footer(file_path, footer)
        
        if success:
            updated += 1
            print(f"✓ {rel_path}")
        elif "No footer" in message:
            skipped += 1
            print(f"⊘ {rel_path} - {message}")
        else:
            errors += 1
            print(f"✗ {rel_path} - {message}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(html_files)}")
    print(f"✓ Updated: {updated}")
    print(f"⊘ Skipped (no footer): {skipped}")
    print(f"✗ Errors: {errors}")
    print("=" * 60)

if __name__ == "__main__":
    main()
