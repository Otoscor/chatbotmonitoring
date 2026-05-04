"""
URL 메타데이터 추출 유틸리티
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


async def extract_url_metadata(url: str, timeout: int = 10) -> Dict[str, Optional[str]]:
    """
    URL에서 메타데이터 추출
    
    Args:
        url: 추출할 URL
        timeout: 타임아웃 (초)
    
    Returns:
        {
            "title": "페이지 제목",
            "description": "페이지 설명",
            "thumbnail": "썸네일 이미지 URL",
            "site_name": "사이트명"
        }
    """
    metadata = {
        "title": None,
        "description": None,
        "thumbnail": None,
        "site_name": None
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=timeout) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return metadata
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # 제목 추출 (우선순위: og:title > twitter:title > title)
                og_title = soup.find('meta', property='og:title')
                twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
                title_tag = soup.find('title')
                
                if og_title and og_title.get('content'):
                    metadata['title'] = og_title.get('content').strip()
                elif twitter_title and twitter_title.get('content'):
                    metadata['title'] = twitter_title.get('content').strip()
                elif title_tag and title_tag.string:
                    metadata['title'] = title_tag.string.strip()
                
                # 설명 추출 (우선순위: og:description > twitter:description > meta description)
                og_desc = soup.find('meta', property='og:description')
                twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                
                if og_desc and og_desc.get('content'):
                    metadata['description'] = og_desc.get('content').strip()
                elif twitter_desc and twitter_desc.get('content'):
                    metadata['description'] = twitter_desc.get('content').strip()
                elif meta_desc and meta_desc.get('content'):
                    metadata['description'] = meta_desc.get('content').strip()
                
                # 이미지 추출 (우선순위: og:image > twitter:image)
                og_image = soup.find('meta', property='og:image')
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content').strip()
                    # 상대 경로를 절대 경로로 변환
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                    metadata['thumbnail'] = img_url
                elif twitter_image and twitter_image.get('content'):
                    img_url = twitter_image.get('content').strip()
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                    metadata['thumbnail'] = img_url
                
                # 사이트명 추출
                og_site = soup.find('meta', property='og:site_name')
                if og_site and og_site.get('content'):
                    metadata['site_name'] = og_site.get('content').strip()
                else:
                    # fallback: URL의 도메인 사용
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    metadata['site_name'] = parsed.netloc
                
                logger.info(f"Successfully extracted metadata from {url}")
                return metadata
                
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error extracting metadata from {url}: {e}")
    except Exception as e:
        logger.error(f"Error extracting metadata from {url}: {e}")
    
    return metadata


async def extract_page_text(url: str, max_length: int = 5000) -> Optional[str]:
    """
    웹페이지에서 본문 텍스트 추출 (AI 요약용)
    
    Args:
        url: 추출할 URL
        max_length: 최대 텍스트 길이
    
    Returns:
        추출된 텍스트 (없으면 None)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # 스크립트, 스타일 태그 제거
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # 본문 추출 (우선순위: article > main > body)
                content = None
                article = soup.find('article')
                main = soup.find('main')
                
                if article:
                    content = article.get_text()
                elif main:
                    content = main.get_text()
                else:
                    content = soup.body.get_text() if soup.body else soup.get_text()
                
                if content:
                    # 공백 정리
                    lines = (line.strip() for line in content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    # 최대 길이 제한
                    if len(text) > max_length:
                        text = text[:max_length] + "..."
                    
                    return text
                
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {e}")
    
    return None
