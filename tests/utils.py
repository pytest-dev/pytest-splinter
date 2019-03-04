def assert_valid_html_screenshot_content(content):
    """Make sure content fetched from html screenshoting looks correct."""
    assert content.startswith('<html xmlns="http://www.w3.org/1999/xhtml">')
    assert '<div id="content">' in content
    assert '<strong>text</strong>' in content
    assert content.endswith('</html>')
