# -*- coding: utf-8 -*-
"""
Jeeves - Personal News Butler
File: jeeves_formatter.py
Description: Hoitaa uutisraportin visuaalisen muotoilun ja lähdeviitteet.
"""

import html

class JeevesFormatter:
    def __init__(self, lang_func, lang="fi"):
        """
        lang_func: Viittaus jeeves_logic.get_localized_text funktioon
        lang: Käytettävä kieli (fi/en)
        """
        self.get_text = lang_func
        self.lang = lang
        self.sources = []

    def _get_category_comment(self, category):
        """Hakee hovimestarin kommentin kategorialle."""
        formatted_cat = category.capitalize()
        comment = self.get_text(f"personality.category_comments.{formatted_cat}", self.lang)

        # Fallback jos kategorialle ei ole omaa kommenttia
        if comment.startswith("["):
            comment = self.get_text("personality.category_comments.Default", self.lang)
        return comment

    def build_report(self, entries, keywords, greeting, pending_indicator, show_full=False):
        """Rakentaa koko raportin tekstimuodossa."""
        self.sources = []  # Nollataan lähdelista
        lines = []

        # 1. Alkurakenne (Tervehdys)
        lines.append(f"\n{'='*60}")
        lines.append(f"    {greeting.upper()}")
        lines.append(f"{'='*60}\n")

        if not entries:
            import random
            idle_msg = self.get_text("personality.idle_comments", self.lang)
            if isinstance(idle_msg, list):
                idle_msg = random.choice(idle_msg)
            lines.append(f"[*] Jeeves: \"{idle_msg}\"")
            return "\n".join(lines)

        # 2. Ryhmitellään uutiset kategorioittain
        report_data = {}
        for e in entries:
            cat = e.get('category', 'General')
            if cat not in report_data:
                report_data[cat] = []
            report_data[cat].append(e)

        # 3. Käydään kategoriat läpi
        for category, items in report_data.items():
            comment = self._get_category_comment(category)
            lines.append(f"[*] Jeeves: \"{comment}\"")
            lines.append(f"--- {category.upper()} ---")

            for item in items:
                # Kerätään URL ja määritetään sen numero
                url = item.get('url', '')
                if url and url not in self.sources:
                    self.sources.append(url)

                source_idx = self.sources.index(url) + 1 if url else "?"

                # Tarkistetaan tila ja prioriteetti
                is_pending = pending_indicator in item.get('summary', '')
                is_priority = any(k in item.get('title', '').lower() for k in keywords)

                if is_priority:
                    prefix = "[!!!]"
                elif is_pending:
                    prefix = "[ ? ]"
                else:
                    prefix = "[ + ]"

                # Lisätään uutisrivi
                clean_title = html.unescape(item.get('title', ''))
                lines.append(f"  {prefix} {clean_title} [{source_idx}]")

                # Jos --full on päällä, näytetään tiivistelmä
                if show_full:
                    if is_pending:
                        lines.append(f"      ({pending_indicator})")
                    else:
                        summary = item.get('summary', '')
                        indented_summary = summary.replace('\n', '\n      ')
                        lines.append(f"      {indented_summary}")
                    lines.append(f"      Lähde: {url}\n")

            lines.append("") # Tyhjä rivi kategorioiden väliin

        # 4. Lähdeluettelo loppuun
        if self.sources:
            sources_label = self.get_text("ui.sources_label", self.lang) or "LÄHTEET JA VIITTEET:"
            lines.append("-" * 30)
            lines.append(sources_label)
            for i, url in enumerate(self.sources, 1):
                lines.append(f"[{i}] {url}")
            lines.append("-" * 30)

        return "\n".join(lines)
