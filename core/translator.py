"""Offline subtitle translation using Argos Translate."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from argostranslate import package, translate

ARGOS_PACKAGE_INDEX_URL = "https://www.argosopentech.com/argospm/index/"
DEFAULT_TRADITIONAL_CHINESE_PAIRS = (("en", "zt"), ("zt", "en"))


class Translator:
    """Argos Translate wrapper with package availability checks."""

    def __init__(self) -> None:
        self._installed_languages = {lang.code: lang for lang in translate.get_installed_languages()}

    def refresh(self) -> None:
        """Reload installed language metadata."""
        self._installed_languages = {lang.code: lang for lang in translate.get_installed_languages()}

    def has_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check whether a specific translation pair is installed."""
        return self._get_translation(source_lang, target_lang) is not None

    def _get_translation(self, source_lang: str, target_lang: str):
        source = self._installed_languages.get(source_lang)
        target = self._installed_languages.get(target_lang)
        if source is None or target is None:
            return None
        return source.get_translation(target)

    def install_online(self, source_lang: str, target_lang: str) -> bool:
        """Install one Argos language package from online package index."""
        package.update_package_index()
        packages = package.get_available_packages()
        match = next(
            (item for item in packages if item.from_code == source_lang and item.to_code == target_lang),
            None,
        )
        if match is None:
            return False

        download_path = match.download()
        package.install_from_path(download_path)
        self.refresh()
        return self.has_pair(source_lang, target_lang)

    def install_defaults_online(self) -> bool:
        """Install default English <-> Traditional Chinese pairs online."""
        ok = True
        for source_lang, target_lang in DEFAULT_TRADITIONAL_CHINESE_PAIRS:
            if not self.has_pair(source_lang, target_lang):
                ok = self.install_online(source_lang, target_lang) and ok
        return ok

    def install_from_directory(self, model_dir: str | Path) -> int:
        """Install all .argosmodel files found in specified directory."""
        directory = Path(model_dir)
        if not directory.exists() or not directory.is_dir():
            return 0

        install_count = 0
        for model_file in directory.glob("*.argosmodel"):
            package.install_from_path(str(model_file))
            install_count += 1
        if install_count:
            self.refresh()
        return install_count

    def default_pairs_ready(self) -> bool:
        """Return whether default en<->zt packages are already installed."""
        return all(self.has_pair(src, dst) for src, dst in DEFAULT_TRADITIONAL_CHINESE_PAIRS)

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

