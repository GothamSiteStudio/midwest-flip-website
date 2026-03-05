# Midwest Flip LLC Website

![Midwest Flip LLC](images/logo.png)

Official website for Midwest Flip LLC, a licensed Michigan residential builder serving Detroit and Metro Detroit.

## Live URLs

- Production domain: https://midwestflipllc.com/
- GitHub Pages fallback: https://gothamssitestudio.github.io/midwest-flip-website/

## Hosting and Deployment

This project is hosted on GitHub Pages.

- Deployment workflow: `.github/workflows/deploy-pages.yml`
- Trigger: push to `main` or manual workflow dispatch
- Custom domain: `CNAME` file (`midwestflipllc.com`)
- Jekyll disabled: `.nojekyll`

Legacy hosting configuration has been removed from this repository.

## Trust and Privacy Pages

- Privacy Policy: `privacy-policy.html`
- Terms of Service: `terms-of-service.html`

Analytics are loaded only after user consent via `scripts/privacy-consent.js`.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/GothamSiteStudio/midwest-flip-website.git
   ```
2. Open `index.html` directly, or run a local server:
   ```bash
   python -m http.server 3000
   ```
3. Visit `http://localhost:3000`.

## Contact

- Phone: (313) 389-6324
- Email: midwestflipllc@gmail.com

## License

© 2026 Midwest Flip LLC. All rights reserved.
