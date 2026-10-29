from backend.app.integrations.confluence_url import extract_page_id_from_query


def test_extract_page_id_from_query_bare_id():
    assert extract_page_id_from_query("1512556436") == "1512556436"


def test_extract_page_id_from_query_url():
    url = "https://confluence.example.com/pages/viewpage.action?pageId=999888777"
    assert extract_page_id_from_query(url) == "999888777"


def test_extract_page_id_from_query_plain_text():
    assert extract_page_id_from_query("Databricks onboarding") is None
