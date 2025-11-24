# 🎬 Atualização Automática de Vídeos do YouTube

Este diretório contém scripts para atualizar automaticamente os vídeos recentes do YouTube exibidos no site.

## 🚀 Escolha Seu Método

### ✨ Método 1: RSS Feed (Recomendado - Sem API Key)

**Vantagens:**
- ✅ 100% gratuito
- ✅ Sem configuração do Google Cloud
- ✅ Sem limites de quota
- ✅ Setup em 2 minutos

**Limitações:**
- ⚠️ Apenas ~15 vídeos mais recentes
- ⚠️ Metadados básicos

**Usar quando:** Você quer simplicidade máxima e só precisa dos vídeos recentes.

📖 **[Guia Completo RSS](../docs/youtube-videos-rss.md)**

```bash
# 1. Instalar
pip install -r scripts/requirements-rss.txt

# 2. Configurar (adicione no .env)
YOUTUBE_CHANNEL_ID=UCxxxxxxxxx  # Seu Channel ID

# 3. Rodar
python scripts/update-youtube-videos-rss.py
```

---

### 🔑 Método 2: YouTube Data API (Opcional - Mais Recursos)

**Vantagens:**
- ✅ Todos os vídeos do canal
- ✅ Metadados completos (views, likes, duração)
- ✅ Estatísticas detalhadas
- ✅ Playlists e filtros avançados

**Requisitos:**
- ⚠️ Precisa de API Key (gratuito mas requer conta Google Cloud)
- ⚠️ Limites de quota (10.000/dia - suficiente para uso normal)

**Usar quando:** Você precisa de metadados detalhados ou vídeos mais antigos.

📖 **[Guia Completo API](../docs/youtube-videos.md)**

```bash
# 1. Instalar
pip install -r scripts/requirements.txt

# 2. Configurar (adicione no .env)
YOUTUBE_API_KEY=sua_api_key
YOUTUBE_CHANNEL_ID=UCxxxxxxxxx

# 3. Rodar
python scripts/update-youtube-videos.py
```

## 📊 Comparação Rápida

| Característica | RSS | API |
|---|---|---|
| API Key | ❌ Não | ✅ Sim |
| Configuração | 🟢 30 seg | 🟡 5 min |
| Limites | 🟢 Ilimitado | 🟡 10k/dia |
| Vídeos | 🟡 15 recentes | 🟢 Todos |
| Metadados | 🟡 Básicos | 🟢 Completos |

## 🤖 Automação com GitHub Actions

Ambos os métodos têm workflows do GitHub Actions configurados:

- **RSS:** `.github/workflows/update-youtube-videos-rss.yml`
- **API:** `.github/workflows/update-youtube-videos.yml`

**Para ativar:**

1. Configure as variáveis no GitHub:
   - `Settings → Variables and secrets → Actions`
   - Adicione `YOUTUBE_CHANNEL_ID` como Variable
   - (API apenas) Adicione `YOUTUBE_API_KEY` como Secret

2. O workflow roda automaticamente:
   - ⏰ Diariamente às 08:00 UTC (05:00 BRT)
   - 🖱️ Ou manualmente via GitHub Actions UI

## 🔍 Como Obter o Channel ID

### Método Fácil (se você tem link customizado)

1. Acesse seu canal
2. Clique com botão direito → "Ver código-fonte"
3. Procure por: `"channelId":"UC`
4. Copie o ID completo (começa com `UC`)

### Método Alternativo

1. Acesse: https://www.youtube.com/account_advanced
2. Seu Channel ID está listado lá

## 📁 Estrutura de Arquivos

```
scripts/
├── update-youtube-videos-rss.py      # Script RSS (sem API key)
├── update-youtube-videos.py          # Script com API  
├── requirements-rss.txt              # Deps para RSS
└── requirements.txt                  # Deps para API

.github/workflows/
├── update-youtube-videos-rss.yml     # Action RSS
└── update-youtube-videos.yml         # Action API

data/
└── youtube.json                      # Dados dos vídeos (gerado)

docs/
├── youtube-videos-rss.md            # Doc RSS completa
└── youtube-videos.md                # Doc API completa
```

## 💡 Dica Pro

**Comece com RSS**, é mais simples! Se no futuro você precisar de mais recursos, migrar para a API é fácil - o formato do `data/youtube.json` é o mesmo.

## 🐛 Problemas?

Consulte a documentação específica de cada método:
- 📖 [Troubleshooting RSS](../docs/youtube-videos-rss.md#-troubleshooting)
- 📖 [Troubleshooting API](../docs/youtube-videos.md#-troubleshooting)
