from app.models.job_match import JobMatch, SkillMatch
from app.services.scoring_service import calculate_compatibility_score
from app.services.skill_gap_service import analyze_skill_gaps

class MockSkill:
    def __init__(self, name, category):
        self.canonical_name = name
        self.category = category

class MockJob:
    def __init__(self):
        self.soft_skills = []

def test_scoring_logic(monkeypatch):
    # Setup mock data
    job_match = JobMatch(id=1)
    job_match.job = MockJob()
    
    skill_matches = [
        SkillMatch(job_match_id=1, match_status='matched', requirement_type='required', skill=MockSkill("Python", "Programming")),
        SkillMatch(job_match_id=1, match_status='matched', requirement_type='required', skill=MockSkill("SQL", "DB")),
        SkillMatch(job_match_id=1, match_status='missing', requirement_type='required', skill=MockSkill("Docker", "DevOps")),
        
        SkillMatch(job_match_id=1, match_status='matched', requirement_type='preferred', skill=MockSkill("AWS", "Cloud")),
        SkillMatch(job_match_id=1, match_status='missing', requirement_type='preferred', skill=MockSkill("Azure", "Cloud")),
    ]
    
    # Mock query.get and query.filter_by
    monkeypatch.setattr("app.models.job_match.JobMatch.query", type('obj', (object,), {'get': lambda id: job_match}))
    monkeypatch.setattr("app.models.job_match.SkillMatch.query", type('obj', (object,), {'filter_by': lambda **kwargs: type('obj', (object,), {'all': lambda: skill_matches})()}))
    
    # Mock db.session.commit
    monkeypatch.setattr("app.db.session.commit", lambda: None)

    # Test scoring
    updated_match = calculate_compatibility_score(1)
    
    # 2 out of 3 required matched -> 66.66%
    assert round(updated_match.required_skills_score) == 67
    
    # 1 out of 2 preferred matched -> 50.0%
    assert updated_match.preferred_skills_score == 50.0
    
    # Overall score = (66.66 * 0.6) + (50 * 0.2) + (100 * 0.1) + (100 * 0.05) + (100 * 0.05)
    # 40 + 10 + 10 + 5 + 5 = 70.0
    assert updated_match.overall_score == 70.0

def test_skill_gap_analysis(monkeypatch):
    # Setup mock data
    job_match = JobMatch(id=1)
    skill_matches = [
        SkillMatch(job_match_id=1, match_status='matched', requirement_type='required', match_confidence=0.99, skill=MockSkill("Python", "Programming")),
        SkillMatch(job_match_id=1, match_status='missing', requirement_type='required', match_confidence=0.0, skill=MockSkill("Docker", "DevOps")),
        SkillMatch(job_match_id=1, match_status='missing', requirement_type='preferred', match_confidence=0.0, skill=MockSkill("AWS", "Cloud")),
    ]
    
    monkeypatch.setattr("app.models.job_match.SkillMatch.query", type('obj', (object,), {'filter_by': lambda **kwargs: type('obj', (object,), {'all': lambda: skill_matches})()}))
    
    gaps = analyze_skill_gaps(1)
    
    assert len(gaps['strengths']) == 1
    assert gaps['strengths'][0]['name'] == "Python"
    
    assert len(gaps['missing_required']) == 1
    assert gaps['missing_required'][0]['name'] == "Docker"
    
    assert len(gaps['missing_preferred']) == 1
    assert gaps['missing_preferred'][0]['name'] == "AWS"
