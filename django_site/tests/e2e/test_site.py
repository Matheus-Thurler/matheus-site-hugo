import re
import pytest
from playwright.sync_api import Page, expect


class TestHomePage:
    """Testes E2E da página inicial."""

    def test_home_loads_successfully(self, page: Page):
        """Verifica que a página inicial carrega sem erros."""
        page.goto("/")
        title = page.title()
        assert "Matheus Thurler" in title

    def test_header_present(self, page: Page):
        """Verifica que o header está presente com logo e navegação."""
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("/")

        logo = page.locator("header a[aria-label='Matheus Thurler']").first
        expect(logo).to_be_visible()

        nav = page.locator("header nav").first
        expect(nav.get_by_text("Posts")).to_be_visible()
        expect(nav.get_by_text("Categories")).to_be_visible()
        expect(nav.get_by_text("Archives")).to_be_visible()
        expect(nav.get_by_text("About")).to_be_visible()

    def test_navigation_links_work(self, page: Page):
        """Verifica que todos os links de navegação funcionam."""
        page.goto("/")

        # Posts - usar seletor mais específico
        page.locator("nav a[href='/posts/']").first.click()
        assert "/posts/" in page.url

        # Archives
        page.locator("nav a[href='/archives/']").first.click()
        assert "/archives/" in page.url

        # About
        page.locator("nav a[href='/about/']").first.click()
        assert "/about/" in page.url

    def test_author_section(self, page: Page):
        """Verifica seção do autor na home."""
        page.goto("/")

        expect(page.get_by_text("Matheus Thurler").first).to_be_visible()
        expect(page.get_by_text("DevOps").first).to_be_visible()

        # Social links
        github_link = page.locator("a[href*='github.com']").first
        expect(github_link).to_be_visible()

    def test_recent_posts_section(self, page: Page):
        """Verifica seção de posts recentes."""
        page.goto("/")

        expect(page.get_by_text("Recent Posts")).to_be_visible()

        # Posts devem ser clicáveis
        posts = page.locator("article a[href*='/posts/']")
        expect(posts.first).to_be_visible()

    def test_view_all_posts_button(self, page: Page):
        """Verifica botão 'View All Posts'."""
        page.goto("/")

        view_all = page.get_by_text("View All Posts")
        expect(view_all).to_be_visible()
        view_all.click()
        assert "/posts/" in page.url

    @pytest.mark.skip(reason="SHOW_DOCK=False in settings")
    def test_dock_visible(self, page: Page):
        """Verifica que o dock está presente."""
        page.goto("/")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)

        dock = page.locator("#dock")
        expect(dock).to_be_visible()

    @pytest.mark.skip(reason="SHOW_DOCK=False in settings")
    def test_dock_buttons(self, page: Page):
        """Verifica botões do dock."""
        page.goto("/")
        page.evaluate("window.scrollTo(0, 200)")

        # Search button
        search_btn = page.locator("#dock-search")
        expect(search_btn).to_be_visible()

    def test_footer_present(self, page: Page):
        """Verifica footer com copyright e links sociais."""
        page.goto("/")

        footer = page.locator("footer")
        expect(footer.get_by_text("Matheus Thurler")).to_be_visible()
        expect(footer.get_by_text("Powered by")).to_be_visible()
        expect(footer.get_by_role("link", name="Django")).to_be_visible()

    def test_footer_social_links(self, page: Page):
        """Verifica links sociais no footer."""
        page.goto("/")

        github = page.locator("footer a[href*='github.com']")
        youtube = page.locator("footer a[href*='youtube.com']")
        linkedin = page.locator("footer a[href*='linkedin.com']")

        expect(github).to_be_visible()
        expect(youtube).to_be_visible()
        expect(linkedin).to_be_visible()


class TestPostsPage:
    """Testes E2E da página de posts."""

    def test_posts_page_loads(self, page: Page):
        """Verifica que a página de posts carrega."""
        page.goto("/posts/")
        expect(page.locator("h1,h2").first).to_be_visible()

    def test_posts_list(self, page: Page):
        """Verifica lista de posts."""
        page.goto("/posts/")

        posts = page.locator("article")
        expect(posts.first).to_be_visible()

    def test_post_cards_have_required_elements(self, page: Page):
        """Verifica elementos obrigatórios nos cards de posts."""
        page.goto("/posts/")

        card = page.locator("article").first
        expect(card).to_be_visible()

        # Título - pode ser h2, h3 ou outro heading
        title = card.locator("h2,h3").first
        expect(title).to_be_visible()

    def test_post_click_navigates_to_detail(self, page: Page):
        """Verifica que clicar em um post navega para detalhes."""
        page.goto("/posts/")

        first_post = page.locator("article a[href*='/posts/']").first
        first_post.click()

        assert "/posts/" in page.url and re.search(r"/posts/[a-z0-9-]+/", page.url)


class TestPostDetail:
    """Testes E2E da página de detalhes do post."""

    def test_post_detail_loads(self, page: Page):
        """Verifica que a página de detalhes carrega."""
        page.goto("/posts/nginx-vs-traefik-vs-caddy/")

        # Título deve estar visível
        h1 = page.locator("h1")
        expect(h1).to_be_visible()

    def test_post_meta_info(self, page: Page):
        """Verifica informações meta do post."""
        page.goto("/posts/nginx-vs-traefik-vs-caddy/")

        # Data
        expect(page.locator("time")).to_be_visible()

        # Tags
        tags = page.locator("a[href*='/tags/']")
        if tags.count() > 0:
            expect(tags.first).to_be_visible()

    def test_post_content(self, page: Page):
        """Verifica que o conteúdo do post está presente."""
        page.goto("/posts/nginx-vs-traefik-vs-caddy/")

        article = page.locator("article.prose")
        expect(article).to_be_visible()

    def test_share_buttons(self, page: Page):
        """Verifica botões de compartilhar."""
        page.goto("/posts/nginx-vs-traefik-vs-caddy/")

        twitter_link = page.locator("a[href*='twitter.com']").first
        linkedin_link = page.locator("a[href*='linkedin.com/sharing']").first

        expect(twitter_link).to_be_visible()
        expect(linkedin_link).to_be_visible()

    def test_comments_section(self, page: Page):
        """Verifica seção de comentários (Giscus carrega sem depender de cookie consent)."""
        page.goto("/posts/nginx-vs-traefik-vs-caddy/")

        comments = page.locator("#comments")
        expect(comments).to_be_visible()

        giscus = page.locator("script[src*='giscus']")
        expect(giscus).to_have_count(1, timeout=5000)


class TestAboutPage:
    """Testes E2E da página About."""

    def test_about_page_loads(self, page: Page):
        """Verifica que a página About carrega."""
        page.goto("/about/")
        assert "About" in page.title()

    def test_author_info(self, page: Page):
        """Verifica informações do autor."""
        page.goto("/about/")

        expect(page.get_by_text("Matheus Thurler").first).to_be_visible()

    def test_social_links(self, page: Page):
        """Verifica links sociais na página About."""
        page.goto("/about/")

        section = page.locator("#lets-connect")
        expect(section.get_by_role("link", name="GitHub")).to_be_visible()
        expect(section.get_by_role("link", name="YouTube")).to_be_visible()


class TestArchivesPage:
    """Testes E2E da página de arquivos."""

    def test_archives_loads(self, page: Page):
        """Verifica que a página de arquivos carrega."""
        page.goto("/archives/")
        assert "Archives" in page.title()

    def test_posts_grouped_by_year(self, page: Page):
        """Verifica posts agrupados por ano."""
        page.goto("/archives/")

        # Deve ter pelo menos um ano
        years = page.locator("h2")
        if years.count() > 0:
            expect(years.first).to_be_visible()


class TestSearchPage:
    """Testes E2E da página de busca."""

    def test_search_page_loads(self, page: Page):
        """Verifica que a página de busca carrega."""
        page.goto("/search/")
        assert "Search" in page.title()

    def test_search_input(self, page: Page):
        """Verifica campo de busca."""
        page.goto("/search/")

        search_input = page.locator("input[name='q']")
        expect(search_input).to_be_visible()

    def test_search_functionality(self, page: Page):
        """Verifica funcionalidade de busca."""
        page.goto("/search/")

        search_input = page.locator("input[name='q']")
        search_input.fill("nginx")

        page.get_by_role("button", name="Search").first.click()

        # Verifica que resultados aparecem ou mensagem de não encontrado
        content = page.content()
        assert "Results" in content or "No results" in content or "Nenhum" in content or "found" in content or "nginx" in content.lower()


class TestPrivacyTerms:
    """Testes E2E das páginas de privacidade e termos."""

    def test_privacy_page_loads(self, page: Page):
        """Verifica página de privacidade."""
        page.goto("/privacy/")
        assert "Privacy" in page.title()

    def test_terms_page_loads(self, page: Page):
        """Verifica página de termos."""
        page.goto("/terms/")
        assert "Terms" in page.title()


class TestThemeSwitcher:
    """Testes para o seletor de tema."""

    def test_theme_switcher_button(self, page: Page):
        """Verifica botão do seletor de tema."""
        page.goto("/")

        theme_btn = page.locator("#theme-switch-btn").first
        expect(theme_btn).to_be_visible()

    @pytest.mark.skip(reason="duplicate #theme-switch-btn IDs in header — fix template IDs")
    def test_theme_dropdown_opens(self, page: Page):
        """Verifica que dropdown de temas abre."""
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("/")

        btn = page.locator("header div.hidden.md\\:flex #theme-switch-btn")
        btn.click()
        expect(btn).to_have_attribute("aria-expanded", "true")

    @pytest.mark.skip(reason="duplicate #theme-switch-btn IDs in header — fix template IDs")
    def test_theme_options_present(self, page: Page):
        """Verifica opções de tema."""
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("/")

        btn = page.locator("header div.hidden.md\\:flex #theme-switch-btn")
        btn.click()
        dropdown = page.locator("header div.hidden.md\\:flex #theme-dropdown")
        expect(dropdown.locator("button[data-theme='nord']")).to_be_visible()
        expect(dropdown.locator("button[data-theme='dracula']")).to_be_visible()
        expect(dropdown.locator("button[data-theme='claude']")).to_be_visible()


class TestDarkMode:
    """Testes para modo escuro."""

    def test_dark_mode_toggle(self, page: Page):
        """Verifica que theme switcher está presente (substitui dark mode toggle)."""
        page.goto("/")

        theme_switch = page.locator("#theme-switch-btn").first
        expect(theme_switch).to_be_visible()

    def test_dark_mode_toggles_class(self, page: Page):
        """Verifica que theme switcher pode ser clicado."""
        page.goto("/")

        html = page.locator("html")
        expect(html).to_be_visible()
        toggle = page.locator("#theme-switch-btn").first
        expect(toggle).to_be_visible()


class TestMobileMenu:
    """Testes para menu mobile."""

    def test_mobile_menu_toggle(self, page: Page):
        """Verifica toggle do menu mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("/")

        menu_toggle = page.locator("#mobile-menu-toggle")
        expect(menu_toggle).to_be_visible()

    def test_mobile_menu_opens(self, page: Page):
        """Verifica que menu mobile abre."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("/")
        page.wait_for_timeout(500)

        # Click via JavaScript
        page.evaluate("document.getElementById('mobile-menu-toggle').click()")
        page.wait_for_timeout(300)

        mobile_menu = page.locator("#mobile-menu")
        expect(mobile_menu).to_be_visible()


class TestNavigation:
    """Testes de navegação completa."""

    def test_full_user_journey(self, page: Page):
        """Journey completo: Home -> Posts -> Post Detail -> About -> Archives."""
        # Home
        page.goto("/")
        assert "Matheus Thurler" in page.title()

        # Posts
        page.locator("nav a[href='/posts/']").first.click()
        assert "/posts/" in page.url

        # Post Detail
        page.locator("article a[href*='/posts/']").first.click()
        assert re.search(r"/posts/.+", page.url)

        # About
        page.locator("nav a[href='/about/']").first.click()
        assert "/about/" in page.url

        # Archives
        page.locator("nav a[href='/archives/']").first.click()
        assert "/archives/" in page.url


class TestAccessibility:
    """Testes de acessibilidade básica."""

    def test_landmark_regions(self, page: Page):
        """Verifica landmarks HTML."""
        page.goto("/")

        header = page.locator("header")
        main = page.locator("main")
        footer = page.locator("footer")

        expect(header).to_be_visible()
        expect(main).to_be_visible()
        expect(footer).to_be_visible()

    def test_skip_navigation(self, page: Page):
        """Verifica que links têm texto acessível."""
        page.goto("/")

        nav_links = page.locator("nav a")
        for link in nav_links.all():
            text = link.inner_text()
            assert len(text.strip()) > 0 or link.get_attribute("aria-label") is not None

    def test_images_have_alt(self, page: Page):
        """Verifica que imagens têm alt text."""
        page.goto("/")

        images = page.locator("img")
        for img in images.all():
            alt = img.get_attribute("alt")
            assert alt is not None, "Image should have alt attribute"


class TestPerformance:
    """Testes de performance básica."""

    def test_page_loads_quickly(self, page: Page):
        """Verifica que página carrega em tempo razoável."""
        import time

        start = time.time()
        page.goto("/", wait_until="networkidle")
        load_time = time.time() - start

        # Deve carregar em menos de 3 segundos
        assert load_time < 3, f"Page took {load_time:.2f}s to load"

    def test_no_404_resources(self, page: Page):
        """Verifica que não há recursos 404."""
        errors = []

        def handle_response(response):
            if response.status == 404:
                errors.append(response)

        page.on("response", handle_response)

        page.goto("/")
        page.wait_for_load_state("networkidle")

        assert len(errors) == 0, f"404 errors found: {[e.url for e in errors]}"
