"""Textos de ajuda exibidos no Django Admin (PT-BR)."""

from django.utils.translation import gettext_lazy as _

ADMIN_HOME_INTRO = _(
    'Atalhos acima para o dia a dia. Menu lateral agrupa por app — clique para expandir.'
)

APP_SECTIONS = [
    {
        'title': _('Conteúdo'),
        'icon': 'fas fa-newspaper',
        'summary': _('Posts, séries, páginas estáticas e biblioteca de mídia.'),
        'models': [
            (_('Posts / Séries'), _('Artigos EN/PT, capas, SEO e cross-post.')),
            (_('Páginas / Mídia'), _('About, Privacy, Terms e uploads reutilizáveis.')),
            (_('Gerar com IA'), _('Rascunho a partir de brief — revisar antes de publicar.')),
        ],
    },
    {
        'title': _('Distribuição'),
        'icon': 'fas fa-paper-plane',
        'summary': _('Newsletter, curadoria RSS, campanhas e carrosséis Instagram.'),
        'models': [
            (_('Newsletter'), _('Assinantes, lead magnets e campanhas semanais.')),
            (_('Curadoria'), _('Feeds RSS → itens com score IA → draft ou newsletter.')),
            (_('Instagram'), _('Carrosséis 1080×1350 com preview — adaptado do instagen (Go).')),
        ],
    },
    {
        'title': _('Automação'),
        'icon': 'fas fa-gears',
        'summary': _('Jobs do Cloud Scheduler e integrações externas.'),
        'models': [
            (_('Pipeline jobs'), _('Log de curadoria, sync YouTube/GitHub, rascunhos IA.')),
            (_('Integrações'), _('Estado de sync — secrets no GCP Secret Manager.')),
        ],
    },
    {
        'title': _('Site & métricas'),
        'icon': 'fas fa-chart-line',
        'summary': _('Autor, links /links/, redirects, contato e pageviews.'),
        'models': [
            (_('Autor / Links'), _('Bio, avatar e link-in-bio editável.')),
            (_('Analytics'), _('Dashboard + pageviews first-party.')),
            (_('Redirects / Contato'), _('301 do Hugo e caixa de mensagens.')),
        ],
    },
]

MODEL_DESCRIPTIONS = {
    'blog.post': _(
        'Artigos do blog em inglês e português. Publicados aparecem em /posts/ e na home. '
        'Capa (cover) e SEO ficam no fieldset "SEO & Extras".'
    ),
    'blog.category': _('Agrupa posts por tema. Gera listagem em /categories/<slug>/'),
    'blog.tag': _('Tags livres nos posts. Gera listagem em /tags/<slug>/'),
    'blog.author': _('Perfil do autor na home e /about/. Campos goals: uma meta por linha.'),
    'blog.profilelink': _(
        'Links da página /links/ (estilo link-in-bio). '
        'section=card → lista principal; section=social → ícones inferiores.'
    ),
    'blog.comment': _(
        'Comentários nativos Django (não confundir com Giscus/GitHub). '
        'Modere antes de aparecer no site se moderation estiver ativa.'
    ),
    'blog.series': _('Agrupa posts em trilhas (/series/<slug>/). Ordene via inline na série.'),
    'newsletter.subscriber': _(
        'Lista de e-mails do formulário "DevOps & Cloud Newsletter". '
        'Token de unsubscribe é derivado do e-mail (compatível com automação antiga).'
    ),
    'newsletter.leadmagnet': _('Lead magnets para captura de e-mail com página de sucesso.'),
    'curation.feedsource': _(
        'Feeds RSS/Atom monitorados pelo job de curadoria (semanal ou manual). '
        'Desative is_active para pausar uma fonte sem apagar histórico.'
    ),
    'curation.curateditem': _(
        'Links capturados dos feeds com resumo IA e score de relevância. '
        'Fluxo: pending → approved/rejected → published (vira post opcional).'
    ),
    'curation.linksubmission': _('Sugestões de links enviadas pelo formulário /suggest-link/.'),
    'campaigns.newslettercampaign': _(
        'Edição de campanha de e-mail em massa. body_markdown = rascunho semanal da curadoria. '
        'Discord: posta em #drafts-review; botões Aprovar enviam, Rejeitar cancelam.'
    ),
    'content_pipeline.pipelinejob': _(
        'Histórico de execuções automáticas. Tipos: full, curation, newsletter, sync, ai_draft. '
        'Consulte log para debug quando o Scheduler falhar.'
    ),
    'content_pipeline.instagramcarousel': _(
        'Carrossel Instagram 1080×1350 (4:5). Gere slides com IA, preview no admin, exporte PNGs '
        'para media/instagram/&lt;id&gt;/. Assuntos duplicados são bloqueados na geração.'
    ),
    'pages.page': _(
        'Páginas estáticas editáveis. slug=about → /about/. is_published oculta sem apagar. '
        'show_in_footer adiciona link no rodapé do site.'
    ),
    'media_library.mediaasset': _(
        'Arquivos de mídia centralizados. tags separadas por vírgula para busca no admin.'
    ),
    'contact.contactmessage': _(
        'Caixa de entrada do formulário de contato. IP guardado para anti-spam; não editável.'
    ),
    'analytics.pageview': _(
        'Contagem de pageviews first-party. visitor_hash = SHA256(IP+UA), sem cookie. '
        'Não inclui tráfego bloqueado por adblock no script próprio.'
    ),
    'redirects.redirect': _(
        'Redirecionamentos HTTP. is_permanent=True → 301 (SEO). '
        'Use notes para lembrar por que o redirect existe.'
    ),
    'integrations.integrationconfig': _(
        'Metadados de integrações externas. Credenciais reais vêm de env/GCP secrets, não deste JSON.'
    ),
}
