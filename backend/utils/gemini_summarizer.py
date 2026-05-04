"""
Google Gemini AI 요약 생성 유틸리티
"""
import google.generativeai as genai
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Gemini API 초기화
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


async def summarize_text(text: str, max_sentences: int = 5) -> Optional[str]:
    """
    텍스트를 Gemini AI로 요약
    
    Args:
        text: 요약할 텍스트
        max_sentences: 최대 문장 수
    
    Returns:
        요약된 텍스트 (실패 시 None)
    """
    if not GEMINI_API_KEY:
        logger.error("Cannot summarize: GEMINI_API_KEY not configured")
        return None
    
    try:
        # Gemini 1.5 Flash 모델 사용 (무료 할당량)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""다음 웹페이지 내용을 {max_sentences}문장 이내로 한글로 요약해주세요. 
핵심 내용만 간결하게 정리하고, 불필요한 부가 설명은 제외하세요.

웹페이지 내용:
{text[:5000]}  # 최대 5000자로 제한

요약:"""
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            summary = response.text.strip()
            logger.info(f"Successfully generated summary: {len(summary)} characters")
            return summary
        else:
            logger.warning("Gemini returned empty response")
            return None
            
    except Exception as e:
        logger.error(f"Error generating summary with Gemini: {e}")
        return None


async def summarize_url(url: str, page_text: Optional[str] = None) -> Optional[str]:
    """
    URL 또는 페이지 텍스트를 요약
    
    Args:
        url: 요약할 URL
        page_text: 이미 추출된 페이지 텍스트 (없으면 URL에서 추출)
    
    Returns:
        요약된 텍스트 (실패 시 None)
    """
    if not page_text:
        # URL에서 텍스트 추출
        from .url_parser import extract_page_text
        page_text = await extract_page_text(url)
    
    if not page_text:
        logger.warning(f"No text extracted from {url}")
        return None
    
    # 텍스트가 너무 짧으면 요약 불필요
    if len(page_text) < 200:
        logger.info(f"Text too short for summarization: {len(page_text)} characters")
        return page_text[:500]  # 그대로 반환
    
    summary = await summarize_text(page_text, max_sentences=5)
    return summary
