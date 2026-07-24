import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import Page


class _LiveServer(StaticLiveServerTestCase):
    pass


@pytest.fixture(scope="session")
def live_server_url(django_db_setup, django_db_blocker):
    """Servidor Django com static files para testes E2E."""
    django_db_blocker.unblock()
    _LiveServer.setUpClass()
    yield _LiveServer.live_server_url
    _LiveServer.tearDownClass()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, live_server_url):
    return {
        **browser_context_args,
        "base_url": live_server_url,
    }


@pytest.fixture
def page(page: Page) -> Page:
    page.goto("/")
    # Pre-set consent for E2E (avoids overlay click flakiness)
    page.evaluate(
        """() => {
            localStorage.setItem('cookie-consent', 'accepted');
            if (window.MTConsent) window.MTConsent.accept();
        }"""
    )
    return page
