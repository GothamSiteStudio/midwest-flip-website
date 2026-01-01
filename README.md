# Midwest Flip website

Simple single-page marketing site for Midwest Flip LLC (Detroit and Metro Detroit residential builder). Contains static HTML/CSS only; no build step required.

## Files
- index.html – main page markup, copy, and structured data.
- styles.css – styling (dark theme with grid layout).
- images/ – place any images you want to use.
- content.txt – raw notes/keywords and reference material.

## Quick start
1) Open index.html in a browser to view the page.
2) For live reload, use VS Code Live Server or run a simple server (e.g., `python -m http.server 3000`) from this folder and open http://localhost:3000/.

## What to customize first
- Contact info: update phone, email, and hours in the Contact section of index.html. Replace placeholders in the JSON-LD block (business URL, phone, email).
- Quote form: replace the placeholder form action with your real intake method (e.g., form backend, mailto link, or embedded form).
- Services and cities: edit the Services grid and Service area chips in index.html to match what you offer and where.
- Branding: adjust colors, typography, and spacing in styles.css to match your brand.

## SEO and copy notes
- Keep the primary headline and meta description aligned with your actual services and locations (Detroit and Metro Detroit).
- Use the keyword clusters in content.txt to expand sections or create future service pages (kitchen, bathroom, basement, additions, roofing, etc.).
- Maintain consistent business name, phone, and service area across the page and the JSON-LD block to help local SEO.

## Deployment
- Because it is a static site, you can host it on any static host (GitHub Pages, Netlify, Vercel, S3/CloudFront, etc.). Deploy the folder contents as-is.

## Future improvements (optional)
- Add real project photos and before/after shots.
- Add trust signals: licenses, insurance, warranty summary, and real reviews.
- Create dedicated subpages for top services and cities using the keywords in content.txt.
