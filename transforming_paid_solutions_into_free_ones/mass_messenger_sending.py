import csv
import customtkinter as ctk
import os
import time
from tkinter import filedialog as fd
from pywa import WhatsApp

GLOBAL_NUMBERS_LIST = []
GLOBAL_IMAGE_PATH = None

def send_image_message (list_numbers, image_path, caption_text, target_label):
    PHONE_ID = os.environ.get("WA_PHONE_ID") 
    TOKEN = os.environ.get("WA_TOKEN")   

    if not PHONE_ID or not TOKEN:
        target_label.configure(text="ERRO: Variáveis de ambiente WA_PHONE_ID ou WA_TOKEN não configuradas.")
        return 

    if not list_numbers:
        target_label.configure(text="ERRO: Nenhuma lista de números válida foi carregada do CSV.")
        return
    
    if not image_path or not os.path.exists(image_path):
        target_label.configure(text="ERRO: Caminho de imagem inválido ou arquivo inexistente.")
        return

    whats = WhatsApp(phone_id=PHONE_ID, token=TOKEN)
    
    sucess_count = 0
    fail_count = 0

    for index, number in enumerate(list_numbers):
        target_label.configure(text=f"Enviando imagem ({index + 1}/{len(list_numbers)}): {number}")
        target_label.update_idletasks() 
        
        try:
            message_id_response = whats.send_image(
                to=number,
                image=image_path,
                caption=caption_text
            )
            
            msg_id = message_id_response.get('messages', [{}]).get('id', 'N/A')
            print(f"Sucesso para {number}. ID: {msg_id}")
            sucess_count += 1
            time.sleep(1) 

        except Exception as e:
            print(f"Ocorreu um erro ao enviar para {number}: {e}")
            fail_count += 1

    target_label.configure(text=f"Processo concluído. Sucessos: {sucess_count}, Falhas: {fail_count}")

def send_message (list_numbers, message_text, target_label):
    PHONE_ID = os.environ.get("WA_PHONE_ID") 
    TOKEN = os.environ.get("WA_TOKEN")

    if not PHONE_ID or not TOKEN:
        error_msg = "ERRO: As variáveis de ambiente WA_PHONE_ID ou WA_TOKEN não estão configuradas."
        print(error_msg)
        target_label.configure(text=error_msg)
        return 

    if not list_numbers:
        target_label.configure(text="ERRO: Nenhuma lista de números válida foi carregada do CSV, por gentileza deixe a lista na segunda coluna.")
        return

    whats = WhatsApp(phone_id=PHONE_ID, token=TOKEN)
    
    sucess_count = 0
    fail_count = 0

    for index, number in enumerate(list_numbers):
        target_label.configure(text=f"Enviando ({index + 1}/{len(list_numbers)}): {number}")
        target_label.update_idletasks() 
        
        try:
            message_id_response = whats.send_message(
                to=number,
                text=message_text
            )
            msg_id = message_id_response.get('messages', [{}])[0].get('id', 'N/A')
            print(f"Sucesso para {number}. ID: {msg_id}")
            sucess_count += 1

            time.sleep(1) 

        except Exception as e:
            print(f"Ocorreu um erro ao enviar para {number}: {e}")
            fail_count += 1

    target_label.configure(text=f"Processo concluído. Sucessos: {sucess_count}, Falhas: {fail_count}")

def open_image_file(target_label):
    global GLOBAL_IMAGE_PATH
    filepath = fd.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
    )

    if not filepath:
        target_label.configure(text="Nenhuma imagem selecionada")
        GLOBAL_IMAGE_PATH = None
        return

    GLOBAL_IMAGE_PATH = filepath
    file_name = filepath.split('/')[-1]
    target_label.configure(text=f"Imagem carregada: {file_name}")

def open_arc (target_label):
    global GLOBAL_NUMBERS_LIST

    GLOBAL_NUMBERS_LIST = []

    filepath = fd.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if not filepath:
        target_label.configure(text="Nenhum arquivo selecionado")
        return

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
                    number = (i[1].strip())
                    if not number.startswith('+'):
                       number = '+55' + number # Isso pode ser perigoso se você tiver números de vários países
                    GLOBAL_NUMBERS_LIST.append(number)
                else:
                    print(f"Aviso: Linha {line} não tem dados suficientes: {i}")
                line += 1

def validate_and_send_image(textbox_widget, placeholder_text, state_label):
    caption = textbox_widget.get("1.0", "end-1c") 
    
    if not GLOBAL_NUMBERS_LIST:
        state_label.configure(text="Erro: Carregue um CSV antes de enviar.")
        return
    
    if not GLOBAL_IMAGE_PATH:
        state_label.configure(text="Erro: Carregue uma imagem antes de enviar.")
        return

    state_label.configure(text="Iniciando processo de envio de imagem...")
    
    send_image_message(GLOBAL_NUMBERS_LIST, GLOBAL_IMAGE_PATH, caption, state_label)

def validate_and_send(textbox_widget, placeholder_text, target_label):
    message = textbox_widget.get("1.0", "end-1c") 
    
    if message == placeholder_text or len(message.strip()) == 0:
        target_label.configure(text="Erro de Validação. Por favor, digite uma mensagem válida.")
        return

    if len(message) > 500:
        target_label.configure(text="A mensagem ultrapassa o limite, por favor reduza-a!")
        return
    
    if not GLOBAL_NUMBERS_LIST:
        target_label.configure(text="Erro de Validação. Por favor, carregue um arquivo CSV válido.")
        return
    
    print(f"Mensagem válida. Iniciando envio para {len(GLOBAL_NUMBERS_LIST)} destinatários.")
    target_label.configure(text="Iniciando processo de envio...")

    send_message(GLOBAL_NUMBERS_LIST, message, target_label)

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

def go_back(current_window, parent_window, close_all=False):
    current_window.destroy()
    if close_all:
        parent_window.destroy()
    else:
        parent_window.deiconify()

def image_window(parent_window):
    
    image_window = ctk.CTk()
    image_window.title("Envio de mensagens com imagem em massa")
    image_window.geometry("450x500")

    image_window.protocol("WM_DELETE_WINDOW", lambda: go_back(image_window, parent_window, close_all=True))

    caption_label = ctk.CTkLabel(image_window, text="Legenda da Imagem (Opcional):")
    caption_label.pack(pady=10)

    PLACEHOLDER_CAPTION = "Digite a legenda da imagem (max 500 chars)..."
    image_caption_textbox = ctk.CTkTextbox(image_window, width=400, height=100, wrap="word", border_width=2, corner_radius=10, text_color=("gray70", "gray40"))
    image_caption_textbox.pack(pady=10)

    count_caption= ctk.CTkLabel(image_window, text=f"0/500", font=ctk.CTkFont(size=12), text_color=("gray50", "gray40"))
    count_caption.pack(anchor='e', padx=25)

    image_caption_textbox.insert("0.0", PLACEHOLDER_CAPTION)
    image_caption_textbox.bind("<FocusIn>", lambda event: handle_focus_in(event, image_caption_textbox, PLACEHOLDER_CAPTION))
    image_caption_textbox.bind("<KeyRelease>", lambda event: update_char_count(event, image_caption_textbox, count_caption))

    img_button = ctk.CTkButton(image_window, text="Selecionar Imagem", command=lambda: open_image_file(image_label))
    img_button.pack(pady=10)
    image_label = ctk.CTkLabel(image_window, text="Nenhuma imagem selecionada", wraplength=350)
    image_label.pack(pady=10)

    arq_mensage = ctk.CTkLabel(image_window, text="Insira apenas arquivos CSV separados por ;")
    arq_mensage.pack(pady=10)
    arq_button = ctk.CTkButton(image_window, text="Selecionar Arquivo CSV", command=lambda: open_arc(file_label))
    arq_button.pack(pady=10)

    file_label = ctk.CTkLabel(image_window, text="Nenhum arquivo selecionado", wraplength=350)
    file_label.pack(pady=10)

    button_frame = ctk.CTkFrame(image_window)
    button_frame.pack(pady=20)
    back_button = ctk.CTkButton(button_frame, text="Voltar", command=lambda: go_back(image_window, parent_window))
    back_button.pack(side='left', padx=10)
    
    send_button = ctk.CTkButton(button_frame, text="Enviar Imagem", command=lambda: validate_and_send_image(image_caption_textbox, PLACEHOLDER_CAPTION, state_label))
    send_button.pack(side='left', padx=10)

    state_label = ctk.CTkLabel(image_window, text="")
    state_label.pack(pady=10)
    
    image_window.mainloop()

def simple_window(parent_window):

    simple_window = ctk.CTk()
    simple_window.title("Envio de mensagens simples em massa")
    simple_window.geometry("450x500")

    simple_window.protocol("WM_DELETE_WINDOW", lambda: go_back(simple_window, parent_window, close_all=True))

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

    send_button = ctk.CTkButton(button_frame, text="Enviar", command=lambda: validate_and_send(simple_textbox, PLACEHOLDER_MSG, state_label))
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

    button_image = ctk.CTkButton(app_window, text="Imagem", command=lambda: [app_window.withdraw(), image_window(app_window)])
    button_image.pack(pady=10)

    app_window.mainloop()

app_window()