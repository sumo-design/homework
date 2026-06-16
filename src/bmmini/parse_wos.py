import re
from pathlib import Path
import pandas as pd
from .utils import clean_author_name, clean_affiliation, parse_cited_refs

def parse_wos_file(file_path):
    """Parse a single WoS tagged export file into a list of record dicts.
    Handles multi-line fields.
    """
    records = []
    current = {}
    current_tag = ''
    with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n\r')
            if not line.strip():
                continue
            # A new tag starts with 2 characters at the beginning of the line
            tag_match = re.match(r'^([A-Z][A-Z0-9])(?:\s|$)', line)
            if tag_match:
                tag = tag_match.group(1)
                rest = line[tag_match.end():]
                value = rest.strip()
                if tag == 'ER':
                    if current:
                        records.append({k: '; '.join(v) for k, v in current.items()})
                    current = {}
                    current_tag = ''
                    continue
                if tag not in current:
                    current[tag] = []
                current[tag].append(value)
                current_tag = tag
            elif current_tag and line.startswith('   '):
                value = line.strip()
                if current_tag in current:
                    current[current_tag].append(value)
    if current:
        records.append({k: '; '.join(v) for k, v in current.items()})
    return records

def parse_wos_dir(dir_path):
    """Parse all WoS .txt files in a directory and return combined records."""
    dir_path = Path(dir_path)
    all_records = []
    for txt_file in sorted(dir_path.glob('*.txt')):
        all_records.extend(parse_wos_file(txt_file))
    return all_records

def normalize_wos_records(records):
    """Normalize raw WoS records into works, references, authors, and keywords.
    Ensures correct schema.
    """
    works_list = []
    refs_list = []
    authors_list = []
    keywords_list = []

    for rec in records:
        ut = rec.get('UT', '').strip()
        if not ut:
            continue
        work_id = ut

        title = rec.get('TI', '').strip()
        doi = rec.get('DI', '').strip()
        year_str = rec.get('PY', '').strip()
        year = int(year_str) if year_str.isdigit() else None
        publication_date = rec.get('PD', '').strip()
        venue = rec.get('SO', '').strip()
        cited_by_count = int(rec['TC']) if rec.get('TC', '').strip().isdigit() else 0
        n_references = int(rec['NR']) if rec.get('NR', '').strip().isdigit() else 0
        abstract = rec.get('AB', '').strip()

        works_list.append({
            'work_id': work_id,
            'title': title,
            'doi': doi,
            'year': year,
            'publication_date': publication_date,
            'venue': venue,
            'cited_by_count': cited_by_count,
            'n_references': n_references,
            'abstract': abstract
        })

        # References (CR)
        cr_text = rec.get('CR', '')
        if cr_text:
            for cr_line in cr_text.split('; '):
                cr_line = cr_line.strip()
                if cr_line:
                    ref_id = parse_cited_refs(cr_line)
                    if ref_id:
                        refs_list.append({'work_id': work_id, 'reference_id': ref_id})

        # Affiliations lookup from C1
        c1_text = rec.get('C1', '')
        author_aff_map = {}
        if c1_text:
            # Parse patterns like: [Wang, Hao; Hu, Jianqi] Koc Univ, Dept...
            matches = re.findall(r'\[(.*?)\]\s*([^\[\n;]+)', c1_text)
            for names_part, aff_part in matches:
                clean_aff = clean_affiliation(aff_part)
                for name in names_part.split(';'):
                    name_clean = clean_author_name(name.strip())
                    if name_clean:
                        author_aff_map[name_clean] = clean_aff

            # If C1 has no brackets, try parsing without brackets
            if not matches:
                clean_aff = clean_affiliation(c1_text.split(';')[0])
                author_aff_map['__default__'] = clean_aff

        # Authors (AU)
        au_text = rec.get('AU', '')
        if au_text:
            for position, au_name in enumerate(au_text.split('; '), start=1):
                au_name = au_name.strip()
                if au_name:
                    name_clean = clean_author_name(au_name)
                    # Get institution
                    inst = author_aff_map.get(name_clean, author_aff_map.get('__default__', ''))
                    authors_list.append({
                        'work_id': work_id,
                        'author_id': '',
                        'author_name': name_clean,
                        'author_position': position,
                        'institutions': inst
                    })

        # Keywords (DE / ID)
        kw_set = set()
        de_text = rec.get('DE', '')
        if de_text:
            for kw in de_text.split('; '):
                kw = kw.strip().lower()
                if len(kw) > 2:
                    kw_set.add(kw)
        id_text = rec.get('ID', '')
        if id_text:
            for kw in id_text.split('; '):
                kw = kw.strip().lower()
                if len(kw) > 2:
                    kw_set.add(kw)
        for kw in kw_set:
            keywords_list.append({
                'work_id': work_id,
                'keyword': kw
            })

    works_df = pd.DataFrame(works_list).drop_duplicates('work_id') if works_list else pd.DataFrame(
        columns=['work_id', 'title', 'doi', 'year', 'publication_date', 'venue', 'cited_by_count', 'n_references', 'abstract']
    )
    refs_df = pd.DataFrame(refs_list).drop_duplicates() if refs_list else pd.DataFrame(
        columns=['work_id', 'reference_id']
    )
    authors_df = pd.DataFrame(authors_list).drop_duplicates() if authors_list else pd.DataFrame(
        columns=['work_id', 'author_id', 'author_name', 'author_position', 'institutions']
    )
    keywords_df = pd.DataFrame(keywords_list).drop_duplicates() if keywords_list else pd.DataFrame(
        columns=['work_id', 'keyword']
    )

    return works_df, refs_df, authors_df, keywords_df

def save_normalized_wos(records, processed_dir):
    """Normalize WoS records and save standard processed CSV files."""
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    works, refs, authors, keywords = normalize_wos_records(records)
    
    paths = {
        'works': processed_dir / 'works_clean.csv',
        'references': processed_dir / 'work_references.csv',
        'authors': processed_dir / 'work_authors.csv',
        'keywords': processed_dir / 'work_keywords.csv'
    }
    
    works.to_csv(paths['works'], index=False, encoding='utf-8-sig')
    refs.to_csv(paths['references'], index=False, encoding='utf-8-sig')
    authors.to_csv(paths['authors'], index=False, encoding='utf-8-sig')
    keywords.to_csv(paths['keywords'], index=False, encoding='utf-8-sig')
    
    print(f"Saved normalized tables:")
    print(f"  - Works: {len(works)} records")
    print(f"  - References: {len(refs)} citations")
    print(f"  - Authors: {len(authors)} authorship rows")
    print(f"  - Keywords: {len(keywords)} keyword mappings")
    
    return paths
