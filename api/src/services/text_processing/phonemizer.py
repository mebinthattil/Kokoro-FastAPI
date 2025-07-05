import re
from abc import ABC, abstractmethod

import phonemizer

from .normalizer import normalize_text
from ...structures.schemas import NormalizationOptions

phonemizers = {}


class PhonemizerBackend(ABC):
    """Abstract base class for phonemization backends"""

    @abstractmethod
    def phonemize(self, text: str) -> str:
        """Convert text to phonemes

        Args:
            text: Text to convert to phonemes

        Returns:
            Phonemized text
        """
        pass


class EspeakBackend(PhonemizerBackend):
    """Espeak-based phonemizer implementation"""

    def __init__(self, language: str):
        """Initialize espeak backend

        Args:
            language: Language code ('en-us' or 'en-gb')
        """
        # Force use of regular espeak instead of espeak-ng
        # Try to find espeak executable, fallback to auto-detection
        import shutil
        import logging
        
        logger = logging.getLogger(__name__)
        
        espeak_executable = shutil.which('espeak')
        if espeak_executable:
            logger.info(f"Using espeak executable: {espeak_executable}")
        else:
            # If espeak is not found, let phonemizer auto-detect (may use espeak-ng)
            logger.warning("espeak executable not found, phonemizer will auto-detect (may use espeak-ng)")
            espeak_executable = None
        
        self.backend = phonemizer.backend.EspeakBackend(
            language=language, 
            preserve_punctuation=True, 
            with_stress=True,
            executable=espeak_executable
        )

        self.language = language

    def phonemize(self, text: str) -> str:
        """Convert text to phonemes using espeak

        Args:
            text: Text to convert to phonemes

        Returns:
            Phonemized text
        """
        # Phonemize text
        ps = self.backend.phonemize([text])
        ps = ps[0] if ps else ""

        # Handle special cases
        ps = ps.replace("kəkˈoːɹoʊ", "kˈoʊkəɹoʊ").replace("kəkˈɔːɹəʊ", "kˈəʊkəɹəʊ")
        ps = ps.replace("ʲ", "j").replace("r", "ɹ").replace("x", "k").replace("ɬ", "l")
        ps = re.sub(r"(?<=[a-zɹː])(?=hˈʌndɹɪd)", " ", ps)
        ps = re.sub(r' z(?=[;:,.!?¡¿—…"«»"" ]|$)', "z", ps)

        # Language-specific rules
        if self.language == "en-us":
            ps = re.sub(r"(?<=nˈaɪn)ti(?!ː)", "di", ps)

        return ps.strip()


def create_phonemizer(language: str = "a") -> PhonemizerBackend:
    """Factory function to create phonemizer backend

    Args:
        language: Language code ('a' for US English, 'b' for British English)

    Returns:
        Phonemizer backend instance
    """
    # Map language codes to espeak language codes
    lang_map = {"a": "en-us", "b": "en-gb", "z": "z"}

    if language not in lang_map:
        raise ValueError(f"Unsupported language code: {language}")

    return EspeakBackend(lang_map[language])


def phonemize(text: str, language: str = "a") -> str:
    """Convert text to phonemes

    Args:
        text: Text to convert to phonemes
        language: Language code ('a' for US English, 'b' for British English)

    Returns:
        Phonemized text
    """
    global phonemizers
    
    # Strip input text first to remove problematic leading/trailing spaces
    text = text.strip()
    
    if language not in phonemizers:
        phonemizers[language] = create_phonemizer(language)
    
    result = phonemizers[language].phonemize(text)
    # Final strip to ensure no leading/trailing spaces in phonemes
    return result.strip()
