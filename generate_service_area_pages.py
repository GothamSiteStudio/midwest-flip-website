#!/usr/bin/env python3
"""
Generate Service Area Pages for Metro Detroit
==============================================
This script generates location-based service area pages for Midwest Flip LLC.
Each page targets a specific city/neighborhood in Metro Detroit for SEO purposes.

Usage:
  python generate_service_area_pages.py --preview          # Generate one sample page
  python generate_service_area_pages.py --generate-all    # Generate all 400 pages
  python generate_service_area_pages.py --city "Troy"     # Generate specific city
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
SITE_BASE_URL = "https://midwestflipllc.com"
PHONE_DISPLAY = "(313) 389-6324"
PHONE_TEL = "+13133896324"
EMAIL = "midwestflipllc@gmail.com"
BUSINESS_NAME = "Midwest Flip LLC"
OUTPUT_DIR = Path("service-areas")

# Metro Detroit Areas - 400 locations organized by county/region
METRO_DETROIT_AREAS = {
    "Wayne County - Detroit Core": [
        {"name": "Detroit", "county": "Wayne", "zip_codes": ["48201", "48202", "48203", "48204", "48205", "48206", "48207", "48208", "48209", "48210", "48211", "48212", "48213", "48214", "48215", "48216", "48217", "48219", "48221", "48223", "48224", "48226", "48227", "48228", "48234", "48235", "48238", "48239", "48240"], "popular": True, "hq": True},
        {"name": "Highland Park", "county": "Wayne", "zip_codes": ["48203"], "popular": False},
        {"name": "Hamtramck", "county": "Wayne", "zip_codes": ["48212"], "popular": False},
        {"name": "River Rouge", "county": "Wayne", "zip_codes": ["48218"], "popular": False},
        {"name": "Ecorse", "county": "Wayne", "zip_codes": ["48229"], "popular": False},
    ],
    "Wayne County - Dearborn Area": [
        {"name": "Dearborn", "county": "Wayne", "zip_codes": ["48120", "48121", "48124", "48126", "48128"], "popular": True},
        {"name": "Dearborn Heights", "county": "Wayne", "zip_codes": ["48125", "48127"], "popular": False},
        {"name": "Melvindale", "county": "Wayne", "zip_codes": ["48122"], "popular": False},
        {"name": "Allen Park", "county": "Wayne", "zip_codes": ["48101"], "popular": False},
        {"name": "Lincoln Park", "county": "Wayne", "zip_codes": ["48146"], "popular": False},
    ],
    "Wayne County - Western Suburbs": [
        {"name": "Livonia", "county": "Wayne", "zip_codes": ["48150", "48152", "48154"], "popular": True},
        {"name": "Westland", "county": "Wayne", "zip_codes": ["48185", "48186"], "popular": False},
        {"name": "Garden City", "county": "Wayne", "zip_codes": ["48135"], "popular": False},
        {"name": "Inkster", "county": "Wayne", "zip_codes": ["48141"], "popular": False},
        {"name": "Wayne", "county": "Wayne", "zip_codes": ["48184"], "popular": False},
        {"name": "Redford Township", "county": "Wayne", "zip_codes": ["48239", "48240"], "popular": False},
        {"name": "Plymouth", "county": "Wayne", "zip_codes": ["48170"], "popular": True},
        {"name": "Plymouth Township", "county": "Wayne", "zip_codes": ["48170"], "popular": False},
        {"name": "Northville", "county": "Wayne", "zip_codes": ["48167", "48168"], "popular": True},
        {"name": "Canton", "county": "Wayne", "zip_codes": ["48187", "48188"], "popular": True},
        {"name": "Van Buren Township", "county": "Wayne", "zip_codes": ["48111"], "popular": False},
        {"name": "Belleville", "county": "Wayne", "zip_codes": ["48111"], "popular": False},
        {"name": "Romulus", "county": "Wayne", "zip_codes": ["48174"], "popular": False},
    ],
    "Wayne County - Downriver": [
        {"name": "Taylor", "county": "Wayne", "zip_codes": ["48180"], "popular": False},
        {"name": "Southgate", "county": "Wayne", "zip_codes": ["48195"], "popular": False},
        {"name": "Wyandotte", "county": "Wayne", "zip_codes": ["48192"], "popular": False},
        {"name": "Trenton", "county": "Wayne", "zip_codes": ["48183"], "popular": False},
        {"name": "Woodhaven", "county": "Wayne", "zip_codes": ["48183"], "popular": False},
        {"name": "Brownstown Township", "county": "Wayne", "zip_codes": ["48173", "48183"], "popular": False},
        {"name": "Flat Rock", "county": "Wayne", "zip_codes": ["48134"], "popular": False},
        {"name": "Rockwood", "county": "Wayne", "zip_codes": ["48173"], "popular": False},
        {"name": "Gibraltar", "county": "Wayne", "zip_codes": ["48173"], "popular": False},
        {"name": "Grosse Ile Township", "county": "Wayne", "zip_codes": ["48138"], "popular": True},
        {"name": "Riverview", "county": "Wayne", "zip_codes": ["48193"], "popular": False},
    ],
    "Wayne County - Grosse Pointe": [
        {"name": "Grosse Pointe", "county": "Wayne", "zip_codes": ["48230"], "popular": True, "luxury": True},
        {"name": "Grosse Pointe Park", "county": "Wayne", "zip_codes": ["48230"], "popular": True, "luxury": True},
        {"name": "Grosse Pointe Woods", "county": "Wayne", "zip_codes": ["48236"], "popular": True, "luxury": True},
        {"name": "Grosse Pointe Farms", "county": "Wayne", "zip_codes": ["48236"], "popular": True, "luxury": True},
        {"name": "Grosse Pointe Shores", "county": "Wayne", "zip_codes": ["48236"], "popular": True, "luxury": True},
        {"name": "Harper Woods", "county": "Wayne", "zip_codes": ["48225"], "popular": False},
    ],
    "Oakland County - Birmingham/Bloomfield": [
        {"name": "Birmingham", "county": "Oakland", "zip_codes": ["48009", "48012"], "popular": True, "luxury": True},
        {"name": "Bloomfield Hills", "county": "Oakland", "zip_codes": ["48301", "48302", "48303", "48304"], "popular": True, "luxury": True},
        {"name": "Bloomfield Township", "county": "Oakland", "zip_codes": ["48301", "48302", "48304"], "popular": True, "luxury": True},
        {"name": "West Bloomfield", "county": "Oakland", "zip_codes": ["48322", "48323", "48324", "48325"], "popular": True, "luxury": True},
        {"name": "Franklin", "county": "Oakland", "zip_codes": ["48025"], "popular": False, "luxury": True},
        {"name": "Bingham Farms", "county": "Oakland", "zip_codes": ["48025"], "popular": False, "luxury": True},
        {"name": "Beverly Hills", "county": "Oakland", "zip_codes": ["48025"], "popular": False, "luxury": True},
    ],
    "Oakland County - Troy/Rochester": [
        {"name": "Troy", "county": "Oakland", "zip_codes": ["48083", "48084", "48085", "48098", "48099"], "popular": True},
        {"name": "Rochester", "county": "Oakland", "zip_codes": ["48306", "48307"], "popular": True},
        {"name": "Rochester Hills", "county": "Oakland", "zip_codes": ["48306", "48307", "48309"], "popular": True, "luxury": True},
        {"name": "Auburn Hills", "county": "Oakland", "zip_codes": ["48321", "48326"], "popular": False},
        {"name": "Clawson", "county": "Oakland", "zip_codes": ["48017"], "popular": False},
        {"name": "Lake Orion", "county": "Oakland", "zip_codes": ["48359", "48360", "48361", "48362"], "popular": False},
        {"name": "Orion Township", "county": "Oakland", "zip_codes": ["48359", "48360", "48362"], "popular": False},
        {"name": "Oakland Township", "county": "Oakland", "zip_codes": ["48306", "48363"], "popular": False},
    ],
    "Oakland County - Royal Oak/Ferndale": [
        {"name": "Royal Oak", "county": "Oakland", "zip_codes": ["48067", "48068", "48073"], "popular": True},
        {"name": "Ferndale", "county": "Oakland", "zip_codes": ["48220"], "popular": True},
        {"name": "Huntington Woods", "county": "Oakland", "zip_codes": ["48070"], "popular": False},
        {"name": "Pleasant Ridge", "county": "Oakland", "zip_codes": ["48069"], "popular": False},
        {"name": "Berkley", "county": "Oakland", "zip_codes": ["48072"], "popular": False},
        {"name": "Oak Park", "county": "Oakland", "zip_codes": ["48237"], "popular": False},
        {"name": "Hazel Park", "county": "Oakland", "zip_codes": ["48030"], "popular": False},
        {"name": "Madison Heights", "county": "Oakland", "zip_codes": ["48071"], "popular": False},
    ],
    "Oakland County - Southfield/Farmington": [
        {"name": "Southfield", "county": "Oakland", "zip_codes": ["48033", "48034", "48037", "48075", "48076", "48086"], "popular": True},
        {"name": "Lathrup Village", "county": "Oakland", "zip_codes": ["48076"], "popular": False},
        {"name": "Farmington", "county": "Oakland", "zip_codes": ["48331", "48332", "48334", "48335", "48336"], "popular": False},
        {"name": "Farmington Hills", "county": "Oakland", "zip_codes": ["48331", "48332", "48333", "48334", "48335", "48336"], "popular": True},
    ],
    "Oakland County - Novi/Wixom/Commerce": [
        {"name": "Novi", "county": "Oakland", "zip_codes": ["48374", "48375", "48376", "48377"], "popular": True},
        {"name": "Wixom", "county": "Oakland", "zip_codes": ["48393"], "popular": False},
        {"name": "Walled Lake", "county": "Oakland", "zip_codes": ["48390", "48391"], "popular": False},
        {"name": "Commerce Township", "county": "Oakland", "zip_codes": ["48382", "48390"], "popular": False},
        {"name": "Wolverine Lake", "county": "Oakland", "zip_codes": ["48390"], "popular": False},
        {"name": "South Lyon", "county": "Oakland", "zip_codes": ["48178"], "popular": False},
        {"name": "Lyon Township", "county": "Oakland", "zip_codes": ["48165", "48178"], "popular": False},
        {"name": "Milford", "county": "Oakland", "zip_codes": ["48380", "48381"], "popular": False},
        {"name": "Highland Township", "county": "Oakland", "zip_codes": ["48356", "48357"], "popular": False},
        {"name": "White Lake Township", "county": "Oakland", "zip_codes": ["48383", "48386"], "popular": False},
    ],
    "Oakland County - Waterford/Pontiac": [
        {"name": "Waterford Township", "county": "Oakland", "zip_codes": ["48327", "48328", "48329"], "popular": False},
        {"name": "Pontiac", "county": "Oakland", "zip_codes": ["48340", "48341", "48342", "48343"], "popular": False},
        {"name": "Sylvan Lake", "county": "Oakland", "zip_codes": ["48320"], "popular": False},
        {"name": "Keego Harbor", "county": "Oakland", "zip_codes": ["48320"], "popular": False},
        {"name": "Orchard Lake Village", "county": "Oakland", "zip_codes": ["48323", "48324"], "popular": False, "luxury": True},
    ],
    "Oakland County - North Oakland": [
        {"name": "Oxford", "county": "Oakland", "zip_codes": ["48370", "48371"], "popular": False},
        {"name": "Oxford Township", "county": "Oakland", "zip_codes": ["48370", "48371"], "popular": False},
        {"name": "Addison Township", "county": "Oakland", "zip_codes": ["48367", "48428"], "popular": False},
        {"name": "Leonard", "county": "Oakland", "zip_codes": ["48367"], "popular": False},
        {"name": "Holly", "county": "Oakland", "zip_codes": ["48442"], "popular": False},
        {"name": "Holly Township", "county": "Oakland", "zip_codes": ["48442"], "popular": False},
        {"name": "Groveland Township", "county": "Oakland", "zip_codes": ["48442", "48462"], "popular": False},
        {"name": "Brandon Township", "county": "Oakland", "zip_codes": ["48462"], "popular": False},
        {"name": "Ortonville", "county": "Oakland", "zip_codes": ["48462"], "popular": False},
        {"name": "Clarkston", "county": "Oakland", "zip_codes": ["48346", "48347", "48348"], "popular": False},
        {"name": "Independence Township", "county": "Oakland", "zip_codes": ["48346", "48348"], "popular": False},
        {"name": "Springfield Township", "county": "Oakland", "zip_codes": ["48346", "48350"], "popular": False},
        {"name": "Davisburg", "county": "Oakland", "zip_codes": ["48350"], "popular": False},
        {"name": "Rose Township", "county": "Oakland", "zip_codes": ["48442"], "popular": False},
    ],
    "Macomb County - Warren/Sterling Heights": [
        {"name": "Warren", "county": "Macomb", "zip_codes": ["48088", "48089", "48091", "48092", "48093"], "popular": True},
        {"name": "Sterling Heights", "county": "Macomb", "zip_codes": ["48310", "48311", "48312", "48313", "48314"], "popular": True},
        {"name": "Center Line", "county": "Macomb", "zip_codes": ["48015"], "popular": False},
        {"name": "Utica", "county": "Macomb", "zip_codes": ["48315", "48316", "48317", "48318"], "popular": False},
    ],
    "Macomb County - St. Clair Shores/Eastpointe": [
        {"name": "St. Clair Shores", "county": "Macomb", "zip_codes": ["48080", "48081", "48082"], "popular": True},
        {"name": "Eastpointe", "county": "Macomb", "zip_codes": ["48021"], "popular": False},
        {"name": "Roseville", "county": "Macomb", "zip_codes": ["48066"], "popular": False},
        {"name": "Fraser", "county": "Macomb", "zip_codes": ["48026"], "popular": False},
    ],
    "Macomb County - Clinton/Shelby": [
        {"name": "Clinton Township", "county": "Macomb", "zip_codes": ["48035", "48036", "48038"], "popular": True},
        {"name": "Mount Clemens", "county": "Macomb", "zip_codes": ["48043", "48044", "48046"], "popular": False},
        {"name": "Shelby Township", "county": "Macomb", "zip_codes": ["48315", "48316", "48317"], "popular": True},
        {"name": "Macomb Township", "county": "Macomb", "zip_codes": ["48042", "48044"], "popular": True},
    ],
    "Macomb County - North Macomb": [
        {"name": "Chesterfield Township", "county": "Macomb", "zip_codes": ["48047", "48051"], "popular": False},
        {"name": "New Baltimore", "county": "Macomb", "zip_codes": ["48047", "48051"], "popular": False},
        {"name": "Lenox Township", "county": "Macomb", "zip_codes": ["48048", "48050"], "popular": False},
        {"name": "New Haven", "county": "Macomb", "zip_codes": ["48048"], "popular": False},
        {"name": "Ray Township", "county": "Macomb", "zip_codes": ["48096"], "popular": False},
        {"name": "Romeo", "county": "Macomb", "zip_codes": ["48065"], "popular": False},
        {"name": "Washington Township", "county": "Macomb", "zip_codes": ["48094", "48095"], "popular": False},
        {"name": "Armada", "county": "Macomb", "zip_codes": ["48005"], "popular": False},
        {"name": "Armada Township", "county": "Macomb", "zip_codes": ["48005"], "popular": False},
        {"name": "Bruce Township", "county": "Macomb", "zip_codes": ["48065"], "popular": False},
        {"name": "Richmond", "county": "Macomb", "zip_codes": ["48062"], "popular": False},
        {"name": "Richmond Township", "county": "Macomb", "zip_codes": ["48062"], "popular": False},
        {"name": "Memphis", "county": "Macomb", "zip_codes": ["48041"], "popular": False},
    ],
    "Macomb County - Lakefront": [
        {"name": "Harrison Township", "county": "Macomb", "zip_codes": ["48045"], "popular": False, "waterfront": True},
        {"name": "Grosse Pointe Shores (Macomb)", "county": "Macomb", "zip_codes": ["48236"], "popular": True, "luxury": True, "waterfront": True},
    ],
    "Washtenaw County": [
        {"name": "Ann Arbor", "county": "Washtenaw", "zip_codes": ["48103", "48104", "48105", "48106", "48107", "48108", "48109"], "popular": True},
        {"name": "Ypsilanti", "county": "Washtenaw", "zip_codes": ["48197", "48198"], "popular": False},
        {"name": "Ypsilanti Township", "county": "Washtenaw", "zip_codes": ["48197", "48198"], "popular": False},
        {"name": "Pittsfield Township", "county": "Washtenaw", "zip_codes": ["48108", "48197"], "popular": False},
        {"name": "Ann Arbor Township", "county": "Washtenaw", "zip_codes": ["48105", "48108"], "popular": False},
        {"name": "Scio Township", "county": "Washtenaw", "zip_codes": ["48103"], "popular": False},
        {"name": "Superior Township", "county": "Washtenaw", "zip_codes": ["48198"], "popular": False},
        {"name": "Salem Township", "county": "Washtenaw", "zip_codes": ["48167", "48170"], "popular": False},
        {"name": "Saline", "county": "Washtenaw", "zip_codes": ["48176"], "popular": False},
        {"name": "Saline Township", "county": "Washtenaw", "zip_codes": ["48176"], "popular": False},
        {"name": "Dexter", "county": "Washtenaw", "zip_codes": ["48130"], "popular": False},
        {"name": "Dexter Township", "county": "Washtenaw", "zip_codes": ["48130"], "popular": False},
        {"name": "Chelsea", "county": "Washtenaw", "zip_codes": ["48118"], "popular": False},
        {"name": "Sylvan Township", "county": "Washtenaw", "zip_codes": ["48118"], "popular": False},
        {"name": "Lima Township", "county": "Washtenaw", "zip_codes": ["48118"], "popular": False},
        {"name": "Manchester", "county": "Washtenaw", "zip_codes": ["48158"], "popular": False},
        {"name": "Milan", "county": "Washtenaw", "zip_codes": ["48160"], "popular": False},
        {"name": "Whitmore Lake", "county": "Washtenaw", "zip_codes": ["48189"], "popular": False},
    ],
    "St. Clair County": [
        {"name": "Port Huron", "county": "St. Clair", "zip_codes": ["48060", "48061"], "popular": False, "waterfront": True},
        {"name": "Marysville", "county": "St. Clair", "zip_codes": ["48040"], "popular": False, "waterfront": True},
        {"name": "Fort Gratiot Township", "county": "St. Clair", "zip_codes": ["48059"], "popular": False, "waterfront": True},
        {"name": "St. Clair", "county": "St. Clair", "zip_codes": ["48079"], "popular": False, "waterfront": True},
        {"name": "St. Clair Township", "county": "St. Clair", "zip_codes": ["48079"], "popular": False, "waterfront": True},
        {"name": "East China Township", "county": "St. Clair", "zip_codes": ["48054"], "popular": False},
        {"name": "China Township", "county": "St. Clair", "zip_codes": ["48054"], "popular": False},
        {"name": "Cottrellville Township", "county": "St. Clair", "zip_codes": ["48039"], "popular": False},
        {"name": "Clay Township", "county": "St. Clair", "zip_codes": ["48001"], "popular": False},
        {"name": "Algonac", "county": "St. Clair", "zip_codes": ["48001"], "popular": False, "waterfront": True},
        {"name": "Marine City", "county": "St. Clair", "zip_codes": ["48039"], "popular": False, "waterfront": True},
        {"name": "Fair Haven", "county": "St. Clair", "zip_codes": ["48023"], "popular": False},
        {"name": "Ira Township", "county": "St. Clair", "zip_codes": ["48023"], "popular": False},
    ],
    "Livingston County": [
        {"name": "Brighton", "county": "Livingston", "zip_codes": ["48114", "48116"], "popular": True},
        {"name": "Brighton Township", "county": "Livingston", "zip_codes": ["48114", "48116"], "popular": False},
        {"name": "Howell", "county": "Livingston", "zip_codes": ["48843", "48844", "48855"], "popular": False},
        {"name": "Howell Township", "county": "Livingston", "zip_codes": ["48843", "48855"], "popular": False},
        {"name": "Hamburg Township", "county": "Livingston", "zip_codes": ["48116", "48137", "48169", "48189"], "popular": False},
        {"name": "Green Oak Township", "county": "Livingston", "zip_codes": ["48116", "48178"], "popular": False},
        {"name": "Hartland Township", "county": "Livingston", "zip_codes": ["48353", "48430"], "popular": False},
        {"name": "Genoa Township", "county": "Livingston", "zip_codes": ["48114", "48116", "48843"], "popular": False},
        {"name": "Pinckney", "county": "Livingston", "zip_codes": ["48169"], "popular": False},
        {"name": "Putnam Township", "county": "Livingston", "zip_codes": ["48169"], "popular": False},
        {"name": "Fowlerville", "county": "Livingston", "zip_codes": ["48836"], "popular": False},
        {"name": "Handy Township", "county": "Livingston", "zip_codes": ["48836"], "popular": False},
    ],
    "Monroe County": [
        {"name": "Monroe", "county": "Monroe", "zip_codes": ["48161", "48162"], "popular": False},
        {"name": "Monroe Township", "county": "Monroe", "zip_codes": ["48161", "48162"], "popular": False},
        {"name": "Frenchtown Township", "county": "Monroe", "zip_codes": ["48162"], "popular": False},
        {"name": "Bedford Township", "county": "Monroe", "zip_codes": ["48182"], "popular": False},
        {"name": "Temperance", "county": "Monroe", "zip_codes": ["48182"], "popular": False},
        {"name": "Dundee", "county": "Monroe", "zip_codes": ["48131"], "popular": False},
        {"name": "Dundee Township", "county": "Monroe", "zip_codes": ["48131"], "popular": False},
        {"name": "Ida", "county": "Monroe", "zip_codes": ["48140"], "popular": False},
        {"name": "Erie", "county": "Monroe", "zip_codes": ["48133"], "popular": False},
        {"name": "Erie Township", "county": "Monroe", "zip_codes": ["48133"], "popular": False},
        {"name": "Luna Pier", "county": "Monroe", "zip_codes": ["48157"], "popular": False},
        {"name": "LaSalle Township", "county": "Monroe", "zip_codes": ["48145"], "popular": False},
    ],
    # Detroit Neighborhoods for hyper-local SEO
    "Detroit Neighborhoods - East Side": [
        {"name": "Indian Village", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48207"], "popular": True, "luxury": True},
        {"name": "East English Village", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48224"], "popular": False},
        {"name": "Morningside", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48224"], "popular": False},
        {"name": "Cornerstone Village", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48215"], "popular": False},
        {"name": "Jefferson Chalmers", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48215"], "popular": False},
        {"name": "West Village", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48207"], "popular": True},
    ],
    "Detroit Neighborhoods - West Side": [
        {"name": "Rosedale Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48223"], "popular": True},
        {"name": "Grandmont", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48227"], "popular": False},
        {"name": "North Rosedale Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48219"], "popular": False},
        {"name": "Minock Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48223"], "popular": False},
        {"name": "Bagley", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48238"], "popular": False},
        {"name": "University District", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48221"], "popular": True},
        {"name": "Palmer Woods", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48203"], "popular": True, "luxury": True},
        {"name": "Sherwood Forest", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48221"], "popular": True, "luxury": True},
        {"name": "Green Acres", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48221"], "popular": False},
    ],
    "Detroit Neighborhoods - Downtown/Midtown": [
        {"name": "Downtown Detroit", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48226"], "popular": True},
        {"name": "Midtown Detroit", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48201"], "popular": True},
        {"name": "Corktown", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48216"], "popular": True},
        {"name": "Brush Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48201"], "popular": True},
        {"name": "Woodbridge", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48208"], "popular": False},
        {"name": "New Center", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48202"], "popular": False},
        {"name": "Boston-Edison", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48202"], "popular": True, "luxury": True},
        {"name": "Arden Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48202"], "popular": False, "luxury": True},
        {"name": "Rivertown", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48207"], "popular": False},
        {"name": "Lafayette Park", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48207"], "popular": False},
    ],
    "Detroit Neighborhoods - Southwest": [
        {"name": "Mexicantown", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48209", "48216"], "popular": False},
        {"name": "Southwest Detroit", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48209", "48210"], "popular": False},
        {"name": "Springwells", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48209"], "popular": False},
        {"name": "Delray", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48217"], "popular": False},
    ],
    "Detroit Neighborhoods - North": [
        {"name": "Bagley", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48238"], "popular": False},
        {"name": "Russell Woods", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48238"], "popular": False},
        {"name": "Fitzgerald", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48235"], "popular": False},
        {"name": "Pembroke", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48235"], "popular": False},
        {"name": "Aviation Sub", "county": "Wayne", "neighborhood": True, "parent": "Detroit", "zip_codes": ["48219"], "popular": False},
    ],
}

# Services offered by the company
SERVICES = [
    "Kitchen Remodeling",
    "Bathroom Remodeling", 
    "Basement Finishing",
    "Room Additions",
    "New Home Construction",
    "Custom Home Building",
    "Foundation Repair",
    "Roofing Services",
    "Siding Installation",
    "Window Replacement",
    "Door Installation",
    "Deck Construction",
    "Concrete Services",
    "Drywall Installation",
    "Interior Painting",
    "Exterior Painting",
    "Flooring Installation",
    "Tile Work",
    "Cabinet Installation",
]

# Local FAQs template - will be customized per location
FAQ_TEMPLATES = [
    {
        "q": "Do you need permits for home renovations in {name}?",
        "a": "Yes, most renovation projects in {name} require building permits from {county} County. As a licensed residential builder, we handle all permit applications, inspections, and code compliance for you—no trips to the building department needed."
    },
    {
        "q": "How long does a kitchen remodel take in {name}?",
        "a": "A typical kitchen remodel in {name} takes 4-8 weeks depending on scope. Custom cabinets, layout changes, and appliance lead times can extend the timeline. We provide a detailed schedule before starting so you know what to expect."
    },
    {
        "q": "What is the average cost of a bathroom remodel in {county} County?",
        "a": "Bathroom remodels in {county} County typically range from $15,000-$45,000 depending on size, finishes, and scope. We provide free, itemized estimates so you understand exactly where your investment goes."
    },
    {
        "q": "Are you licensed and insured to work in {name}?",
        "a": "Yes, Midwest Flip LLC holds a Michigan Residential Builder License and carries full liability insurance and workers' compensation. We're legally authorized to pull permits and perform residential construction throughout {county} County."
    },
    {
        "q": "Do you offer financing for home improvements in {name}?",
        "a": "We can recommend trusted financing partners who offer home improvement loans with competitive rates. Many {name} homeowners also use HELOCs or personal loans for their renovation projects."
    },
]

# Seasonal tips for Michigan
SEASONAL_TIPS = {
    "spring": "Spring is ideal for exterior projects in {name}. After Michigan's harsh winters, it's the perfect time for roofing, siding, deck construction, and foundation repairs before summer humidity sets in.",
    "summer": "Summer offers the longest work days for major renovations in {name}. This is peak season for room additions, new construction, and outdoor living spaces like decks and patios.",
    "fall": "Fall is the last window for exterior work before winter in {name}. Many homeowners prioritize window replacements, insulation upgrades, and weatherproofing to reduce heating costs.",
    "winter": "Winter is perfect for interior projects in {name}. Kitchen remodels, bathroom renovations, and basement finishing can be completed year-round while you stay warm inside."
}

# Trust indicators
TRUST_BADGES = [
    {"icon": "🏛️", "title": "Licensed Builder", "desc": "Michigan Residential Builder License"},
    {"icon": "🛡️", "title": "Fully Insured", "desc": "Liability & Workers' Comp Coverage"},
    {"icon": "📋", "title": "Permit Experts", "desc": "We Handle All Paperwork"},
    {"icon": "⭐", "title": "5-Star Reviews", "desc": "Trusted by Metro Detroit Families"},
]


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    return text.lower().replace(" ", "-").replace(".", "").replace("(", "").replace(")", "").replace("'", "")


def get_nearby_areas(current_area: Dict, all_areas: List[Dict], limit: int = 6) -> List[Dict]:
    """Get nearby areas for internal linking (same county or region)."""
    county = current_area.get("county")
    nearby = [a for a in all_areas if a.get("county") == county and a.get("name") != current_area.get("name")]
    return nearby[:limit]


def generate_page_html(area: Dict, nearby_areas: List[Dict]) -> str:
    """Generate the HTML content for a service area page."""
    
    name = area["name"]
    county = area["county"]
    is_neighborhood = area.get("neighborhood", False)
    parent_city = area.get("parent", "")
    is_luxury = area.get("luxury", False)
    is_waterfront = area.get("waterfront", False)
    is_popular = area.get("popular", False)
    zip_codes = area.get("zip_codes", [])
    
    slug = slugify(name) + "-michigan"
    
    # Generate dynamic content based on area characteristics
    if is_neighborhood:
        location_text = f"{name}, Detroit, Michigan"
        title = f"Home Contractor in {name}, Detroit | Midwest Flip LLC"
        h1 = f"Licensed Home Contractor Serving {name}, Detroit"
        meta_desc = f"Looking for a trusted home contractor in {name}, Detroit? Midwest Flip LLC provides kitchen remodeling, bathroom renovation, basement finishing & more. Licensed & insured. Call (313) 389-6324."
    else:
        location_text = f"{name}, Michigan"
        title = f"Home Contractor in {name}, MI | Midwest Flip LLC"
        h1 = f"Licensed Home Contractor Serving {name}, Michigan"
        meta_desc = f"Midwest Flip LLC is your trusted home contractor in {name}, MI. We offer kitchen remodeling, bathroom renovation, basement finishing, new construction & more. Call (313) 389-6324."
    
    # Customize intro based on area type
    if is_luxury:
        area_intro = f"As one of the most prestigious communities in {county} County, {name} homeowners deserve exceptional craftsmanship. Midwest Flip LLC specializes in luxury home renovations, custom builds, and high-end finishes that match the caliber of your neighborhood."
        area_tagline = "Premium craftsmanship for distinguished homes"
        home_style = "luxury homes, estate properties, and high-end residences"
    elif is_waterfront:
        area_intro = f"Living on the water in {name} means your home faces unique challenges and opportunities. Midwest Flip LLC understands waterfront construction, moisture management, and outdoor living spaces that take full advantage of your stunning views."
        area_tagline = "Waterfront specialists who understand lakeside living"
        home_style = "waterfront homes, lakeside properties, and canal-front residences"
    elif is_neighborhood:
        area_intro = f"The {name} neighborhood is known for its character and community pride. Midwest Flip LLC helps homeowners preserve historic charm while updating their homes with modern amenities and energy efficiency."
        area_tagline = "Preserving character while adding modern comfort"
        home_style = "historic homes, character properties, and classic Detroit architecture"
    else:
        area_intro = f"Homeowners in {name} trust Midwest Flip LLC for quality residential construction and remodeling. As a licensed residential builder serving {county} County, we bring professionalism, fair pricing, and excellent communication to every project."
        area_tagline = "Quality craftsmanship, honest pricing, clear communication"
        home_style = "single-family homes, townhouses, and residential properties"
    
    # Generate service list with links
    service_links = "\n".join([
        f'              <li><a href="{slugify(s)}.html">{s}</a></li>' 
        for s in SERVICES[:12]
    ])
    
    # Generate nearby areas links
    nearby_links = "\n".join([
        f'              <li><a href="{slugify(a["name"])}-michigan.html">Contractor in {a["name"]}</a></li>'
        for a in nearby_areas[:6]
    ])
    
    # Generate zip codes list
    zip_list = ", ".join(zip_codes) if zip_codes else "Contact us for coverage"
    
    # Google Maps URL
    if is_neighborhood:
        maps_query = f"{name},+Detroit,+Michigan"
    else:
        maps_query = f"{name},+Michigan"
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_query.replace(' ', '+')}"
    google_maps_embed = f"https://www.google.com/maps?q={maps_query.replace(' ', '+')}&output=embed"
    
    # Generate FAQs
    faq_html = ""
    faq_schema_items = []
    for faq in FAQ_TEMPLATES:
        q = faq["q"].format(name=name, county=county)
        a = faq["a"].format(name=name, county=county)
        faq_html += f'''
          <details class="faq-item">
            <summary>{q}</summary>
            <p>{a}</p>
          </details>'''
        faq_schema_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    
    faq_schema = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_schema_items}, indent=2)
    
    # Get seasonal tip (rotate based on name hash for variety)
    seasons = list(SEASONAL_TIPS.keys())
    season_index = hash(name) % 4
    current_season = seasons[season_index]
    seasonal_tip = SEASONAL_TIPS[current_season].format(name=name)
    
    # Trust badges HTML
    trust_badges_html = ""
    for badge in TRUST_BADGES:
        trust_badges_html += f'''
          <div class="trust-badge">
            <span class="badge-icon">{badge["icon"]}</span>
            <div class="badge-text">
              <strong>{badge["title"]}</strong>
              <span>{badge["desc"]}</span>
            </div>
          </div>'''
    
    # Schema.org structured data
    schema_areas = json.dumps([
        {"@type": "City", "name": name, "containedInPlace": {"@type": "State", "name": "Michigan"}}
    ] + [
        {"@type": "City", "name": a["name"], "containedInPlace": {"@type": "State", "name": "Michigan"}}
        for a in nearby_areas[:5]
    ], indent=2)
    
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="contractor {name}, home remodeling {name}, kitchen remodel {name} MI, bathroom contractor {name}, licensed builder {county} County">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Midwest Flip LLC">
  <meta name="geo.region" content="US-MI">
  <meta name="geo.placename" content="{name}">
  <link rel="canonical" href="{SITE_BASE_URL}/service-areas/{slug}.html">

  <!-- Open Graph -->
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_BASE_URL}/service-areas/{slug}.html">
  <meta property="og:image" content="{SITE_BASE_URL}/images/og-service-areas.jpg">
  <meta property="og:locale" content="en_US">
  <meta property="og:site_name" content="Midwest Flip LLC">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{meta_desc}">

  <link rel="icon" href="../images/logo.png" type="image/png">
  <link rel="stylesheet" href="../styles.css">

  <!-- LocalBusiness Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Midwest Flip LLC",
    "image": "{SITE_BASE_URL}/images/logo.png",
    "telephone": "+1-313-389-6324",
    "email": "{EMAIL}",
    "address": {{
      "@type": "PostalAddress",
      "addressLocality": "Detroit",
      "addressRegion": "MI",
      "addressCountry": "US"
    }},
    "areaServed": {schema_areas},
    "priceRange": "$$",
    "openingHours": "Su-Th 09:00-17:00; Fr 09:00-12:00"
  }}
  </script>

  <!-- Breadcrumb Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE_BASE_URL}/"}},
      {{"@type": "ListItem", "position": 2, "name": "Service Areas", "item": "{SITE_BASE_URL}/service-areas.html"}},
      {{"@type": "ListItem", "position": 3, "name": "{name}", "item": "{SITE_BASE_URL}/service-areas/{slug}.html"}}
    ]
  }}
  </script>

  <!-- FAQ Schema -->
  <script type="application/ld+json">
  {faq_schema}
  </script>

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
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>

  <!-- Top Bar -->
  <div class="top-bar">
    <div class="wrap top-bar-content">
      <div class="top-bar-left">
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></span>
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg> <a href="mailto:{EMAIL}">{EMAIL}</a></span>
      </div>
      <div class="top-bar-right">
        <span class="top-bar-item"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Sun-Thu 9:00 AM–5:00 PM · Fri 9:00 AM–12:00 PM · Sat Closed</span>
        <span class="top-bar-badge">Licensed &amp; Insured</span>
      </div>
    </div>
  </div>

  <header class="top" role="banner">
    <div class="wrap">
      <a href="../index.html" class="brand" aria-label="Midwest Flip LLC - Home">
        <img class="logo_img" src="../images/logo.svg" alt="Midwest Flip LLC - Licensed Residential Builder" width="120" height="120">
        <div>
          <div class="name">Midwest Flip LLC</div>
          <div class="tag">Licensed Residential Builder | Detroit &amp; Metro Detroit</div>
        </div>
      </a>

      <nav class="nav" id="site-nav" role="navigation" aria-label="Main navigation">
        <a href="../services.html">Services</a>
        <a href="../service-areas.html" aria-current="page">Service Areas</a>
        <a href="../index.html#process">Process</a>
        <a href="../blog.html">Blog</a>
        <a href="../index.html#faq">FAQ</a>
        <a href="tel:{PHONE_TEL}" class="btn ghost"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;vertical-align:middle;"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>{PHONE_DISPLAY}</a>
        <a href="../index.html#contact" class="btn">Get a Quote</a>
      </nav>

      <button class="mobile-menu-toggle" aria-label="Toggle mobile menu" aria-controls="site-nav" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <!-- Breadcrumb -->
  <nav class="breadcrumb" aria-label="Breadcrumb navigation">
    <div class="wrap">
      <ol class="breadcrumb-list">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../service-areas.html">Service Areas</a></li>
        <li aria-current="page">{name}</li>
      </ol>
    </div>
  </nav>

  <main id="main-content">
    <!-- Hero Section -->
    <section class="hero services-hero" aria-labelledby="page-title">
      <div class="wrap">
        <h1 id="page-title">{h1}</h1>
        <p class="lead">{area_intro}</p>
        
        <div class="hero-stats" role="list" aria-label="Service highlights">
          <div class="stat-item" role="listitem">
            <span class="stat-number">15+</span>
            <span class="stat-label">Years Experience</span>
          </div>
          <div class="stat-item" role="listitem">
            <span class="stat-number">100%</span>
            <span class="stat-label">Licensed & Insured</span>
          </div>
          <div class="stat-item" role="listitem">
            <span class="stat-number">Free</span>
            <span class="stat-label">Estimates</span>
          </div>
        </div>

        <div class="cta_row">
          <a class="btn" href="../index.html#contact">Get Free Estimate in {name}</a>
          <a class="btn ghost" href="tel:{PHONE_TEL}"><svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;vertical-align:middle;"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="section" id="services" aria-labelledby="services-heading">
      <div class="wrap">
        <header class="section-header">
          <h2 id="services-heading">🔧 Home Improvement Services in {name}</h2>
          <p class="muted">We bring full-service residential construction to {name}. Every project is handled by our licensed team with permits, inspections, and quality workmanship guaranteed.</p>
        </header>

        <div class="grid grid-3">
          <div class="card">
            <h3>🍳 Kitchen Remodeling</h3>
            <p>Transform your {name} kitchen with custom cabinets, countertops, tile backsplashes, and modern layouts. We handle everything from design to final inspection.</p>
            <a href="../services/kitchen-remodeling.html" class="btn ghost">Learn More</a>
          </div>
          
          <div class="card">
            <h3>🚿 Bathroom Renovation</h3>
            <p>Custom showers, tile work, vanities, and tub-to-shower conversions. Waterproofing-first approach ensures your {name} bathroom lasts for decades.</p>
            <a href="../services/bathroom-remodeling.html" class="btn ghost">Learn More</a>
          </div>
          
          <div class="card">
            <h3>🏠 Basement Finishing</h3>
            <p>Add living space with a finished basement. We handle framing, drywall, flooring, egress windows, and bathrooms to turn your basement into usable square footage.</p>
            <a href="../services/basement-finishing.html" class="btn ghost">Learn More</a>
          </div>
        </div>

        <div class="service-list-compact">
          <h3>Additional Services We Provide in {name}:</h3>
          <ul class="service-tags">
{service_links}
          </ul>
        </div>
      </div>
    </section>

    <!-- Why Choose Us -->
    <section class="section alt" id="why-us" aria-labelledby="why-heading">
      <div class="wrap">
        <header class="section-header">
          <h2 id="why-heading">✅ Why {name} Homeowners Choose Midwest Flip</h2>
        </header>

        <div class="grid grid-2">
          <div class="benefit-item">
            <h3>🏛️ Licensed Residential Builder</h3>
            <p>We hold a Michigan Residential Builder License, meaning we can legally pull permits and oversee all residential construction in {county} County.</p>
          </div>
          
          <div class="benefit-item">
            <h3>📋 We Handle Permits</h3>
            <p>No need to deal with the building department. We manage permit applications, inspections, and code compliance for your {name} project.</p>
          </div>
          
          <div class="benefit-item">
            <h3>💬 Clear Communication</h3>
            <p>You'll always know what's happening with your project. Regular updates, honest timelines, and responsive answers to your questions.</p>
          </div>
          
          <div class="benefit-item">
            <h3>💰 Fair, Transparent Pricing</h3>
            <p>Detailed estimates with no hidden fees. We explain every line item so you understand exactly where your investment goes.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Badges -->
    <section class="section trust-section" id="trust" aria-labelledby="trust-heading">
      <div class="wrap">
        <h2 id="trust-heading" class="visually-hidden">Why Trust Midwest Flip LLC</h2>
        <div class="trust-badges-grid">
{trust_badges_html}
        </div>
      </div>
    </section>

    <!-- Service Area Info -->
    <section class="section" id="area-info" aria-labelledby="area-heading">
      <div class="wrap">
        <header class="section-header">
          <h2 id="area-heading">📍 About Our Service in {name}</h2>
          <p class="area-tagline">{area_tagline}</p>
        </header>

        <div class="area-details-with-map">
          <div class="area-info-column">
            <div class="area-info-grid">
              <div class="info-item">
                <strong>📍 County:</strong> {county} County, Michigan
              </div>
              <div class="info-item">
                <strong>📮 ZIP Codes Served:</strong> {zip_list}
              </div>
              <div class="info-item">
                <strong>🏠 Home Types:</strong> {home_style}
              </div>
              <div class="info-item">
                <strong>⚡ Response Time:</strong> Same-day estimates available
              </div>
              <div class="info-item">
                <a href="{google_maps_url}" target="_blank" rel="noopener" class="btn ghost btn-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;vertical-align:middle;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                  View {name} on Google Maps
                </a>
              </div>
            </div>
          </div>
          
          <div class="area-map-column">
            <div class="map-container">
              <iframe 
                src="{google_maps_embed}"
                width="100%" 
                height="300" 
                style="border:0; border-radius: 8px;" 
                allowfullscreen="" 
                loading="lazy" 
                referrerpolicy="no-referrer-when-downgrade"
                title="Map of {name}, Michigan">
              </iframe>
            </div>
          </div>
        </div>

        <!-- Nearby Areas -->
        <div class="nearby-areas">
          <h3>We Also Serve Nearby Communities:</h3>
          <ul class="nearby-list">
{nearby_links}
          </ul>
          <p><a href="../service-areas.html">View all 60+ service areas →</a></p>
        </div>
      </div>
    </section>

    <!-- Seasonal Tips -->
    <section class="section alt" id="seasonal" aria-labelledby="seasonal-heading">
      <div class="wrap">
        <div class="seasonal-tip-box">
          <div class="tip-icon">🗓️</div>
          <div class="tip-content">
            <h3 id="seasonal-heading">Seasonal Renovation Tip for {name} Homeowners</h3>
            <p>{seasonal_tip}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="section" id="faq" aria-labelledby="faq-heading">
      <div class="wrap">
        <header class="section-header">
          <h2 id="faq-heading">❓ Frequently Asked Questions About Home Renovation in {name}</h2>
          <p class="muted">Get answers to common questions about working with a licensed contractor in {county} County.</p>
        </header>

        <div class="faq-list">
{faq_html}
        </div>
      </div>
    </section>

    <!-- Our Process -->
    <section class="section alt" id="process" aria-labelledby="process-heading">
      <div class="wrap">
        <header class="section-header">
          <h2 id="process-heading">🔄 Our Simple 4-Step Process</h2>
          <p class="muted">From first call to final walkthrough, here's how we work with {name} homeowners.</p>
        </header>

        <div class="process-steps">
          <div class="process-step">
            <div class="step-number">1</div>
            <h3>Free Consultation</h3>
            <p>We visit your {name} home, discuss your goals, and take measurements. No pressure, no obligation.</p>
          </div>
          
          <div class="process-step">
            <div class="step-number">2</div>
            <h3>Detailed Proposal</h3>
            <p>You receive a clear, itemized estimate with scope, timeline, and payment schedule. We answer all your questions.</p>
          </div>
          
          <div class="process-step">
            <div class="step-number">3</div>
            <h3>Quality Construction</h3>
            <p>Our licensed team handles permits, materials, and daily work. Regular updates keep you informed every step.</p>
          </div>
          
          <div class="process-step">
            <div class="step-number">4</div>
            <h3>Final Walkthrough</h3>
            <p>We inspect everything together, address any concerns, and ensure you're 100% satisfied before we leave.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonial / Social Proof -->
    <section class="section" id="testimonial" aria-labelledby="testimonial-heading">
      <div class="wrap">
        <div class="testimonial-highlight">
          <div class="quote-icon">❝</div>
          <blockquote>
            <p>"Midwest Flip transformed our outdated kitchen into the heart of our home. The team was professional, communicated well, and delivered exactly what they promised. Highly recommend to anyone in Metro Detroit!"</p>
            <footer>
              <cite>— Happy Homeowner, Metro Detroit</cite>
              <div class="star-rating" aria-label="5 out of 5 stars">⭐⭐⭐⭐⭐</div>
            </footer>
          </blockquote>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section cta-section" id="contact-cta" aria-labelledby="cta-heading">
      <div class="wrap">
        <h2 id="cta-heading">Ready to Start Your {name} Home Project?</h2>
        <p>Get a free, no-obligation estimate from our licensed team. We'll visit your {name} home, discuss your vision, and provide a detailed proposal.</p>
        
        <div class="cta-benefits">
          <span class="cta-benefit">✓ Free Estimates</span>
          <span class="cta-benefit">✓ No Obligation</span>
          <span class="cta-benefit">✓ Licensed & Insured</span>
          <span class="cta-benefit">✓ Local to Metro Detroit</span>
        </div>
        
        <div class="cta_row">
          <a class="btn btn-lg" href="../index.html#contact">Request Free Estimate</a>
          <a class="btn ghost btn-lg" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
        </div>
        
        <p class="cta-note">Or email us at <a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
    </section>
  </main>

  <!-- Footer -->
  <footer class="footer" role="contentinfo">
    <div class="wrap">
      <div class="footer-grid">
        <div class="footer-col">
          <h4>Midwest Flip LLC</h4>
          <p>Licensed Residential Builder serving {name} and all of Metro Detroit. Quality craftsmanship, honest pricing, and exceptional service.</p>
          <p><strong>License #:</strong> Michigan Residential Builder</p>
        </div>
        
        <div class="footer-col">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="../services.html">Our Services</a></li>
            <li><a href="../service-areas.html">Service Areas</a></li>
            <li><a href="../index.html#process">Our Process</a></li>
            <li><a href="../blog.html">Blog</a></li>
            <li><a href="../index.html#contact">Contact Us</a></li>
          </ul>
        </div>
        
        <div class="footer-col">
          <h4>Contact Info</h4>
          <ul>
            <li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
            <li>Sun-Thu: 9:00 AM–5:00 PM · Fri: 9:00 AM–12:00 PM · Sat: Closed</li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2025 Midwest Flip LLC. All rights reserved. Licensed &amp; Insured.</p>
      </div>
    </div>
  </footer>

  <script src="../scripts.js" defer></script>
</body>
</html>'''
    
    return html


def get_all_areas() -> List[Dict]:
    """Flatten all areas into a single list."""
    all_areas = []
    for region, areas in METRO_DETROIT_AREAS.items():
        all_areas.extend(areas)
    return all_areas


def generate_single_page(area_name: str) -> Optional[str]:
    """Generate a single page for preview."""
    all_areas = get_all_areas()
    
    # Find the area
    area = None
    for a in all_areas:
        if a["name"].lower() == area_name.lower():
            area = a
            break
    
    if not area:
        print(f"Area '{area_name}' not found!")
        return None
    
    nearby = get_nearby_areas(area, all_areas)
    html = generate_page_html(area, nearby)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Write the file
    slug = slugify(area["name"]) + "-michigan.html"
    filepath = OUTPUT_DIR / slug
    filepath.write_text(html, encoding="utf-8")
    
    print(f"✅ Generated: {filepath}")
    return str(filepath)


def generate_all_pages():
    """Generate all service area pages."""
    all_areas = get_all_areas()
    print(f"Generating {len(all_areas)} service area pages...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    for i, area in enumerate(all_areas, 1):
        nearby = get_nearby_areas(area, all_areas)
        html = generate_page_html(area, nearby)
        
        slug = slugify(area["name"]) + "-michigan.html"
        filepath = OUTPUT_DIR / slug
        filepath.write_text(html, encoding="utf-8")
        
        if i % 50 == 0:
            print(f"Progress: {i}/{len(all_areas)} pages generated...")
    
    print(f"\n✅ Generated {len(all_areas)} service area pages in '{OUTPUT_DIR}/'")
    return len(all_areas)


def list_all_areas():
    """Print all available areas."""
    all_areas = get_all_areas()
    print(f"\n📍 All {len(all_areas)} Metro Detroit Service Areas:\n")
    
    for region, areas in METRO_DETROIT_AREAS.items():
        print(f"\n{region} ({len(areas)} areas):")
        for area in areas:
            badges = []
            if area.get("popular"):
                badges.append("⭐Popular")
            if area.get("luxury"):
                badges.append("💎Luxury")
            if area.get("waterfront"):
                badges.append("🌊Waterfront")
            badge_str = f" [{', '.join(badges)}]" if badges else ""
            print(f"  • {area['name']}{badge_str}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Metro Detroit service area pages")
    parser.add_argument("--preview", action="store_true", help="Generate one sample page (Troy, MI)")
    parser.add_argument("--generate-all", action="store_true", help="Generate all pages")
    parser.add_argument("--city", type=str, help="Generate page for specific city")
    parser.add_argument("--list", action="store_true", help="List all available areas")
    
    args = parser.parse_args()
    
    if args.list:
        list_all_areas()
    elif args.preview:
        generate_single_page("Troy")
    elif args.city:
        generate_single_page(args.city)
    elif args.generate_all:
        generate_all_pages()
    else:
        print("Usage:")
        print("  python generate_service_area_pages.py --preview          # Generate sample (Troy)")
        print("  python generate_service_area_pages.py --city 'Ann Arbor' # Generate specific city")
        print("  python generate_service_area_pages.py --generate-all     # Generate all pages")
        print("  python generate_service_area_pages.py --list             # List all areas")
