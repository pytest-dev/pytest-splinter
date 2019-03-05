"""Configuration for pytest runner."""
import pytest


pytest_plugins = 'pytester'


@pytest.fixture
def simple_page_content():
    """Return simple page content."""
    return """<html xmlns="http://www.w3.org/1999/xhtml"><head></head>
    <body>
        <div id="content">
            <p>
                Some <strong>text</strong>
            </p>
        </div>
        <textarea id="textarea">area text</textarea>
    </body>
</html>"""


@pytest.fixture
def simple_page(httpserver, browser, simple_page_content):
    """Serve simple html page."""
    httpserver.serve_content(
        simple_page_content, code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)
