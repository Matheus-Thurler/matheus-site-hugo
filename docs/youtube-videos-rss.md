# Como Atualizar Vídeos do YouTube - Método RSS (Sem API Key)

## 🎯 Vantagens do Método RSS

- ✅ **Sem API Key necessária** - 100% gratuito!
- ✅ **Sem limites de quota** - RSS feeds são públicos
- ✅ **Configuração simples** - Só precisa do Channel ID/Username
- ✅ **Mais leve** - Menos dependências Python
- ⚠️ **Limitação**: Pega apenas os ~15 vídeos mais recentes do canal

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r scripts/requirements-rss.txt
```

### 2. Configurar Canal

Edite o arquivo `.env`:

```bash
# Opção A: Use seu Channel ID (recomendado)
YOUTUBE_CHANNEL_ID=UC-SEU-CHANNEL-ID-AQUI

# OU Opção B: Use seu username/handle
YOUTUBE_CHANNEL_USERNAME=@matheusthurler

# Quantidade de vídeos (opcional, padrão: 2)
MAX_RECENT_VIDEOS=2
```

### 3. Executar Script

```bash
python scripts/update-youtube-videos-rss.py
```

Pronto! O arquivo `data/youtube.json` será atualizado automaticamente.

## 🔍 Como Obter o Channel ID

### Método 1: Via URL do Canal

1. Acesse seu canal do YouTube
2. Clique em "Personalizar canal"
3. Veja a URL: `youtube.com/channel/UC-XXXXX`
4. Copie o ID que começa com `UC`

### Método 2: Via Código Fonte (se URL customizada)

1. Acesse seu canal
2. Clique com botão direito → "Ver código-fonte da página"
3. Procure por `"channelId":"UC`
4. Copie o ID completo

### Método 3: Use o Username/Handle

Se seu canal tem handle (ex: `@matheusthurler`), você pode usar diretamente:

```bash
YOUTUBE_CHANNEL_USERNAME=@matheusthurler
```

## 🤖 Automação com GitHub Actions

### Configurar no GitHub

1. Vá em: `Settings → Variables and secrets → Actions → Variables`
2. Adicione uma variável:
   - **Name**: `YOUTUBE_CHANNEL_ID`
   - **Value**: Seu Channel ID (ex: `UCxxxxxxx`) OU seu handle (ex: `@matheusthurler`)

### Ativar o Workflow

O arquivo `.github/workflows/update-youtube-videos-rss.yml` já está configurado para:

- ✅ Executar diariamente às 08:00 UTC (05:00 BRT)
- ✅ Pode ser executado manualmente
- ✅ Faz commit automático se houver novos vídeos

**Para executar manualmente:**

1. Vá em: `Actions → Update YouTube Videos (RSS)`
2. Clique em `Run workflow`

## 📊 Comparação: RSS vs API

| Característica | RSS Feed | YouTube API |
|---------------|----------|-------------|
| **API Key** | ❌ Não precisa | ✅ Precisa |
| **Configuração** | 🟢 Simples | 🟡 Média |
| **Limites** | 🟢 Ilimitado | 🟡 10.000 quotas/dia |
| **Metadados** | 🟡 Básicos | 🟢 Completos |
| **Vídeos disponíveis** | 🟡 ~15 recentes | 🟢 Todos |
| **Estatísticas** | ❌ Não | ✅ Views, likes, etc |
| **Confiabilidade** | 🟢 Alta | 🟢 Alta |

## 💡 Quando Usar Cada Método?

### Use RSS Feed quando:
- ✅ Quer simplicidade máxima
- ✅ Não quer criar conta no Google Cloud
- ✅ Precisa apenas dos vídeos mais recentes (últimos 15)
- ✅ Quer evitar lidar com quotas de API

### Use YouTube API quando:
- ✅ Precisa de metadados detalhados (views, likes, duração)
- ✅ Quer buscar vídeos mais antigos
- ✅ Precisa de playlists específicas
- ✅ Quer estatísticas de engagement

## 🔧 Testando Localmente

```bash
# 1. Configure o .env
echo "YOUTUBE_CHANNEL_ID=@matheusthurler" > .env
echo "MAX_RECENT_VIDEOS=2" >> .env

# 2. Instale dependências
pip install -r scripts/requirements-rss.txt

# 3. Execute o script
python scripts/update-youtube-videos-rss.py

# 4. Verifique o resultado
cat data/youtube.json
```

## 🐛 Troubleshooting

### Erro: "Nenhum vídeo encontrado"

**Soluções:**

1. **Verifique o Channel ID:**
   ```bash
   # Teste o RSS feed manualmente no navegador:
   https://www.youtube.com/feeds/videos.xml?channel_id=SEU_CHANNEL_ID
   ```

2. **Se estiver usando username**, tente o Channel ID completo:
   - Username pode não funcionar para todos os canais
   - Channel ID (UC...) é mais confiável

3. **Verifique se o canal tem vídeos públicos**
   - Vídeos privados/não listados não aparecem no RSS

### Erro: "Module not found"

```bash
# Reinstale as dependências
pip install --upgrade -r scripts/requirements-rss.txt
```

### RSS Feed não atualiza imediatamente

O RSS do YouTube pode ter delay de alguns minutos após publicar um vídeo novo. Isso é normal.

## 📚 Recursos

- [YouTube RSS Feeds Documentation](https://support.google.com/youtube/answer/6224202)
- [Feedparser Documentation](https://feedparser.readthedocs.io/)

## 🔄 Migrar de API para RSS

Se você já está usando o script com API e quer trocar para RSS:

1. **Mantenha o `data/youtube.json`** (formato é o mesmo)
2. **Troque o workflow** no GitHub Actions:
   - Desative: `.github/workflows/update-youtube-videos.yml`
   - Ative: `.github/workflows/update-youtube-videos-rss.yml`
3. **Atualize a variável** no GitHub:
   - Não precisa mais do Secret `YOUTUBE_API_KEY`
   - Só precisa da Variable `YOUTUBE_CHANNEL_ID`

Pronto! O site continuará funcionando normalmente.
