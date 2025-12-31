import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x240")
app.title("Jeeves Test")
label = ctk.CTkLabel(app, text="If you see this, the library is working, sir!")
label.pack(pady=20)
app.mainloop()
