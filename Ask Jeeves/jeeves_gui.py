# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler UI
File: jeeves_gui.py
Author: [Tuomas Lähteenmäki]
Version: 3.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Source: https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

import customtkinter as ctk
import subprocess
import sys
import threading
import webbrowser
import json
import os
from jeeves_logic import MEMORY_FILE, METADATA_FILE, JeevesMemory, get_localized_text, get_priority_keywords, get_time_based_greeting
from PIL import Image
from jeeves_personality import JeevesPersonality
from jeeves_updater import check_for_updates

# Päivitetty versionumero tähän
CURRENT_VERSION = "3.1.0"

class ConsoleRedirector:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

class JeevesGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. ALUSTETAAN MUUTTUJAT JA LADATAAN DATA HETI
        self.category_styles = {}
        self.filter_buttons = {}
        self.memory = JeevesMemory()
        self.lang = self.memory.lang

        # --- LADATAAN TYYLIT TIEDOSTOSTA ENNEN KUIN NIITÄ KÄYTETÄÄN ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        personality_path = os.path.join(current_dir, "resources", "personality.json")

        try:
            with open(personality_path, "r", encoding="utf-8") as f:
                full_metadata = json.load(f)
                self.category_styles = full_metadata.get("category_styles", {})
                print(f"[*] Jeeves: Tyylit ladattu kohteesta: {personality_path}")
        except Exception as e:
            print(f"[!] Jeeves: Tyylien lataus epäonnistui: {e}")
            self.category_styles = {"Default": {"icon": "📰", "color": "transparent"}}

        # Ikkunan perusasetukset
        self.title(get_localized_text("gui_title", self.lang))
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- VASEN PANEELI (KIINTEÄ) ---
        self.sidebar = ctk.CTkFrame(self, width=320)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)

        # 1. Päivitys-nappi
        self.refresh_btn = ctk.CTkButton(self.sidebar,
                                        text=get_localized_text("gui_refresh", self.lang),
                                        command=self.on_refresh)
        self.refresh_btn.pack(pady=(20, 10), padx=10, fill="x")

        # --- JAETAAN ALAPUOLI: IKONIT JA LISTA ---
        self.sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_content.pack(expand=True, fill="both")

        # A. Ikonipalkki (Vasen reuna)
        self.icon_bar = ctk.CTkFrame(self.sidebar_content, width=50, fg_color="transparent")
        self.icon_bar.pack(side="left", fill="y", padx=(2, 0), pady=5)
        self.icon_bar.pack_propagate(False)

        # B. Uutislista (Oikea reuna)
        self.scrollable_list = ctk.CTkScrollableFrame(self.sidebar_content,
                                                     label_text=get_localized_text("gui_news_feed", self.lang))
        self.scrollable_list.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.scrollable_list._scrollbar.configure(width=8)

        # 2. Luodaan suodatin-ikonit pystyriviin
        current_news = self.memory.get_report()
        for cat, style in self.category_styles.items():
            count = len(current_news) if cat == "Default" else sum(1 for e in current_news if e.get('category') == cat)

            btn = ctk.CTkButton(
                self.icon_bar,
                text=f"{style['icon']}\n{count}",
                width=40,
                height=45,
                fg_color=style['color'],
                hover_color="#444444",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda c=cat: self.filter_news(c)
            )
            btn.pack(pady=3, anchor="center")
            self.filter_buttons[cat] = btn

        # --- OIKEA PANEELI ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.personality = JeevesPersonality()

        self.jeeves_panel = ctk.CTkFrame(self.content, fg_color=("#ebebeb", "#2b2b2b"), corner_radius=10)
        self.jeeves_panel.pack(fill="x", pady=(0, 20))

        self.avatar_frame = ctk.CTkFrame(self.jeeves_panel, width=80, height=80, fg_color="transparent")
        self.avatar_frame.pack(side="left", padx=15, pady=10)
        self.avatar_frame.pack_propagate(False)

        image_path = os.path.join(current_dir, "resources", "jeeves_avatar.png")
        try:
            self.jeeves_image = ctk.CTkImage(
                light_image=Image.open(image_path),
                dark_image=Image.open(image_path),
                size=(70, 70)
            )
            self.avatar_label = ctk.CTkLabel(self.avatar_frame, image=self.jeeves_image, text="")
        except Exception as e:
            self.avatar_label = ctk.CTkLabel(self.avatar_frame, text="👤", font=ctk.CTkFont(size=40))

        self.avatar_label.pack(expand=True)

        self.speech_bubble = ctk.CTkLabel(
            self.jeeves_panel,
            text=self.personality.get_greeting(self.lang),
            font=ctk.CTkFont(size=14, slant="italic"),
            wraplength=600,
            justify="left",
            anchor="w"
        )
        self.speech_bubble.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=10)

        self.title_var = ctk.StringVar(value=get_localized_text("gui_select_news", self.lang))
        self.title_label = ctk.CTkLabel(self.content, textvariable=self.title_var,
                                        font=ctk.CTkFont(size=22, weight="bold"), wraplength=700, justify="left")
        self.title_label.pack(pady=(0, 10), anchor="w")

        self.meta_var = ctk.StringVar(value="")
        self.meta_label = ctk.CTkLabel(self.content, textvariable=self.meta_var, font=ctk.CTkFont(size=12, slant="italic"))
        self.meta_label.pack(pady=(0, 10), anchor="w")

        self.summary_text = ctk.CTkTextbox(self.content, font=ctk.CTkFont(size=15), wrap="word")
        self.summary_text.pack(expand=True, fill="both", pady=5)
        self.summary_text.configure(state="disabled")

        self.button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=5)

        self.open_web_btn = ctk.CTkButton(self.button_frame,
                                          text=get_localized_text("gui_open_web", self.lang),
                                          command=self.open_url, state="disabled")
        self.open_web_btn.pack(side="right")

        self.console_label = ctk.CTkLabel(self.content,
                                          text=get_localized_text("gui_system_log", self.lang),
                                          font=ctk.CTkFont(size=11, weight="bold"))
        self.console_label.pack(anchor="w", pady=(10, 0))

        self.console_box = ctk.CTkTextbox(self.content, height=150, font=("Consolas", 11), fg_color="#1a1a1a", text_color="#00ff00")
        self.console_box.pack(fill="x", pady=(5, 0))
        self.console_box.configure(state="disabled")

        sys.stdout = ConsoleRedirector(self.console_box)
        self.current_entry = None

        # Luodaan pieni 100 millisekunnin viive, jotta loki ehtii mukaan
        self.after(100, self.start_up_routines)

    def start_up_routines(self):
        """Suorittaa alkutoimet niin, että ne ehtivät lokiin saakka."""
        startup_msg = get_localized_text("gui_startup_msg", self.lang)
        print(startup_msg)
        self.load_news()
        self.check_for_app_updates()

    def check_for_app_updates(self):
        import threading
        from jeeves_logic import PersonalityEngine
        from jeeves_updater import get_remote_version

    def task():
        # Suoritetaan verkkotarkistus taustalla
        update_data = get_remote_version(CURRENT_VERSION)

        # Haetaan kohtelias tervehdys
        greeting = PersonalityEngine.get_time_of_day_greeting()

    def get_translated_category(self, raw_cat):
        # Haetaan ui-osio
        ui_texts = get_localized_text("ui", self.lang) or {}
        # Haetaan category-sanakirja ui-osion sisältä
        cat_map = ui_texts.get("category", {})
        # Palautetaan käännös tai alkuperäinen jos käännöstä ei löydy
        return cat_map.get(raw_cat, raw_cat)

    def filter_news(self, category):
        # 1. Määritetään oletukset
        localized_cat = category
        msg_template = "Etsitään uutisia {category}-kategoriasta, sir."

        try:
            # 2. Haetaan kieli (oletus 'fi')
            current_lang = self.lang if hasattr(self, 'lang') else 'fi'

            # 3. Luetaan personality.json suoraan (varmistetaan tiedostopolku)
            import json
            import os
            json_path = os.path.join("resources", "personality.json")

            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Navigoidaan syvälle JSON-rakenteeseen: fi -> ui -> category
                lang_data = data.get(current_lang, {})
                ui_data = lang_data.get("ui", {})

                # Haetaan lausepohja
                msg_template = ui_data.get("gui_filtering_msg", msg_template)

                # Haetaan kategorian käännös
                cat_translations = ui_data.get("category", {})
                localized_cat = cat_translations.get(category, category)
        except Exception as e:
            print(f"DEBUG: Virhe käännöksessä: {e}")

        # 4. Päivitetään puhekupla
        final_msg = msg_template.replace("{category}", localized_cat)
        self.speech_bubble.configure(text=final_msg)

        # 5. Suoritetaan varsinainen haku
        self.load_news(filter_cat=category)

    def check_priority(self, title):
        # Haetaan sanat configista
        priority_keywords = self.get_keywords_from_config()

        # Määritellään oikeasti kriittiset termit
        critical_terms = ["CVE", "CRITICAL", "SECURITY", "VULNERABILITY"]

        title_upper = title.upper()
        for word in priority_keywords:
            if word.upper() in title_upper:
                # Jos sana on kriittisellä listalla -> [!!!]
                if any(crit in word.upper() for crit in critical_terms):
                    return True, "[!!!]"
                # Muutoin se on vain kiinnostava -> [⭐]
                return True, "[⭐]"

        return False, ""

    def update_speech_bubble(self, title):
        is_priority, prefix = self.check_priority_status(title)

        if is_priority:
            # TÄMÄ on se teidän toivoma lause:
            msg = "Sir, huomasin uutisen, joka liittyy erityisesti teidän prioriteetteihinne."
            self.speech_bubble.configure(text=msg)
        else:
            # Tavallinen tervehdys
            from jeeves_logic import get_localized_text
            msg = get_localized_text("ui.gui_select_news", self.lang)
            self.speech_bubble.configure(text=msg)

    def load_news(self, filter_cat=None):
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()
        try:
            self.memory = JeevesMemory()
            entries = self.memory.get_report(days=7)
            prio_keywords = get_priority_keywords()
            entries.sort(key=lambda x: any(k in x['title'].lower() for k in prio_keywords), reverse=True)

            for entry in entries:
                cat_name = entry.get('category', 'Default')
                if filter_cat and filter_cat != "Default" and cat_name != filter_cat:
                    continue

                is_priority = any(k in entry['title'].lower() for k in prio_keywords)
                orig_title = entry.get('title', 'No Title')
                disp_title = (orig_title[:38] + "..") if len(orig_title) > 38 else orig_title
                style = self.category_styles.get(cat_name, self.category_styles.get("Default", {"icon": "•", "color": "transparent"}))

                bg_color = "#3d1414" if is_priority else style['color']
                icon = "⚠️" if is_priority else style['icon']

                btn = ctk.CTkButton(self.scrollable_list,
                                    text=f"{icon} {disp_title}",
                                    anchor="w",
                                    fg_color=bg_color,
                                    command=lambda e=entry: self.show_details(e))
                btn.pack(fill="x", pady=2, padx=5)
        except Exception as e:
            print(f"[!] Error loading news: {e}")

    def show_details(self, entry):
        self.current_entry = entry
        self.title_var.set(entry['title'])
        self.open_web_btn.configure(state="normal")
        category = entry.get('category', 'Default')
        priority_keywords = get_priority_keywords()
        priority = "Critical" if any(k in entry['title'].lower() for k in priority_keywords) else "Normal"
        self.speech_bubble.configure(text=self.personality.get_commentary(category, priority, self.lang))

        intro = get_localized_text("analysis_intro", self.lang)
        source_label = get_localized_text("ui.sources_label", self.lang) or "LÄHTEET JA VIITTEET:"
        full_display_text = f"{intro}\n\n{entry.get('summary', '').strip()}\n"
        full_display_text += f"\n{'-'*60}\n{source_label}\n• Lähde: {entry.get('url', '#')}\n• Kategoria: {category}\n{'-'*60}"

        self.summary_text.configure(state="normal")
        self.summary_text.delete("0.0", "end")
        self.summary_text.insert("0.0", full_display_text)
        self.summary_text.configure(state="disabled")

    def open_url(self):
        if self.current_entry:
            webbrowser.open(self.current_entry['url'])

    def run_logic_task(self):
        """Suorittaa uutisten haun taustalla ja lukee lokia UTF-8 muodossa."""
        # 1. Pakotetaan ympäristö käyttämään UTF-8 (korjaa ääkköset)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            # 2. Käynnistetään prosessi parannetuilla asetuksilla
            process = subprocess.Popen(
                [sys.executable, "jeeves.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8", # Varmistaa, että Python lukee tekstin oikein
                env=env
            )

            # 3. Luetaan lokia reaaliajassa
            if process.stdout:
                for line in process.stdout:
                    print(line, end="") # Ohjautuu vihreään laatikkoon

            process.wait()
        except Exception as e:
            print(f"[!] Virhe uutisten haussa: {e}")

        # 4. Palataan pääsäikeeseen päivittämään lista
        self.after(0, self.finish_refresh)

    def on_refresh(self):
        self.console_box.configure(state="normal")
        self.console_box.delete("0.0", "end")
        self.console_box.configure(state="disabled")
        self.refresh_btn.configure(state="disabled", text=get_localized_text("gui_refreshing", self.lang))
        threading.Thread(target=self.run_logic_task, daemon=True).start()

    def finish_refresh(self):
        self.refresh_btn.configure(state="normal", text=get_localized_text("gui_refresh", self.lang))
        self.memory = JeevesMemory()
        current_news = self.memory.get_report()
        for cat, style in self.category_styles.items():
            if cat in self.filter_buttons:
                count = len(current_news) if cat == "Default" else sum(1 for e in current_news if e.get('category') == cat)
                self.filter_buttons[cat].configure(text=f"{style['icon']}\n{count}")
        self.load_news()

    def check_for_app_updates(self):
        import threading
        from jeeves_logic import get_time_based_greeting, get_localized_text
        from jeeves_updater import check_for_updates

        def task():
            update_data = check_for_updates(CURRENT_VERSION)
            greeting = get_time_based_greeting(self.lang)

            if update_data:
                new_ver, _ = update_data
                # Tehdään dynaaminen haku JSON-tiedostosta
                raw_msg = get_localized_text("update_available", self.lang)
                msg = raw_msg.replace("{greeting}", greeting).replace("{version}", new_ver)
            else:
                raw_msg = get_localized_text("all_systems_ok", self.lang)
                msg = raw_msg.replace("{greeting}", greeting)

            self.after(0, lambda: self.speech_bubble.configure(text=msg))

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    app = JeevesGUI()
    app.mainloop()
