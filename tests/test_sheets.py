from newyearscards.sheets import extract_ids


def test_extract_ids_fragment():
    url = "https://docs.google.com/spreadsheets/d/abc123-DEF_456/edit#gid=987654321"
    sid, gid = extract_ids(url)
    assert sid == "abc123-DEF_456"
    assert gid == "987654321"


def test_extract_ids_query():
    url = "https://docs.google.com/spreadsheets/d/someId/export?format=csv&gid=42"
    sid, gid = extract_ids(url)
    assert sid == "someId"
    assert gid == "42"


def test_extract_ids_default_gid():
    url = "https://docs.google.com/spreadsheets/d/onlyId/edit"
    sid, gid = extract_ids(url)
    assert sid == "onlyId"
    assert gid == "0"

