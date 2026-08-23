import json

TEMPLATES_CONFIG = [
    {
        "id": "ats_focused",
        "name": "ATS Focused",
        "description": "Clean, single-column layout optimized for 100% ATS parser readability.",
        "is_ats_friendly": True,
        "font_family": "Helvetica",
        "primary_color": "#111827",
        "accent_color": "#2563eb"
    },
    {
        "id": "classic_professional",
        "name": "Classic Professional",
        "description": "Elegant serif headers and traditional layout preferred for corporate and executive roles.",
        "is_ats_friendly": True,
        "font_family": "Times-Roman",
        "primary_color": "#1f2937",
        "accent_color": "#1e40af"
    },
    {
        "id": "modern_minimal",
        "name": "Modern Minimal",
        "description": "Sleek sans-serif typography with clean accent section dividers.",
        "is_ats_friendly": True,
        "font_family": "Helvetica-Bold",
        "primary_color": "#0f172a",
        "accent_color": "#0d9488"
    },
    {
        "id": "technical",
        "name": "Technical",
        "description": "Structured layout emphasizing core skill matrix and technical achievements.",
        "is_ats_friendly": True,
        "font_family": "Courier",
        "primary_color": "#18181b",
        "accent_color": "#4f46e5"
    }
]
