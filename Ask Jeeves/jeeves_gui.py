# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler UI
File: ask_jeeves.py and jeeves_logic.py, jeeves_gui.py
Author: [Tuomas Lähteenmäki]
Version: v2.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Website:

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
from jeeves_logic import MEMORY_FILE, METADATA_FILE, JeevesMemory, get_localized_text, get_priority_keywords

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

        # Alustetaan muisti kielen hakemista varten
        self.memory = JeevesMemory()
        self.lang = self.memory.lang # Haetaan kieliasetus automaattisesti

        # Asetetaan ikkunan otsikko metadatasta
        self.title(get_localized_text("gui_title", self.lang))
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")

        # Asetetaan ikkunan ruudukon säännöt
        self.grid_columnconfigure(0, weight=0, minsize=320) # Vasen: Ei kasva, vähintään 320px
        self.grid_columnconfigure(1, weight=1)             # Oikea: Vie kaiken lopun tilan
        self.grid_rowconfigure(0, weight=1)

        # --- VASEN PANEELI (KIINTEÄ) ---
        # Asetetaan width=300 tai haluamanne leveys pikseleinä
        self.sidebar = ctk.CTkFrame(self, width=320) # Kiinteä leveys
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False) # Lukitus: ei muuta kokoaan sisällön mukaan


        self.refresh_btn = ctk.CTkButton(self.sidebar,
                                        text=get_localized_text("gui_refresh", self.lang),
                                        command=self.on_refresh)
        self.refresh_btn.pack(pady=20, padx=10, fill="x")

        self.scrollable_list = ctk.CTkScrollableFrame(self.sidebar,
                                                     label_text=get_localized_text("gui_news_feed", self.lang))
        self.scrollable_list.pack(expand=True, fill="both", padx=5, pady=5)

        # --- OIKEA PANEELI ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

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

        # --- JÄRJESTELMÄLOKI ---
        self.console_label = ctk.CTkLabel(self.content,
                                          text=get_localized_text("gui_system_log", self.lang),
                                          font=ctk.CTkFont(size=11, weight="bold"))
        self.console_label.pack(anchor="w", pady=(10, 0))

        self.console_box = ctk.CTkTextbox(self.content, height=150, font=("Consolas", 11), fg_color="#1a1a1a", text_color="#00ff00")
        self.console_box.pack(fill="x", pady=(5, 0))
        self.console_box.configure(state="disabled")

        sys.stdout = ConsoleRedirector(self.console_box)

        self.current_entry = None
        self.load_news()
        print(get_localized_text("gui_loaded", self.lang))

    def load_news(self):
        # Tyhjennetään vanhat uutiset listasta
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()

        try:
            self.memory = JeevesMemory()
            entries = self.memory.get_report(days=7)

            # --- DYNAAMINEN PRIORISOINTI ---
            prio_keywords = get_priority_keywords()
            # Lajitellaan: prioriteetit ensin
            entries.sort(key=lambda x: any(k in x['title'].lower() for k in prio_keywords), reverse=True)

            for entry in entries:
                is_priority = any(k in entry['title'].lower() for k in prio_keywords)

                # OTSIKON KATKAISU (Estää ruudun hyppimisen)
                orig_title = entry.get('title', 'No Title')
                disp_title = (orig_title[:42] + "..") if len(orig_title) > 42 else orig_title

                btn_text = f"{'⚠️ ' if is_priority else '• '}{disp_title}"

                # Pidetään värit tyylikkäänä
                btn = ctk.CTkButton(self.scrollable_list,
                                    text=btn_text,
                                    anchor="w",
                                    fg_color="transparent" if not is_priority else "#3d1414",
                                    hover_color="#5a1d1d" if is_priority else None,
                                    command=lambda e=entry: self.show_details(e))
                btn.pack(fill="x", pady=2, padx=5)

        except Exception as e:
            print(f"[!] Error loading news: {e}")

    def show_details(self, entry):
        self.current_entry = entry
        self.title_var.set(entry['title'])
        self.open_web_btn.configure(state="normal")

        # 1. Haetaan lokalisoidut raamit ja fraasit
        intro = get_localized_text("analysis_intro", self.lang)
        greetings = get_localized_text("common_greetings", self.lang)

        # Varmistetaan, että greetings on lista (jos metadatassa on virhe)
        if isinstance(greetings, str):
            greetings = [greetings]
        elif not greetings:
            greetings = []

        # 2. Puhdistetaan raaka teksti hovimestarin fraaseista
        cleaned = entry.get('summary', '')

        # Poistetaan intro, jos se on jo tallennettu summaryyn (estetään tuplaus)
        cleaned = cleaned.replace(intro, "").strip()

        # Poistetaan listatut tervehdykset
        for phrase in greetings:
            cleaned = cleaned.replace(phrase, "").strip()

        # 3. MUOTOILU: Pidetään teksti siistinä mutta juoksevana
        final_text = cleaned.strip()

        # 4. Kootaan lopputulos (Intro ja puhdas sisältö)
        full_display_text = f"{intro}\n\n{final_text}"

        # 5. Päivitys käyttöliittymään
        self.summary_text.configure(state="normal")
        self.summary_text.delete("0.0", "end")
        self.summary_text.insert("0.0", full_display_text)
        self.summary_text.configure(state="disabled")

    def open_url(self):
        if self.current_entry:
            webbrowser.open(self.current_entry['url'])

    def on_refresh(self):
        self.refresh_btn.configure(state="disabled", text=get_localized_text("gui_refreshing", self.lang))
        print(get_localized_text("gui_refresh_start", self.lang))
        threading.Thread(target=self.run_logic_task, daemon=True).start()

    def run_logic_task(self):
        process = subprocess.Popen([sys.executable, "jeeves.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        self.after(0, self.finish_refresh)

    def finish_refresh(self):
        self.refresh_btn.configure(state="normal", text=get_localized_text("gui_refresh", self.lang))
        self.load_news()
        print(get_localized_text("gui_refresh_done", self.lang))

if __name__ == "__main__":
    app = JeevesGUI()
    app.mainloop()
