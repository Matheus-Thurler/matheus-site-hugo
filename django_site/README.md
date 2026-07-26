# Matheus Thurler Blog — Django

Blog pessoal em Django 6 — DevOps, GCP, Kubernetes, CI/CD e AI.

## Stack

- Django 6 + **SQLite** (dev) / **PostgreSQL** (prod/Docker)
- **uv** para dependências
- **Gunicorn** + **WhiteNoise** (static comprimido)
- **Docker Compose** com profiles SQLite e Postgres
- pytest + Playwright (E2E)

## Desenvolvimento local (uv)

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver 8000
```

## Docker

```bash
cp .env.example .env   # ajuste DJANGO_SECRET_KEY

# SQLite (default — simples, dev/local)
docker compose up --build

# PostgreSQL (prod-like)
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build
```

App em http://localhost:8000

### Volumes

| Volume | Uso |
|--------|-----|
| `sqlite_data` | Banco SQLite em `/app/data/db.sqlite3` |
| `pg_data` | PostgreSQL (profile postgres) |
| `media_data` | Uploads (`/app/media`) |

## Testes

```bash
uv sync --group dev
uv run playwright install chromium
uv run pytest
```

## Performance / LGPD

- GA, AdSense e Giscus carregam **somente após consent** (`static/js/consent.js`)
- Cookie banner é **overlay fixo** — não empurra layout (CLS)
- `robots.txt` dinâmico com Sitemap absoluto

## Conteúdo

Posts markdown: `content/posts/` — sync via `uv run python manage.py update_hugo_posts`

## Newsletter

App Django unificada — substitui a Cloud Function `subscribe` do repo [content-automation](https://github.com/Matheus-Thurler/content-automation).

| Endpoint | Uso |
|----------|-----|
| `POST /newsletter/subscribe/` | Inscrição (JSON `{email, name}` — compatível com Hugo/CF) |
| `GET /newsletter/unsubscribe/?token=` | Cancelamento (token base64 do email) |
| `GET /newsletter/api/subscribers/` | Lista ativos para envio (header `X-Internal-Token`) |

```bash
# Migrar subscribers.json do GCS
uv run python manage.py import_subscribers path/to/subscribers.json

# Exportar para content-automation (formato GCS)
uv run python manage.py export_subscribers -o subscribers.json
```

Configure `NEWSLETTER_INTERNAL_TOKEN` e `SMTP_PASSWORD` no `.env` para produção. Em dev, emails vão para o console.

## Posts com IA (Gemini)

No admin: **Blog → Posts → Generate with AI** (ou sidebar *Gerar post com IA*).

1. Descreva o post (tema, estrutura, links, tom)
2. Escolha idioma (EN, PT ou ambos)
3. Gemini gera um **rascunho** — revise e publique no admin

```bash
# .env
GEMINI_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-3.5-flash   # GA jul/2026 — substitui gemini-2.5-flash (indisponível p/ contas novas)
```

Usa a mesma API do `content-automation` (Google AI Studio / Secret Manager).

## Platform apps

| App | Função | Comando / URL |
|-----|--------|---------------|
| `curation` | RSS → Gemini → Discord | `uv run python manage.py run_curation` |
| `campaigns` | Newsletter semanal | `uv run python manage.py build_campaign` / `--send` |
| `content_pipeline` | Orquestra tudo | `uv run python manage.py run_pipeline` |
| `redirects` | 301/302 (migração Hugo) | Admin → Redirects |
| `pages` | CMS (about, terms…) | `/pages/<slug>/` |
| `media_library` | Biblioteca de imagens | Admin → Media library |
| `contact` | Formulário de contato | `/contact/` |
| `analytics` | Pageviews próprios | `/analytics/track/` + Admin |
| `integrations` | YouTube + GitHub sync | `uv run python manage.py sync_integrations` |

Setup inicial:

```bash
uv run python manage.py seed_platform   # feeds RSS + integrações padrão
```

Variáveis extras no `.env`: `YOUTUBE_CHANNEL_ID`, `DISCORD_PUBLIC_KEY`, Discord bot via GCP secret `discord-bot-token`.

### Discord interativo + schedulers

| Endpoint | Schedule | Função |
|----------|----------|--------|
| `POST /discord/interactions/` | — | Botões Aprovar/Rejeitar (mesmo fluxo GCP) |
| `POST /internal/scheduler/check-content/` | 08:00 BRT diário | Novos posts/vídeos → Discord |
| `POST /internal/scheduler/curate/` | Dom 20:00 BRT | Gemini draft → `#drafts-review` |

Header: `X-Internal-Token` (GCP secret `internal-api-token` ou `NEWSLETTER_INTERNAL_TOKEN`).

```bash
# Manual / cron local
uv run python manage.py run_scheduled_jobs --job=curate
uv run python manage.py run_scheduled_jobs --job=check_content

# Docker com cron embutido
docker compose --profile scheduler up
```

**Discord Developer Portal:** apontar Interactions URL para `https://seu-dominio/discord/interactions/`

## CI/CD (GitHub Actions)

| Workflow | Trigger | Ação |
|----------|---------|------|
| `cloud-run-deploy-merge.yml` | push `django-migration` | build → Cloud Run → **Firebase CDN (live)** |
| `cloud-run-deploy-pull-request.yml` | PR com mudanças em `django_site/` | pytest + build Docker (sem deploy) |
| `firebase-hosting-merge.yml` | push `master` | Hugo → channel **`hugo-backup`** (rollback) |

**Arquitetura live:** `matheusthurler.com.br` → Firebase Hosting (CDN global) → Cloud Run (`matheus-blog`).

**Rollback Hugo:** https://hugo-backup--matheus-cloud-pessoal.web.app (atualizado a cada push no `master`).

Config: `firebase.json` (Django live) · `firebase.hugo.json` (Hugo estático no channel).

Secret reutilizada: `FIREBASE_SERVICE_ACCOUNT_MATHEUS_CLOUD_PESSOAL`.

A SA do GitHub (`github-action-1099034129@...`) precisa de roles extras para deploy:

```bash
SA=github-action-1099034129@matheus-cloud-pessoal.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding matheus-cloud-pessoal \
  --member="serviceAccount:${SA}" --role="roles/run.admin"
gcloud projects add-iam-policy-binding matheus-cloud-pessoal \
  --member="serviceAccount:${SA}" --role="roles/artifactregistry.writer"
gcloud iam service-accounts add-iam-policy-binding \
  blog-cloud-run@matheus-cloud-pessoal.iam.gserviceaccount.com \
  --member="serviceAccount:${SA}" --role="roles/iam.serviceAccountUser"
```

Env/secrets do Cloud Run continuam no Terraform; a CI só atualiza a **imagem**.
