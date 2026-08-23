import re
import spacy
from app.models.skill import SkillAlias
import logging

logger = logging.getLogger(__name__)

# Cache aliases to avoid querying DB for every word
# Maps alias string to skill_id (Integer) to avoid SQLAlchemy detached instance errors!
_alias_cache = {}
_initialized = False

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.warning(f"Failed to load spacy model: {e}. Falling back to basic regex.")
    nlp = None

def _load_aliases():
    global _alias_cache, _initialized
    if _initialized:
        return
        
    logger.info("Loading skill aliases into memory cache...")
    aliases = SkillAlias.query.all()
    for alias_obj in aliases:
        # Map lowercased alias to canonical Skill ID
        _alias_cache[alias_obj.alias.lower()] = alias_obj.skill_id
        
    _initialized = True

def normalize_skill_name(raw_name: str) -> int:
    """
    Given a raw extracted skill name, try to normalize it against the KB.
    Returns the skill_id if found, else None.
    """
    _load_aliases()
    
    clean_name = raw_name.strip().lower()
    
    if clean_name in _alias_cache:
        return _alias_cache[clean_name]
        
    stripped_name = clean_name.strip('.,;:-()[]{}')
    if stripped_name in _alias_cache:
        return _alias_cache[stripped_name]
        
    return None

def extract_skills_from_text(text: str) -> list[tuple[int, str]]:
    """
    Extracts skills from a block of text avoiding substring false matches.
    Returns a list of tuples: (skill_id, Matched_Text)
    """
    _load_aliases()
    found_skills = []
    
    if not text:
        return found_skills
        
    all_aliases = sorted(list(_alias_cache.keys()), key=len, reverse=True)
    
    for alias in all_aliases:
        skill_id = _alias_cache[alias]
        
        # Check if we already found this canonical skill to avoid redundant checks
        if any(s[0] == skill_id for s in found_skills):
            continue
            
        escaped_alias = re.escape(alias)
        
        if alias.isalpha() or alias.isalnum():
            pattern = r'\b' + escaped_alias + r'\b'
        else:
            start_bound = r'(?<!\w)' if not alias[0].isalnum() else r'\b'
            end_bound = r'(?!\w)' if not alias[-1].isalnum() else r'\b'
            pattern = start_bound + escaped_alias + end_bound
            
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
        if matches:
            matched_text = matches[0].group(0)
            found_skills.append((skill_id, matched_text))
            
            for match in matches:
                start, end = match.span()
                text = text[:start] + (" " * (end-start)) + text[end:]
                
    return found_skills
