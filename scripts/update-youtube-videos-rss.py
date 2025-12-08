#!/usr/bin/env python3
"""
Script para atualizar automaticamente os vídeos recentes do YouTube usando RSS Feed.
VANTAGEM: Não requer API Key do YouTube!

Requisitos:
    pip install feedparser python-dotenv

Uso:
    python scripts/update-youtube-videos-rss.py

Configuração:
    Crie um arquivo .env com:
    YOUTUBE_CHANNEL_ID=seu_channel_id_aqui
    # OU
    YOUTUBE_CHANNEL_USERNAME=@matheusthurler
"""

import os
import json
import sys
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    import feedparser
    from dotenv import load_dotenv
except ImportError:
    print("❌ Erro: Dependências não instaladas.")
    print("Execute: pip install feedparser python-dotenv")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')
CHANNEL_USERNAME = os.getenv('YOUTUBE_CHANNEL_USERNAME')
MAX_VIDEOS = int(os.getenv('MAX_RECENT_VIDEOS', '2'))

# Caminhos
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'youtube.json'


def get_channel_id_from_username(username: str) -> str:
    """
    Tenta extrair o Channel ID a partir do username.
    Nota: Para RSS, podemos usar o username diretamente em alguns casos.
    """
    # Remove @ se presente
    username = username.lstrip('@')
    return username


def extract_video_id_from_url(url: str) -> str:
    """Extrai o ID do vídeo a partir da URL."""
    # URL format: https://www.youtube.com/watch?v=VIDEO_ID
    match = re.search(r'watch\?v=([^&]+)', url)
    if match:
        return match.group(1)
    return None


def is_short_video(entry) -> bool:
    """
    Detecta se um vídeo é um Short.
    
    Shorts podem ser identificados por:
    - URL contendo '/shorts/'
    - Título começando com '#' (comum em shorts)
    - Descrição muito curta (menos de 50 caracteres)
    
    Args:
        entry: Entrada do feed RSS
        
    Returns:
        True se for um Short, False caso contrário
    """
    # Verificar URL por '/shorts/'
    if hasattr(entry, 'link') and '/shorts/' in entry.link:
        return True
    
    # Verificar se há links alternativos com '/shorts/'
    if hasattr(entry, 'links'):
        for link in entry.links:
            if hasattr(link, 'href') and '/shorts/' in link.href:
                return True
    
    # Verificar título - Shorts geralmente têm títulos curtos ou começam com #
    title = entry.title if hasattr(entry, 'title') else ''
    if title.startswith('#'):
        return True
    
    # Verificar media:group por duração (se disponível)
    # Shorts têm menos de 60 segundos
    if hasattr(entry, 'media_group'):
        for media in entry.media_group:
            if hasattr(media, 'duration'):
                try:
                    duration = int(media.duration)
                    if duration <= 60:
                        return True
                except (ValueError, TypeError):
                    pass
    
    return False


def get_latest_videos_from_rss(channel_identifier: str, max_results: int = 2) -> List[Dict]:
    """
    Busca os vídeos mais recentes de um canal do YouTube usando RSS Feed.
    Filtra automaticamente os Shorts, retornando apenas vídeos normais.
    
    Args:
        channel_identifier: Channel ID ou username do canal
        max_results: Número máximo de vídeos para retornar
        
    Returns:
        Lista de dicionários com informações dos vídeos
    """
    # Construir URL do RSS Feed
    # Formato: https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
    # OU: https://www.youtube.com/feeds/videos.xml?user=USERNAME
    
    # Tentar com channel_id primeiro
    if channel_identifier.startswith('UC'):
        # É um Channel ID
        rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_identifier}'
    else:
        # É um username (sem @)
        channel_identifier = channel_identifier.lstrip('@')
        # Tentar primeiro como user
        rss_url = f'https://www.youtube.com/feeds/videos.xml?user={channel_identifier}'
    
    print(f"🔍 Buscando RSS Feed: {rss_url}")
    
    try:
        # Parse do RSS feed
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            # Tentar com channel_id se user não funcionou
            if not channel_identifier.startswith('UC'):
                print(f"⚠️  Nenhum vídeo encontrado com user={channel_identifier}")
                print(f"💡 Dica: Tente usar o Channel ID completo (começa com UC)")
                return []
        
        videos = []
        shorts_skipped = 0
        
        for entry in feed.entries:
            # Pular se for um Short
            if is_short_video(entry):
                shorts_skipped += 1
                print(f"⏭️  Pulando Short: {entry.title[:50]}...")
                continue
            
            video_id = extract_video_id_from_url(entry.link)
            
            if not video_id:
                continue
            
            # Processar data de publicação
            published_date = entry.published if hasattr(entry, 'published') else entry.updated
            
            # Extrair descrição (limitada no RSS)
            description = entry.summary if hasattr(entry, 'summary') else ''
            # Remover HTML tags
            description = re.sub('<[^<]+?>', '', description)
            # Limitar tamanho
            if len(description) > 200:
                description = description[:200] + '...'
            
            video_data = {
                'id': video_id,
                'title': entry.title,
                'description': description,
                'published_at': published_date,
                'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
                'embed_url': f'https://www.youtube.com/embed/{video_id}',
                'watch_url': f'https://youtu.be/{video_id}'
            }
            videos.append(video_data)
            
            # Parar quando atingir o número desejado
            if len(videos) >= max_results:
                break
        
        if shorts_skipped > 0:
            print(f"📊 {shorts_skipped} Short(s) ignorado(s)")
        
        return videos
        
    except Exception as e:
        print(f"❌ Erro ao buscar RSS feed: {e}")
        return []


def save_videos_to_json(videos: List[Dict], output_file: Path):
    """Salva a lista de vídeos no arquivo JSON."""
    data = {
        'recent_videos': videos,
        'last_updated': datetime.now().isoformat(),
        'total_videos': len(videos),
        'source': 'rss_feed'
    }
    
    # Criar diretório se não existir
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar JSON com formatação bonita
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Arquivo atualizado: {output_file}")


def main():
    """Função principal."""
    print("🎬 Atualizando vídeos recentes do YouTube via RSS Feed...")
    print("✨ Vantagem: Não requer API Key!\n")
    print(f"📁 Diretório do projeto: {PROJECT_ROOT}")
    
    # Determinar identificador do canal
    channel_identifier = None
    
    if CHANNEL_ID:
        channel_identifier = CHANNEL_ID
        print(f"📺 Canal (ID): {channel_identifier}")
    elif CHANNEL_USERNAME:
        channel_identifier = CHANNEL_USERNAME
        print(f"📺 Canal (Username): {channel_identifier}")
    else:
        print("❌ Erro: Nenhum identificador de canal configurado no .env")
        print("\nAdicione uma das seguintes variáveis no arquivo .env:")
        print("  YOUTUBE_CHANNEL_ID=UC... (Channel ID completo)")
        print("  YOUTUBE_CHANNEL_USERNAME=@matheusthurler (seu handle)")
        print("\n💡 Como obter o Channel ID:")
        print("1. Acesse seu canal e clique em 'Personalizar canal'")
        print("2. O ID está na URL: youtube.com/channel/SEU_CHANNEL_ID")
        print("3. Copie o ID que começa com 'UC'")
        print("\n💡 Ou use seu username/handle com @")
        sys.exit(1)
    
    # Buscar vídeos
    print(f"🔍 Buscando últimos {MAX_VIDEOS} vídeos...\n")
    
    videos = get_latest_videos_from_rss(channel_identifier, MAX_VIDEOS)
    
    if not videos:
        print("\n❌ Nenhum vídeo encontrado.")
        print("\n💡 Possíveis soluções:")
        print("1. Verifique se o Channel ID está correto")
        print("2. Se está usando username, tente o Channel ID completo")
        print("3. Verifique se o canal tem vídeos públicos")
        sys.exit(1)
    
    # Exibir vídeos encontrados
    print(f"✅ {len(videos)} vídeo(s) encontrado(s):")
    for i, video in enumerate(videos, 1):
        print(f"\n  {i}. {video['title']}")
        print(f"     📅 {video['published_at']}")
        print(f"     🔗 {video['watch_url']}")
        if video['description']:
            desc_preview = video['description'][:80] + '...' if len(video['description']) > 80 else video['description']
            print(f"     📝 {desc_preview}")
    
    # Salvar no arquivo JSON
    print(f"\n💾 Salvando em {OUTPUT_FILE}...")
    save_videos_to_json(videos, OUTPUT_FILE)
    
    print("\n✨ Atualização concluída com sucesso!")
    print(f"📊 Total de vídeos: {len(videos)}")
    print(f"📁 Arquivo: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
    print(f"🔄 Método: RSS Feed (sem API Key necessária)")


if __name__ == '__main__':
    main()
