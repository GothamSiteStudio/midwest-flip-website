#!/usr/bin/env python3
"""
Update all service area page footers to match the main site footer.
"""

import os
import re

# New footer HTML that matches main site
NEW_FOOTER = '''  <!-- Footer -->
  <footer class="footer" role="contentinfo">
    <div class="wrap">
      <div class="footer-main">
        <!-- Company Info -->
        <div class="footer-col footer-about">
          <img class="footer-logo" src="../images/logo.svg" alt="Midwest Flip LLC Logo" width="50" height="50">
          <h3>Midwest Flip LLC</h3>
          <p>Licensed Michigan Residential Builder serving Detroit and Metro Detroit since 2019. Over 400 completed projects with a commitment to quality craftsmanship.</p>
          <div class="footer-badges">
            <span class="footer-badge">Licensed</span>
            <span class="footer-badge">Insured</span>
            <span class="footer-badge">5-Year Warranty</span>
          </div>
        </div>

        <!-- Services Links -->
        <div class="footer-col">
          <h4>Our Services</h4>
          <ul class="footer-links">
            <li><a href="../services.html#remodeling">Kitchen Remodeling</a></li>
            <li><a href="../services.html#remodeling">Bathroom Remodeling</a></li>
            <li><a href="../services.html#remodeling">Basement Finishing</a></li>
            <li><a href="../services.html#remodeling">Home Additions</a></li>
            <li><a href="../services.html#exterior">Roofing & Siding</a></li>
            <li><a href="../services.html#remodeling">Whole Home Renovation</a></li>
          </ul>
        </div>

        <!-- Service Areas -->
        <div class="footer-col">
          <h4>Service Areas</h4>
          <ul class="footer-links footer-area-links">
            <li><a href="../service-areas.html"><strong>Oakland County</strong>: Southfield, Farmington Hills, Novi, Troy, Royal Oak, Birmingham, Bloomfield Hills, West Bloomfield, Oak Park, Pontiac, Auburn Hills, Clarkston, Waterford</a></li>
            <li><a href="../service-areas.html"><strong>Wayne County</strong>: Detroit, Dearborn, Livonia, Canton, Westland, Taylor, Dearborn Heights, Allen Park, Lincoln Park, Wyandotte, Garden City, Inkster</a></li>
            <li><a href="../service-areas.html"><strong>Macomb County</strong>: Warren, Sterling Heights, Clinton Township, Shelby Township, Macomb Township, Chesterfield Township, Roseville, Eastpointe, St. Clair Shores, Fraser, Harrison Township, Mount Clemens</a></li>
          </ul>
        </div>

        <!-- Contact Info -->
        <div class="footer-col footer-contact">
          <h4>Contact Us</h4>
          <ul class="footer-contact-list">
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
              <a href="tel:+13133896324">(313) 389-6324</a>
            </li>
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
              <a href="mailto:midwestflipllc@gmail.com">midwestflipllc@gmail.com</a>
            </li>
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              <span>Sun-Thu 9:00 AM–5:00 PM · Fri 9:00 AM–12:00 PM · Sat Closed</span>
            </li>
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
              <span>Detroit & Metro Detroit, MI</span>
            </li>
          </ul>
          <a href="../index.html#contact" class="btn footer-cta">Get a Quote</a>
          
          <!-- Google Map -->
          <div class="footer-map">
            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d773397.2248756414!2d-83.24613095!3d42.67748945!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8254ccd6e5da9aef%3A0xac79689355ebab12!2sMidwest%20Flip!5e1!3m2!1sen!2sus!4v1767715579769!5m2!1sen!2sus" width="100%" height="200" style="border:0; border-radius: 12px; margin-top: 16px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Midwest Flip LLC location on Google Maps - Detroit Metro Area"></iframe>
          </div>
        </div>
      </div>

      <!-- Footer Bottom -->
      <div class="footer-bottom">
        <div class="footer-bottom-left">
          <p>&copy; <span id="year"></span> Midwest Flip LLC. All Rights Reserved.</p>
          <p class="footer-license">Michigan Residential Builder License</p>
        </div>
        <div class="footer-bottom-right">
          <nav class="footer-bottom-nav" aria-label="Footer navigation">
            <a href="../services.html">Services</a>
            <a href="../index.html#process">Process</a>
            <a href="../service-areas.html">Areas</a>
            <a href="../index.html#reviews">Reviews</a>
            <a href="../index.html#contact">Contact</a>
          </nav>
        </div>
      </div>

      <!-- Watermark -->
      <div class="footer-watermark">
        <p>Website designed & developed by <a href="https://gothamsitestudio.com/" target="_blank" rel="noopener noreferrer">Gotham Site Studio</a></p>
      </div>
    </div>
  </footer>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
  </script>
  <script src="../scripts.js" defer></script>
</body>
</html>'''

def update_footer(file_path):
    """Update footer in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the old footer (from <!-- Footer --> to </html>)
    pattern = r'  <!-- Footer -->.*?</html>'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, NEW_FOOTER, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    service_areas_dir = 'service-areas'
    
    if not os.path.exists(service_areas_dir):
        print(f"❌ Directory '{service_areas_dir}' not found!")
        return
    
    html_files = [f for f in os.listdir(service_areas_dir) if f.endswith('.html')]
    
    print(f"🔄 Updating footers on {len(html_files)} service area pages...")
    
    updated = 0
    failed = 0
    
    for filename in html_files:
        file_path = os.path.join(service_areas_dir, filename)
        try:
            if update_footer(file_path):
                updated += 1
                if updated % 50 == 0:
                    print(f"  Progress: {updated}/{len(html_files)}...")
            else:
                print(f"  ⚠️  Could not find footer pattern in: {filename}")
                failed += 1
        except Exception as e:
            print(f"  ❌ Error updating {filename}: {e}")
            failed += 1
    
    print(f"\n✅ Successfully updated {updated} pages")
    if failed > 0:
        print(f"⚠️  Failed to update {failed} pages")

if __name__ == '__main__':
    main()
