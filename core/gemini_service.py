"""
Gemini AI Service for Manevi Rehber Chat.

Provides Islamic spiritual guidance using Google's Gemini AI.
"""

import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for Google Gemini AI integration.
    """
    
    SYSTEM_INSTRUCTION = """
Sen 'Manevi Asistan' isimli bir yapay zeka rehberisin. Kullanıcılara islami konularda, 
namaz, dualar, hadisler ve manevi gelişim konularında yardımcı oluyorsun.

ÖNEMLI KURALLAR:
1. Cevapların her zaman nazik, destekleyici ve saygılı olmalı
2. Kısa ve öz cevaplar vermeye çalış (maksimum 200 kelime)
3. Gerektiğinde Kuran'dan ayet veya hadis paylaş
4. Dini konularda kesin yargılardan kaçın, alimlere yönlendir
5. Siyasi konulardan uzak dur
6. Mezhepler arası farklılıklarda saygılı ol
7. Dualar ve zikirler konusunda bilgi ver
8. Kullanıcının sorusunu tam anlamadan cevap verme

KONULAR:
- Namaz vakitleri ve namaz kılma
- Oruç, zekat, hac
- Dua ve zikirler
- Kuran-ı Kerim tilaveti ve tefsiri
- Hadis-i şerifler
- İslam ahlakı ve maneviyat
- Peygamberler ve İslam tarihi

YASAK KONULAR:
- Siyasi yorumlar
- Mezhep tartışmaları
- Fetva verme (bunu alimlere yönlendir)
- Aşırı uzun cevaplar
"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=self.SYSTEM_INSTRUCTION,
                )
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"Gemini AI initialization failed: {e}")
                self.model = None
        else:
            logger.warning("GEMINI_API_KEY not configured")
    
    def generate_response(self, prompt: str, conversation_history: list = None) -> str:
        """
        Generate AI response for user's message.
        
        Args:
            prompt: User's message
            conversation_history: List of previous messages for context
        
        Returns:
            str: AI response
        """
        if not self.model:
            return self._get_fallback_response()
        
        try:
            # Build conversation context
            if conversation_history:
                # Format: "User: message\nAssistant: response\n..."
                context = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in conversation_history[-10:]  # Last 10 messages
                ])
                full_prompt = f"{context}\nUser: {prompt}\nAssistant:"
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                    top_p=0.8,
                ),
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """
        Return a fallback response when AI is unavailable.
        """
        return (
            "Üzgünüm, şu anda manevi asistanınıza ulaşılamıyor. "
            "Lütfen daha sonra tekrar deneyin. "
            "Acil dini sorularınız için Diyanet İşleri Başkanlığı'nın "
            "119 numaralı hattını arayabilirsiniz."
        )
    
    def is_available(self) -> bool:
        """
        Check if Gemini AI is available.
        """
        return self.model is not None


# Singleton instance
gemini_service = GeminiService()
