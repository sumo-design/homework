import re
import yaml
from pathlib import Path

def load_config(config_path="config/query.yaml"):
    """Load configuration from a YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dirs(config):
    """Ensure all required output directories exist."""
    Path(config['data']['processed_dir']).mkdir(parents=True, exist_ok=True)
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/html").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)
    Path("paper").mkdir(parents=True, exist_ok=True)
    Path("presentation").mkdir(parents=True, exist_ok=True)
    Path("reflection").mkdir(parents=True, exist_ok=True)

def clean_author_name(author_str):
    """Clean and normalize author name to 'LastName, FirstInitial.' format."""
    if not isinstance(author_str, str) or not author_str.strip():
        return ""
    parts = author_str.strip().split(',')
    if len(parts) >= 1:
        last = parts[0].strip()
        first_init = ""
        if len(parts) > 1:
            first_part = parts[1].strip()
            if first_part:
                first_init = first_part[0]
        return f"{last}, {first_init}." if first_init else last
    return author_str

def clean_affiliation(aff_str):
    """Normalize and map common institution names to their standard aliases."""
    if not isinstance(aff_str, str) or not aff_str.strip():
        return ""
    aff_str = aff_str.strip()
    mapping = {
        "Beijing Informat Sci & Technol Univ": "Beijing Information S&T University",
        "Beijing Information Science & Technology University": "Beijing Information S&T University",
        "MIT": "Massachusetts Institute of Technology",
        "Mass. Inst. Tech.": "Massachusetts Institute of Technology",
        "Tsinghua Univ": "Tsinghua University",
        "Peking Univ": "Peking University",
        "Sorbonne Univ": "Sorbonne University",
        "Ecole Normale Super": "Ecole Normale Superieure",
        "Swiss Fed Inst Technol": "ETH Zurich",
        "ETH Zurich": "ETH Zurich",
        "NTT Res Inc": "NTT Research Inc",
        "NTT Research": "NTT Research Inc",
        "Univ Trento": "University of Trento",
        "Koc Univ": "Koc University"
    }
    for alias, std in mapping.items():
        if alias in aff_str:
            return std
    return aff_str

def parse_cited_refs(ref_str):
    """Normalize a single CR reference into a stable, readable citation identifier.
    Format: Author_Year_Journal.
    """
    if not isinstance(ref_str, str) or not ref_str.strip():
        return None
    parts = [p.strip() for p in ref_str.split(',')]
    if len(parts) >= 3:
        author = parts[0].strip()
        # Clean author name in reference (e.g. remove initials to group references easily)
        author_clean = author.split(' ')[0]
        year = parts[1].strip()
        # Find 4 digit year
        year_match = re.search(r'\d{4}', year)
        if year_match:
            year = year_match.group(0)
        source = parts[2].strip().upper()
        # Keep source short and clean
        source_clean = source.replace('.', '').replace('AND', '&')
        return f"{author_clean}_{year}_{source_clean}"
    return ref_str.strip()
