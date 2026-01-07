import json
import re
import unicodedata
from pathlib import Path

SERVICES_HTML = Path("services.html")
OUTPUT_JSON = Path("services_data_generated.json")


def slugify(name: str) -> str:
    """Convert service name to kebab-case slug."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(ch for ch in normalized if ord(ch) < 128)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "service"


def extract_titles(html: str) -> list[str]:
    matches = re.findall(r"<h4>(.*?)</h4>", html, flags=re.DOTALL | re.IGNORECASE)
    cleaned = []
    for raw in matches:
        text = re.sub(r"<[^>]+>", "", raw).strip()
        if text:
            cleaned.append(text)
    return cleaned


def main() -> None:
    html = SERVICES_HTML.read_text(encoding="utf-8")
    raw_titles = extract_titles(html)

    # Drop obvious non-service/navigation items and avoid duplicate names.
    banned_slugs = {
        "our-services",
        "service-areas",
        "contact-us",
        "detroit-amp-metro-detroit-primary-focus",
        "residential-properties-12-family-dwellings",
        "townhouses-up-to-3-stories",
        "detached-accessory-structures",
    }

    seen: dict[str, str] = {}
    titles: list[tuple[str, str]] = []
    for name in raw_titles:
        base = slugify(name)
        slug = base
        idx = 2
        while slug in seen:
            slug = f"{base}-{idx}"
            idx += 1
        seen[slug] = name
        titles.append((name, slug))

    areas = [
        "Detroit",
        "Dearborn",
        "Livonia",
        "Southfield",
        "Royal Oak",
        "Troy",
        "Farmington Hills",
        "Ann Arbor",
        "Warren",
        "Sterling Heights",
    ]

    services = []
    unique_names: set[str] = set()
    for name, slug in titles:
        norm_name = name.lower()
        if slug in banned_slugs:
            continue
        if norm_name in unique_names:
            continue
        unique_names.add(norm_name)
        lower = name.lower()
        services.append(
            {
                "slug": slug,
                "service_name": name,
                "service_type": name,
                "city": "Detroit",
                "state": "MI",
                "meta_title": f"{name} | Midwest Flip LLC",
                "meta_description": f"{name} services for Detroit and Metro Detroit homes. Licensed, insured, and focused on clean execution, permits, and communication.",
                "og_description": f"Detroit {name} services with licensed builders and clear schedules.",
                "keywords": f"{lower}, contractor, Detroit",
                "hero_h1": f"{name} Services",
                "hero_lead": f"{name} for Detroit and Metro Detroit homes - proper planning, permits, and clean finishes.",
                "hero_badges": ["Licensed & Insured", "Clean Jobsite", "Transparent Pricing"],
                "cta_primary_label": f"Get a {name} Estimate",
                "cta_secondary_label": "Call (313) 389-6324",
                "h2_intro": f"Professional {name}",
                "intro_paragraphs": [
                    f"We deliver {lower} across Detroit with permit-ready scopes, coordinated trades, and tidy sites.",
                    "Expect clear communication, predictable scheduling, and finishes ready for daily use.",
                ],
                "service_image": f"{slug}.jpg",
                "service_image_alt": f"{name} project",
                "service_image_caption": f"Recent {lower} completed in Detroit",
                "h2_services": f"Our {name} Services",
                "services_intro": f"Select the {lower} help you need - planning through punch, we keep it organized and code-compliant.",
                "services_offered": [
                    {"title": f"{name} Planning", "description": f"Scope, sequencing, and material guidance tailored to your {lower}."},
                    {"title": f"{name} Execution", "description": "Licensed trades, inspections, and quality checks at each phase."},
                    {"title": "Finishing & QA", "description": "Clean finishes, protection, and punch-list follow-through."},
                    {"title": "Coordination & Permits", "description": "We handle city requirements, scheduling, and homeowner updates."},
                ],
                "h2_benefits": "Why Choose Us",
                "benefits": [
                    {"title": "Licensed Michigan Builder", "description": "Permits, inspections, and code alignment for Detroit and nearby cities."},
                    {"title": "Organized Process", "description": "Sequenced work to reduce delays and protect finished areas."},
                    {"title": "Clear Communication", "description": "Transparent pricing, scope clarity, and regular updates."},
                    {"title": "Clean Jobsite", "description": "Protection, debris control, and respectful crews in your home."},
                ],
                "h2_process": f"Our {name} Process",
                "process_intro": "A simple, repeatable flow to keep your project moving.",
                "process_steps": [
                    {"title": "Consult & Scope", "description": "Review goals, site conditions, and budget to set expectations."},
                    {"title": "Plan & Permit", "description": "Define schedule, materials, and submit permits when required."},
                    {"title": "Build & Inspect", "description": "Execute work in the right order with checkpoints and inspections."},
                    {"title": "Finish & Punch", "description": "Detail work, walkthrough, and closeout so it is ready for use."},
                ],
                "h2_pricing": "Pricing Overview",
                "pricing_table": {
                    "rows": [
                        {"label": "Standard projects", "value": "Custom estimate"},
                        {"label": "Expanded scope", "value": "Custom estimate"},
                        {"label": "Complex/structural", "value": "Custom estimate"},
                    ],
                    "note": "Pricing varies by scope, access, and selections. Request a written estimate for your project.",
                },
                "related_services": [],
                "service_areas": areas,
                "faq_heading": f"{name} FAQ",
                "faqs": [
                    {"q": f"Do you handle permits for {lower}?", "a": "Yes, we manage permits and inspections where required."},
                    {"q": "How long will the project take?", "a": "Timelines vary by scope; we provide a schedule before work starts."},
                    {"q": "Do you work in occupied homes?", "a": "Yes, we protect surfaces, manage debris, and keep you updated daily."},
                ],
                "sidebar_title": name,
                "sidebar_body": f"Need {lower}? Get a licensed Detroit team to plan, permit, and deliver clean results.",
            }
        )

    OUTPUT_JSON.write_text(json.dumps(services, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"Wrote {len(services)} services to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
