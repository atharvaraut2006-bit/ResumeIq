from app.utils.validators import allowed_file

def test_allowed_file():
    assert allowed_file("resume.pdf") == True
    assert allowed_file("RESUME.PDF") == True
    assert allowed_file("resume.doc") == False
    assert allowed_file("resume") == False
