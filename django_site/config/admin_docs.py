"""Textos de ajuda exibidos no Django Admin (PT-BR)."""

from django.utils.translation import gettext_lazy as _

# Visão geral na página inicial do /admin/
ADMIN_HOME_INTRO = _(
    'Painel da plataforma do blog. Cada seção abaixo explica o que faz e quando usar.'
)

APP_SECTIONS = [
    {
        'title': _('Blog'),
        'icon': 'fas fa-newspaper',
        'summary': _(
            'Conteúdo público do site: posts, categorias, tags, autor e moderação de comentários nativos.'
        ),
        'models': [
            (_('Posts'), _('Artigos EN/PT publicados em /posts/. Use status "published" e data de publicação.')),
            (_('Gerar post com IA'), _('Rascunho via Gemini a partir de um brief — revisar antes de publicar.')),
            (_('Categorias / Tags'), _('Organização e URLs de arquivo (/categories/, /tags/).')),
            (_('Autor'), _('Perfil exibido na home e página About (bio, links sociais, avatar).')),
            (_('Comentários'), _('Comentários Django no post (alternativa ao Giscus). Aprove ou rejeite aqui.')),
        ],
    },
    {
        'title': _('Newsletter'),
        'icon': 'fas fa-envelope',
        'summary': _(
            'Inscrições do formulário da home. Substitui a Cloud Function subscribe do content-automation.'
        ),
        'models': [
            (_('Assinantes'), _('E-mails ativos/inativos, idioma e export CSV. Desative quem pediu unsubscribe.')),
        ],
    },
    {
        'title': _('Curadoria'),
        'icon': 'fas fa-rss',
        'summary': _(
            'Lê feeds RSS configurados, resume com IA e guarda links candidatos a post ou newsletter.'
        ),
        'models': [
            (_('Fontes RSS'), _('URLs de blogs/feeds a monitorar. max_items limita itens por execução.')),
            (_('Itens curados'), _('Links capturados com score e resumo IA — aprove, rejeite ou publique.')),
        ],
    },
    {
        'title': _('Campanhas'),
        'icon': 'fas fa-paper-plane',
        'summary': _(
            'Newsletter semanal em massa. Pode enviar direto ou pedir revisão no Discord antes.'
        ),
        'models': [
            (_('Campanhas'), _(
                'Rascunho PT/EN → ação "Post to Discord for review" ou "Send campaign now". '
                'Status pending_review aguarda botões Aprovar/Rejeitar no Discord.'
            )),
        ],
    },
    {
        'title': _('Pipeline'),
        'icon': 'fas fa-gears',
        'summary': _(
            'Log de jobs automáticos (Cloud Scheduler): curadoria, newsletter, sync e rascunhos IA.'
        ),
        'models': [
            (_('Jobs'), _('Somente leitura — veja se o cron rodou, erros e duração. Disparado via HTTP interno.')),
        ],
    },
    {
        'title': _('Páginas'),
        'icon': 'fas fa-file-alt',
        'summary': _('Páginas estáticas CMS: About, Privacy, Terms, Links — conteúdo EN/PT editável.'),
        'models': [
            (_('Páginas'), _('slug define a URL (/about/, /privacy/). show_in_footer aparece no rodapé.')),
        ],
    },
    {
        'title': _('Mídia'),
        'icon': 'fas fa-images',
        'summary': _('Biblioteca central de imagens e arquivos reutilizáveis (capas, diagramas, galeria).'),
        'models': [
            (_('Biblioteca'), _('Upload com alt, caption e tags. Referencie nos posts ou páginas.')),
        ],
    },
    {
        'title': _('Contato'),
        'icon': 'fas fa-inbox',
        'summary': _('Mensagens enviadas pelo formulário de contato (se habilitado no site).'),
        'models': [
            (_('Mensagens'), _('Somente leitura — marque como lida após responder por e-mail.')),
        ],
    },
    {
        'title': _('Analytics'),
        'icon': 'fas fa-chart-line',
        'summary': _(
            'Pageviews próprios (sem cookies Google). Registrados por analytics-track.js após consent opcional.'
        ),
        'models': [
            (_('Visualizações'), _('Path, referrer e hash anônimo do visitante. Top páginas no topo da lista.')),
        ],
    },
    {
        'title': _('Redirects'),
        'icon': 'fas fa-route',
        'summary': _('Redirecionamentos 301/302 — URLs antigas do Hugo ou links que mudaram.'),
        'models': [
            (_('Redirects'), _('old_path → new_path. Middleware aplica antes da view Django.')),
        ],
    },
    {
        'title': _('Integrações'),
        'icon': 'fas fa-plug',
        'summary': _('Estado de sync com YouTube, GitHub e Discord (config JSON + último resultado).'),
        'models': [
            (_('Integrações'), _('Ative/desative e veja last_sync_at. Secrets ficam no GCP Secret Manager.')),
        ],
    },
]

# Descrição no topo de cada changelist / change form (chave: app_label.model_name)
MODEL_DESCRIPTIONS = {
    'blog.post': _(
        'Artigos do blog em inglês e português. Publicados aparecem em /posts/ e na home. '
        'Capa (cover) e SEO ficam no fieldset "SEO & Extras".'
    ),
    'blog.category': _('Agrupa posts por tema. Gera listagem em /categories/<slug>/'),
    'blog.tag': _('Tags livres nos posts. Gera listagem em /tags/<slug>/'),
    'blog.author': _('Perfil do autor na home e /about/. Campos goals: uma meta por linha.'),
    'blog.comment': _(
        'Comentários nativos Django (não confundir com Giscus/GitHub). '
        'Modere antes de aparecer no site se moderation estiver ativa.'
    ),
    'newsletter.subscriber': _(
        'Lista de e-mails do formulário "DevOps & Cloud Newsletter". '
        'Token de unsubscribe é derivado do e-mail (compatível com automação antiga).'
    ),
    'curation.feedsource': _(
        'Feeds RSS/Atom monitorados pelo job de curadoria (semanal ou manual). '
        'Desative is_active para pausar uma fonte sem apagar histórico.'
    ),
    'curation.curateditem': _(
        'Links capturados dos feeds com resumo IA e score de relevância. '
        'Fluxo: pending → approved/rejected → published (vira post opcional).'
    ),
    'campaigns.newslettercampaign': _(
        'Edição de campanha de e-mail em massa. body_markdown = rascunho semanal da curadoria. '
        'Discord: posta em #drafts-review; botões Aprovar enviam, Rejeitar cancelam.'
    ),
    'content_pipeline.pipelinejob': _(
        'Histórico de execuções automáticas. Tipos: full, curation, newsletter, sync, ai_draft. '
        'Consulte log para debug quando o Scheduler falhar.'
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
