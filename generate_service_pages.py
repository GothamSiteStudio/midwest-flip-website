import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

# Simple HTML generator for service pages based on a JSON data file.
# Usage examples:
#   python generate_service_pages.py --data services_data.json
#   python generate_service_pages.py --data services_data.json --slug bathroom-remodeling

SITE_BASE_URL = "https://midwestflipllc.com"
PHONE_DISPLAY = "(313) 389-6324"
PHONE_TEL = "+13133896324"
EMAIL = "midwestflipllc@gmail.com"
BUSINESS_NAME = "Midwest Flip LLC"
LOGO_URL = f"{SITE_BASE_URL}/images/logo.png"
DEFAULT_OPENING_HOURS = "Mo-Th 09:00-17:00"

# SEO length targets (used for generated pages)
TITLE_MIN_LEN = 30
TITLE_MAX_LEN = 60
META_DESC_MIN_LEN = 70
META_DESC_MAX_LEN = 160


def _normalize_space(text: str) -> str:
  return " ".join((text or "").split()).strip()


def _trim_to_word_boundary(text: str, max_len: int) -> str:
  text = _normalize_space(text)
  if len(text) <= max_len:
    return text
  cut = text.rfind(" ", 0, max_len + 1)
  if cut <= 0:
    return text[:max_len].strip()
  return text[:cut].strip()


def _extend_description(text: str, min_len: int, max_len: int) -> str:
  text = _normalize_space(text)
  if len(text) >= min_len:
    return _trim_to_word_boundary(text, max_len)
  suffixes = [
    "Serving Detroit & Metro Detroit.",
    f"Call {PHONE_DISPLAY}.",
  ]
  for suffix in suffixes:
    candidate = _normalize_space((text + " " + suffix).strip()) if text else suffix
    if len(candidate) <= max_len:
      text = candidate
    if len(text) >= min_len:
      break
  return _trim_to_word_boundary(text, max_len)


def _clamp_title(meta_title: str) -> str:
  meta_title = _normalize_space(meta_title)
  if len(meta_title) > TITLE_MAX_LEN:
    meta_title = _trim_to_word_boundary(meta_title, TITLE_MAX_LEN)
  if len(meta_title) < TITLE_MIN_LEN:
    # Keep it simple: ensure the brand appears.
    if BUSINESS_NAME.lower() not in meta_title.lower():
      candidate = _normalize_space(f"{meta_title} | {BUSINESS_NAME}") if meta_title else BUSINESS_NAME
      meta_title = _trim_to_word_boundary(candidate, TITLE_MAX_LEN)
  return meta_title


def _clamp_meta_description(meta_description: str) -> str:
  meta_description = _normalize_space(meta_description)
  if len(meta_description) > META_DESC_MAX_LEN:
    meta_description = _trim_to_word_boundary(meta_description, META_DESC_MAX_LEN)
  if len(meta_description) < META_DESC_MIN_LEN:
    meta_description = _extend_description(meta_description, META_DESC_MIN_LEN, META_DESC_MAX_LEN)
  return meta_description


def render_list(items: List[str], cls: str = "") -> str:
    if not items:
        return ""
    class_attr = f' class="{cls}"' if cls else ""
    li_html = "\n".join(f"<li>{item}</li>" for item in items)
    return f"<ul{class_attr}>\n{li_html}\n</ul>"


def render_cards(items: List[Dict[str, str]], wrapper_class: str) -> str:
    if not items:
        return ""
    cards = []
    for item in items:
        title = item.get("title", "").strip()
        description = item.get("description", "").strip()
        cards.append(
            f"<div class=\"{wrapper_class}\">\n"
            f"  <h3>{title}</h3>\n"
            f"  <p>{description}</p>\n"
            f"</div>"
        )
    return "\n\n".join(cards)


def render_process(steps: List[Dict[str, str]]) -> str:
    if not steps:
        return ""
    items = []
    for step in steps:
        title = step.get("title", "").strip()
        description = step.get("description", "").strip()
        items.append(
            "  <li>\n"
            f"    <strong>{title}</strong>\n"
            f"    <p>{description}</p>\n"
            "  </li>"
        )
    return "<ol class=\"process-steps\">\n" + "\n".join(items) + "\n</ol>"


def render_pricing(table: Dict[str, Any]) -> str:
    if not table:
        return ""
    rows = table.get("rows", [])
    note = table.get("note", "")
    if not rows:
        return ""
    rows_html = "\n".join(
        f"                <tr><td>{row.get('label','')}</td><td>{row.get('value','')}</td></tr>"
        for row in rows
    )
    note_html = f"<p class=\"muted\">{note}</p>" if note else ""
    return (
        "<table class=\"pricing-table\">\n"
        "  <thead>\n    <tr><th>Project Type</th><th>Typical Cost Range</th></tr>\n  </thead>\n"
        "  <tbody>\n" + rows_html + "\n  </tbody>\n</table>\n" + note_html
    )


def render_faq_details(faqs: List[Dict[str, str]]) -> str:
    if not faqs:
        return ""
    items = []
    for faq in faqs:
        q = faq.get("q", "").strip()
        a = faq.get("a", "").strip()
        items.append(
            "  <details class=\"faq-item\">\n"
            f"    <summary>{q}</summary>\n"
            f"    <p>{a}</p>\n"
            "  </details>"
        )
    return "<div class=\"faq-list\">\n" + "\n\n".join(items) + "\n</div>"


def render_schema_service(service: Dict[str, Any]) -> str:
  city = service.get("city", "").strip()
  state = service.get("state", "").strip()

  area_list = service.get("service_areas", [])
  area_json = [
    {
      "@type": "City",
      "name": area_city,
      "containedInPlace": {"@type": "State", "name": state or "Michigan"},
    }
    for area_city in area_list
  ]

  service_name = service.get("service_name", "Service").strip()
  location_suffix = f" in {city}, {state}" if city else ""
  schema_name = f"{service_name} Services{location_suffix}".rstrip(", ")

  address: Dict[str, str] = {"@type": "PostalAddress", "addressCountry": "US"}
  if city:
    address["addressLocality"] = city
  if state:
    address["addressRegion"] = state

  schema = {
    "@context": "https://schema.org",
    "@type": "Service",
    "serviceType": service.get("service_type", service_name),
    "name": schema_name,
    "description": service.get("meta_description", ""),
    "provider": {
      "@type": "LocalBusiness",
      "name": BUSINESS_NAME,
      "image": LOGO_URL,
      "telephone": f"+1-{PHONE_DISPLAY}".replace("(", "").replace(")", "").replace(" ", "-"),
      "email": EMAIL,
      "address": address,
      "priceRange": "$$",
      "openingHours": service.get("opening_hours", DEFAULT_OPENING_HOURS),
    },
    "areaServed": area_json,
  }
  return json.dumps(schema, ensure_ascii=True, indent=2)


def render_schema_faq(faqs: List[Dict[str, str]]) -> str:
    if not faqs:
        return ""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.get("q", ""),
                "acceptedAnswer": {"@type": "Answer", "text": faq.get("a", "")},
            }
            for faq in faqs
        ],
    }
    return json.dumps(schema, ensure_ascii=True, indent=2)


def render_breadcrumb(slug: str, title: str) -> str:
    return (
        "    <nav class=\"breadcrumb\" aria-label=\"Breadcrumb\">\n"
        "      <div class=\"wrap\">\n"
        "        <ol>\n"
        "          <li><a href=\"../index.html\">Home</a></li>\n"
        "          <li><a href=\"../services.html\">Services</a></li>\n"
        f"          <li aria-current=\"page\">{title}</li>\n"
        "        </ol>\n"
        "      </div>\n"
        "    </nav>\n"
    )


def render_page(service: Dict[str, Any]) -> str:
    slug = service["slug"].strip()
  meta_title = service.get("meta_title", service.get("hero_h1", service.get("service_name", "Service")))
  meta_description = service.get("meta_description", "")

  meta_title = _clamp_title(str(meta_title))
  meta_description = _clamp_meta_description(str(meta_description))
    og_description = service.get("og_description", meta_description)
    keywords = service.get("keywords", "")
    canonical = f"{SITE_BASE_URL}/services/{slug}.html"
    og_image = service.get("og_image", f"{SITE_BASE_URL}/images/services/{service.get('service_image', slug + '.jpg')}")
    hero_badges = service.get("hero_badges", [])

    intro_paragraphs = service.get("intro_paragraphs", [])
    intro_html = "\n\n".join(f"<p>{p}</p>" for p in intro_paragraphs)

    services_offered_html = render_cards(service.get("services_offered", []), "service-item")
    benefits_html = render_cards(service.get("benefits", []), "benefit")
    process_html = render_process(service.get("process_steps", []))
    pricing_html = render_pricing(service.get("pricing_table", {}))
    faq_details_html = render_faq_details(service.get("faqs", []))

    schema_service = render_schema_service(service)
    schema_faq = render_schema_faq(service.get("faqs", []))

    related_services = service.get("related_services", [])
    related_links = "\n".join(
        f"                <li><a href=\"{rel}.html\">{rel.replace('-', ' ').title()}</a></li>" for rel in related_services
    )

    area_tags = "\n".join(f"                <li>{area}</li>" for area in service.get("service_areas", []))
    footer_area_links = "\n".join(
      f"          <li><a href=\"../service-areas.html\">{area}</a></li>"
      for area in service.get("service_areas", [])[:3]
    )

    hero_badges_html = "\n".join(f"          <span class=\"badge\">✓ {badge}</span>" for badge in hero_badges)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{meta_title}</title>
  <meta name=\"description\" content=\"{meta_description}\">
  <meta name=\"keywords\" content=\"{keywords}\">
  <meta name=\"robots\" content=\"index, follow\">
  <meta name=\"author\" content=\"{BUSINESS_NAME}\">
  <link rel=\"canonical\" href=\"{canonical}\">

  <!-- Open Graph -->
  <meta property=\"og:title\" content=\"{meta_title}\">
  <meta property=\"og:description\" content=\"{og_description}\">
  <meta property=\"og:type\" content=\"website\">
  <meta property=\"og:url\" content=\"{canonical}\">
  <meta property=\"og:image\" content=\"{og_image}\">
  <meta property=\"og:locale\" content=\"en_US\">

  <!-- Twitter Card -->
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <meta name=\"twitter:title\" content=\"{meta_title}\">
  <meta name=\"twitter:description\" content=\"{og_description}\">

  <link rel=\"icon\" href=\"../images/logo.png\" type=\"image/png\">
  <link rel=\"stylesheet\" href=\"../styles.css\">

  <!-- Service Schema -->
  <script type=\"application/ld+json\">
{schema_service}
  </script>

  <!-- FAQ Schema -->
  <script type=\"application/ld+json\">
{schema_faq}
  </script>

  <!-- Breadcrumb Schema -->
  <script type=\"application/ld+json\">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE_BASE_URL}/"}},
      {{"@type": "ListItem", "position": 2, "name": "Services", "item": "{SITE_BASE_URL}/services.html"}},
      {{"@type": "ListItem", "position": 3, "name": "{service.get('hero_h1', service.get('service_name',''))}", "item": "{canonical}"}}
    ]
  }}
  </script>
</head>
<body>
  <a class=\"skip-link\" href=\"#main-content\">Skip to main content</a>

  <div class="top-bar">
    <div class="wrap top-bar-content">
      <div class="top-bar-left">
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></span>
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg> <a href="mailto:{EMAIL}">{EMAIL}</a></span>
      </div>
      <div class="top-bar-right">
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Mon-Thu 9am-5pm</span>
        <span class="top-bar-badge">Licensed &amp; Insured</span>
      </div>
    </div>
  </div>

  <header class=\"top\" role=\"banner\">
    <div class=\"wrap\">
      <a href=\"../index.html\" class=\"brand\" aria-label=\"{BUSINESS_NAME} - Home\">
          <img class=\"logo_img\" src=\"../images/logo.svg\" alt=\"{BUSINESS_NAME} - Licensed Residential Builder\" width=\"120\" height=\"120\">
        <div>
          <div class=\"name\">{BUSINESS_NAME}</div>
          <div class=\"tag\">Licensed Residential Builder</div>
        </div>
      </a>
    <!-- Matomo -->
    <script>
      var _paq = window._paq = window._paq || [];
      /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
      _paq.push(['trackPageView']);
      _paq.push(['enableLinkTracking']);
      (function() {{
        var u="https://alphalockandsafe.matomo.cloud/";
        _paq.push(['setTrackerUrl', u+'matomo.php']);
        _paq.push(['setSiteId', '2']);
        var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
        g.async=true; g.src='https://cdn.matomo.cloud/alphalockandsafe.matomo.cloud/matomo.js'; s.parentNode.insertBefore(g,s);
      }})();
    </script>
    <!-- End Matomo Code -->

      <nav class=\"nav\" id=\"site-nav\" role=\"navigation\" aria-label=\"Main navigation\">
        <a href=\"../services.html\" aria-label=\"Services\">Services</a>
        <a href=\"../service-areas.html\" aria-label=\"Service Areas\">Service Areas</a>
        <a href=\"../index.html#process\" aria-label=\"Our Process\">Process</a>
        <a href=\"../blog.html\" aria-label=\"Our Blog\">Blog</a>
        <a href=\"../index.html#faq\" aria-label=\"Frequently Asked Questions\">FAQ</a>
        <a href=\"tel:{PHONE_TEL}\" class=\"btn ghost\" aria-label=\"Call us at {PHONE_DISPLAY}\"><svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" style=\"margin-right:6px;vertical-align:middle;\"><path d=\"M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z\"></path></svg>{PHONE_DISPLAY}</a>
        <a href=\"../index.html#contact\" class=\"btn\" aria-label=\"Get a Quote\">Get a Quote</a>
      </nav>

      <button class=\"mobile-menu-toggle\" aria-label=\"Toggle mobile menu\" aria-controls=\"site-nav\" aria-expanded=\"false\">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
  </header>

  <main id=\"main-content\">
{render_breadcrumb(slug, service.get('hero_h1', service.get('service_name','')))}

    <section class=\"hero service-page-hero\">
      <div class=\"wrap\">
        <h1>{service.get('hero_h1', '')}</h1>
        <p class=\"lead\">{service.get('hero_lead', '')}</p>
        <div class=\"cta_row\">
          <a class=\"btn\" href=\"../index.html#contact\">{service.get('cta_primary_label', 'Get a Quote')}</a>
          <a class=\"btn ghost\" href=\"tel:{PHONE_TEL}\">{service.get('cta_secondary_label', f'Call {PHONE_DISPLAY}')}</a>
        </div>
        <div class=\"trust-badges\">
{hero_badges_html}
        </div>
      </div>
    </section>

    <section class=\"section service-content\">
      <div class=\"wrap\">
        <div class=\"content-grid\">
          <div class=\"main-content\">
            <h2>{service.get('h2_intro', f"Professional {service.get('service_name','')}")}</h2>
{intro_html}

            <div class=\"service-image\">
              <img src="../images/services/{service.get('service_image', slug + '.jpg')}" alt="{service.get('service_image_alt', service.get('service_name',''))} project by {BUSINESS_NAME}" width="800" height="500" loading="lazy">
              <p class="caption">{service.get('service_image_caption', f"A recent {service.get('service_name','').lower()} project")}</p>
            </div>

            <h2>{service.get('h2_services', f"Our {service.get('service_name','')} Services")}</h2>
            <p>{service.get('services_intro', '')}</p>

            <div class=\"services-list\">
{services_offered_html}
            </div>

            <h2>{service.get('h2_benefits', 'Why Choose Us')}</h2>
            <div class=\"benefits-list\">
{benefits_html}
            </div>

            <h2>{service.get('h2_process', f"Our {service.get('service_name','')} Process")}</h2>
            <p>{service.get('process_intro', '')}</p>
{process_html}

{(('<h2>' + service.get('h2_pricing','Pricing Overview') + '</h2>\n' + pricing_html) if pricing_html else '')}

          </div>

          <aside class=\"sidebar\">
            <div class=\"sidebar-cta\">
              <h3>{service.get('sidebar_title', service.get('service_name',''))} Estimate</h3>
              <p>{service.get('sidebar_body', 'Ready to start? Contact us today for a consultation.')}</p>
              <a class=\"btn\" href=\"../index.html#contact\">Request Estimate</a>
              <p class=\"phone-cta\">Or call <a href=\"tel:{PHONE_TEL}\">{PHONE_DISPLAY}</a></p>
            </div>

            <div class=\"sidebar-box\">
              <h4>Related Services</h4>
              <ul>
{related_links}
              </ul>
            </div>

            <div class=\"sidebar-box\">
              <h4>Service Areas</h4>
              <p>We provide {service.get('service_name','')} services in these areas:</p>
              <ul class=\"area-tags\">
{area_tags}
              </ul>
              <a href=\"../service-areas.html\">View all service areas →</a>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class=\"section alt faq-section\" id=\"faq\">
      <div class=\"wrap\">
        <h2>{service.get('faq_heading', f"Frequently Asked Questions About {service.get('service_name','')}")}</h2>
{faq_details_html}
      </div>
    </section>

    <section class=\"section cta-section\">
      <div class=\"wrap\" style=\"text-align:center;\">
        <h2>{service.get('cta_bottom_heading', f"Ready to Start Your {service.get('service_name','')}?")}</h2>
        <p class=\"lead\">{service.get('cta_bottom_subheading', f"Get an estimate from a trusted {service.get('service_name','').lower()} contractor.")}</p>
        <div class=\"cta_row\" style=\"justify-content:center;\">
          <a class=\"btn\" href=\"../index.html#contact\">Request Estimate</a>
          <a class=\"btn ghost\" href=\"tel:{PHONE_TEL}\">Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer" role="contentinfo">
    <div class="wrap footer-grid">
      <div class="footer-col">
        <h4>{BUSINESS_NAME}</h4>
        <p>Licensed Residential Builder.</p>
        <p><strong>License:</strong> State of Michigan Residential Builder</p>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p>Mon-Thu 9am-5pm</p>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        <ul>
          <li><a href="{slug}.html">{service.get('service_name','')}</a></li>
          <li><a href="kitchen-remodeling.html">Kitchen Remodeling</a></li>
          <li><a href="basement-finishing.html">Basement Finishing</a></li>
          <li><a href="../services.html">All Services</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Service Areas</h4>
        <ul>
{footer_area_links}
          <li><a href="../service-areas.html">All Areas</a></li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>&copy; 2025 {BUSINESS_NAME}. All rights reserved.</p>
    </div>
  </footer>

  <script>
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.nav');
    toggle?.addEventListener('click', () => {{
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', (!expanded)).toString();
      nav.classList.toggle('open');
    }});
  </script>
</body>
</html>
"""
def load_services(data_path: Path) -> List[Dict[str, Any]]:
    with data_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        # allow {"services": [...]} structure
        if "services" in data and isinstance(data["services"], list):
            return data["services"]
        raise ValueError("JSON must be a list or contain a 'services' list")
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of services")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate service pages from JSON data.")
    parser.add_argument("--data", required=True, help="Path to services_data.json")
    parser.add_argument("--output-dir", default="services", help="Output directory for HTML files")
    parser.add_argument("--slug", help="Generate only this slug (otherwise generates all)")
    args = parser.parse_args()

    data_path = Path(args.data)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    services = load_services(data_path)

    for svc in services:
        slug = svc.get("slug")
        if not slug:
            print("Skipping entry without slug")
            continue
        if args.slug and slug != args.slug:
            continue
        html = render_page(svc)
        out_file = output_dir / f"{slug}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
