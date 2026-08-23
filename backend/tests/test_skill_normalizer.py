from app.services.skill_normalizer import normalize_skill_name, extract_skills_from_text
from app.models.skill import Skill
from unittest.mock import patch, MagicMock

@patch('app.services.skill_normalizer._alias_cache', {
    'javascript': 1,
    'js': 1,
    'python': 2,
    'c': 3,
    'c++': 4
})
@patch('app.services.skill_normalizer._initialized', True)
def test_extract_skills_from_text():
    # Should find Python (2) and JavaScript (1) but NOT C (3) or C++ (4)
    text1 = "I have experience with Python and JS frameworks."
    skills1 = extract_skills_from_text(text1)
    skill_ids1 = [s[0] for s in skills1]
    
    assert 2 in skill_ids1
    assert 1 in skill_ids1
    assert 3 not in skill_ids1
    
    # Boundary test for 'C' and 'C++'
    text2 = "Developed in C++ and a little bit of C. Also used C#."
    skills2 = extract_skills_from_text(text2)
    skill_ids2 = [s[0] for s in skills2]
    
    assert 4 in skill_ids2
    assert 3 in skill_ids2
