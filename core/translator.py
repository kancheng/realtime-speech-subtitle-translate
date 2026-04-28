"""Offline subtitle translation using Argos Translate."""

from __future__ import annotations

from typing import Optional

from argostranslate import translate


class Translator:
    """Argos Translate wrapper with package availability checks."""

    def __init__(self) -> None:
        self._installed_languages = {lang.code: lang for lang in translate.get_installed_languages()}

    def refresh(self) -> None:
        """Reload installed language metadata."""
        self._installed_languages = {lang.code: lang for lang in translate.get_installed_languages()}

    def _get_translation(self, source_lang: str, target_lang: str):
        source = self._installed_languages.get(source_lang)
        target = self._installed_languages.get(target_lang)
        if source is None or target is None:
            return None
        return source.get_translation(target)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language."""
        clean_text = (text or "").strip()
        if not clean_text:
            return ""
        if source_lang == target_lang:
            return clean_text

        translation = self._get_translation(source_lang, target_lang)
        if translation is None:
            return f"Translation package not installed for {source_lang} to {target_lang}."

        try:
            result: Optional[str] = translation.translate(clean_text)
            return result.strip() if result else ""
        except Exception:
            return f"Translation failed for {source_lang} to {target_lang}."

