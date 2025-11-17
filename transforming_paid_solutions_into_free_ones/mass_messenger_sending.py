import customtkinter as ctk

def simple():
    simple = ctk.CTk()
    simple.geometry("450x450")
    simple_mensage = ctk.CTkLabel(simple, text="Mensagem:")
    simple_mensage.pack(pady=10)
    simple_text = ctk.CTkEntry(simple, placeholder_text="Digite aqui sua mensagem.")
    simple_text.pack(pady=10)
    simple.mainloop()

def app():
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Envio de mensagens do whatsapp em massa")
    app.geometry("450x450")

    mensagem_simple = ctk.CTkLabel(app, text="Mensagem simples")
    mensagem_simple.pack(pady=10)
    button_simple = ctk.CTkButton(app, text="Simples", command=simple)
    button_simple.pack(pady=10)

    mensagem_image = ctk.CTkLabel(app, text="Mensagem com imagem")
    mensagem_image.pack(pady=20)
    button_image = ctk.CTkButton(app, text="Imagem", command=simple)
    button_image.pack(pady=10)
    app.mainloop()

app()