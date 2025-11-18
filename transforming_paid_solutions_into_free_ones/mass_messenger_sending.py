import csv
import customtkinter as ctk
from tkinter import filedialog as fd

def open_arc (target_label):
    filepath = fd.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if not filepath:
        target_label.configure(text="Nenhum arquivo selecionado")
        return

    list_names = []
    list_numbers = []

    with open(filepath, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=";")

        file_name = filepath.split('/')[-1]
        new_file_label = f"Arquivo carregado: {file_name}"     
        target_label.configure(text=new_file_label)

        line = 0
        for i in csv_reader:
            if line == 0:
                print(f"\tColunas: {' '.join(i)}")
                line += 1
            else:
                if len(i) >= 2:
                    list_names.append(i[0])
                    list_numbers.append(i[1])
                else:
                    print(f"Aviso: Linha {line} não tem dados suficientes: {i}")
                line += 1

    return (list_names, list_numbers)

def validar_e_enviar(textbox_widget, placeholder_text, target_label):
    mensage = textbox_widget.get("1.0", "end-1c") 
    
    if mensage == placeholder_text or len(mensage.strip()) == 0:
        target_label.configure(text="Erro de Validação. Por favor, digite uma mensagem válida.")
        return

    if len(mensage) > 500:
        target_label.configure(text="A mensagem ultrapassa o limite, por favor reduza-a!")
        return
    else:
        print(f"Mensagem válida enviada ({len(mensage)}")

def handle_focus_in(event, textbox_widget, placeholder_text):
    current_text = textbox_widget.get("1.0", "end-1c")
    if current_text == placeholder_text:
        textbox_widget.delete("1.0", "end")
        textbox_widget.configure(text_color=("black", "white")) 

def update_char_count(event, textbox_widget, count_label):
    mensagem = textbox_widget.get("1.0", "end-1c")
    current_length = len(mensagem)
    max_length = 500
    
    count_label.configure(text=f"{current_length}/{max_length}")

    if current_length > max_length:
        count_label.configure(text_color="red")
    else:
        count_label.configure(text_color=("gray50", "gray40"))

def go_back(current_window, parent_window):
    current_window.destroy()
    parent_window.deiconify()

def simple_window(parent_window):

    simple_window = ctk.CTk()
    simple_window.title("Envio de mensagens simples em massa")
    simple_window.geometry("450x500")

    simple_mensage = ctk.CTkLabel(simple_window, text="Mensagem:")
    simple_mensage.pack(pady=10)

    PLACEHOLDER_MSG = "Digite aqui sua mensagem..."

    simple_textbox = ctk.CTkTextbox(simple_window, width=400, height=150, wrap="word",border_width=2, corner_radius=10,text_color=("gray70", "gray40"))
    simple_textbox.pack(pady=10)

    count_label = ctk.CTkLabel(simple_window, text=f"0/500", font=ctk.CTkFont(size=12), text_color=("gray50", "gray40"))
    count_label.pack(anchor='e', padx=25)

    simple_textbox.insert("0.0", PLACEHOLDER_MSG)
    simple_textbox.bind("<FocusIn>", lambda event: handle_focus_in(event, simple_textbox, PLACEHOLDER_MSG))
    simple_textbox.bind("<KeyRelease>", lambda event: update_char_count(event, simple_textbox, count_label))


    arq_mensage = ctk.CTkLabel(simple_window, text="Insira apenas arquivos CSV separados por ;")
    arq_mensage.pack(pady=10)
    arq_button = ctk.CTkButton(simple_window, text="Selecionar Arquivo CSV", command=lambda: open_arc(file_label))
    arq_button.pack(pady=10)

    file_label = ctk.CTkLabel(simple_window, text="Nenhum arquivo selecionado", wraplength=350)
    file_label.pack(pady=10)

    button_frame = ctk.CTkFrame(simple_window)
    button_frame.pack(pady=20)

    back_button = ctk.CTkButton(button_frame, text="Voltar", command=lambda: go_back(simple_window, parent_window))
    back_button.pack(side='left', padx=10)

    send_button = ctk.CTkButton(button_frame, text="Enviar", command=lambda: validar_e_enviar(simple_textbox, PLACEHOLDER_MSG, state_label))
    send_button.pack(side='left', padx=10)

    state_label = ctk.CTkLabel(simple_window, text="")
    state_label.pack(pady=10)
    
    simple_window.mainloop()

def app_window():
    ctk.set_appearance_mode("system")

    app_window = ctk.CTk()
    app_window.title("Envio de mensagens em massa")
    app_window.geometry("350x250")

    mensagem_simple = ctk.CTkLabel(app_window, text="Mensagem simples")
    mensagem_simple.pack(pady=10)

    button_simple = ctk.CTkButton(app_window, text="Simples", command=lambda: [app_window.withdraw(), simple_window(app_window)])
    button_simple.pack(pady=10)

    mensagem_image = ctk.CTkLabel(app_window, text="Mensagem com imagem")
    mensagem_image.pack(pady=20)

    button_image = ctk.CTkButton(app_window, text="Imagem")
    button_image.pack(pady=10)

    app_window.mainloop()

app_window()