import csv
import customtkinter as ctk
import logging
from logging.handlers import RotatingFileHandler
import os
import phonenumbers
import sys
import time
import threading
from tkinter import filedialog as fd
from pywa import WhatsApp

POSSIBLE_HEADERS = ["telefone", "telefones", "número", "números", "whatsapp", "whatsapp", "phone", "phone number", "celular"]
GLOBAL_NUMBERS_LIST = []
GLOBAL_IMAGE_PATH = None
logger = None

def setup_log ():
    """
    Configura o sistema de logging para a aplicação.

    Cria um logger global com:
    - Console handler (INFO)
    - Rotating file handler (DEBUG) em logs/mass_messenger_sending.log
    - Formatação padrão: timestamp, nome do logger, nível, mensagem

    Retorna:
        logging.Logger: logger configurado
    """
        
    global logger

    logger = logging.getLogger("MassMessengerApp")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger_filename = "mass_messenger_sending.log"
    logger_dir = os.path.join("transforming_paid_solutions_into_free_ones", "mass_messenger_sending", "logs")
    logger_path = os.path.join(os.getcwd(), logger_dir, logger_filename)

    if not os.path.exists(logger_dir):
        os.makedirs(logger_dir)

    file_handler = RotatingFileHandler(
    logger_path,
    maxBytes = 300000,
    backupCount = 5
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Sistema de logging configurado com sucesso.")
    return logger

def send_image_message (list_numbers, image_path, caption_text, target_label, progress_bar=None):
    """
    Envia uma imagem via WhatsApp para uma lista de números.

    Parâmetros:
        list_numbers (list): Lista de números de telefone no formato E.164
        image_path (str): Caminho do arquivo de imagem a ser enviado
        caption_text (str): Texto da legenda da imagem
        target_label (ctk.CTkLabel): Label da GUI para mostrar status
        progress_bar (ctk.CTkProgressBar, opcional): Barra de progresso para atualizar envio
    """

    PHONE_ID = os.environ.get("WA_PHONE_ID") 
    TOKEN = os.environ.get("WA_TOKEN")   

    if not PHONE_ID or not TOKEN:
        error_msg = "ERRO: Variaveis de ambiente WA_PHONE_ID ou WA_TOKEN nao configuradas."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return 

    if not list_numbers:
        error_msg = "ERRO: Nenhuma lista de numeros valida foi carregada do CSV."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return
    
    if not image_path or not os.path.exists(image_path):
        error_msg = "ERRO: Caminho de imagem invalido ou arquivo inexistente."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return

    whats = WhatsApp(phone_id = PHONE_ID, token = TOKEN)
    logger.info(f"Iniciando o envio de imagens para {len(list_numbers)} destinatarios.")
    
    sucess_count = 0
    fail_count = 0
    total_numbers = len(list_numbers)

    for index, number in enumerate(list_numbers):
        target_label.configure(text=f"Enviando imagem ({index + 1}/{len(list_numbers)}): {number}")
        target_label.update_idletasks() 
        
        try:
            message_id_response = whats.send_image(
                to=number,
                image=image_path,
                caption=caption_text
            )
            
            messages = message_id_response.get("messages", [])
            msg_id = messages[0].get("id", "N/A") if messages else "N/A"
            logger.info(f"Sucesso para {number}. ID: {msg_id}")
            sucess_count += 1
            time.sleep(0.5) 

        except Exception as e:
            logger.error(f"Ocorreu um erro ao enviar para {number}: {e}", exc_info=True)
            fail_count += 1

        if progress_bar:
            progress = (index + 1) / total_numbers
            progress_bar.set(progress)
            target_label.update_idletasks()

    sucess_msg = f"Processo concluido. Sucessos: {sucess_count}, Falhas: {fail_count}"
    logger.info(sucess_msg)
    target_label.configure(text=sucess_msg)

    if progress_bar:
        progress_bar.set(1.0)

def send_message (list_numbers, message_text, target_label, progress_bar=None):
    """
    Envia uma mensagem de texto via WhatsApp para uma lista de números.

    Parâmetros:
        list_numbers (list): Lista de números de telefone no formato E.164
        message_text (str): Texto da mensagem a ser enviado
        target_label (ctk.CTkLabel): Label da GUI para mostrar status
        progress_bar (ctk.CTkProgressBar, opcional): Barra de progresso para atualizar envio
    """

    PHONE_ID = os.environ.get("WA_PHONE_ID") 
    TOKEN = os.environ.get("WA_TOKEN")

    if not PHONE_ID or not TOKEN:
        error_msg = "ERRO: Variaveis de ambiente WA_PHONE_ID ou WA_TOKEN nao configuradas."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return 

    if not list_numbers:
        error_msg = "ERRO: Nenhuma lista de numeros valida foi carregada do CSV."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return

    whats = WhatsApp(phone_id=PHONE_ID, token=TOKEN)
    logger.info(f"Iniciando o envio de mensagens para {len(list_numbers)} destinatarios.")
    
    sucess_count = 0
    fail_count = 0
    total_numbers = len(list_numbers)

    for index, number in enumerate(list_numbers):
        target_label.configure(text = f"Enviando ({index + 1}/{len(list_numbers)}): {number}")
        target_label.update_idletasks() 
        
        try:
            message_id_response = whats.send_message(
                to=number,
                text=message_text
            )
            messages = message_id_response.get("messages", [])
            msg_id = messages[0].get("id", "N/A") if messages else "N/A"
            logger.info(f"Sucesso para {number}. ID: {msg_id}")
            sucess_count += 1

            time.sleep(0.5) 

        except Exception as e:
            logger.error(f"Ocorreu um erro ao enviar para {number}: {e}", exc_info=True)
            fail_count += 1

        if progress_bar:

            progress = (index + 1) / total_numbers
            progress_bar.set(progress)
            target_label.update_idletasks()

    sucess_msg = f"Processo concluído. Sucessos: {sucess_count}, Falhas: {fail_count}"
    logger.info(sucess_msg)
    target_label.configure(text=sucess_msg)

    if progress_bar:
        progress_bar.set(1.0)

def open_image_file(target_label):
    """
    Abre um seletor de arquivo para escolher uma imagem.

    Atualiza a variável global GLOBAL_IMAGE_PATH com o caminho da imagem selecionada.

    Parâmetros:
        target_label (ctk.CTkLabel): Label da GUI para mostrar o nome da imagem selecionada
    """

    global GLOBAL_IMAGE_PATH
    filepath = fd.askopenfilename(
        filetypes = [("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
    )

    if not filepath:
        target_label.configure(text="Nenhuma imagem selecionada")
        GLOBAL_IMAGE_PATH = None
        return

    GLOBAL_IMAGE_PATH = filepath
    file_name = filepath.split('/')[-1]
    target_label.configure(text=f"Imagem carregada: {file_name}")

def open_csv_file (target_label, selected_delimiter_text):
    """
    Abre um arquivo CSV, identifica a coluna de números de telefone e armazena os números válidos.

    Parâmetros:
        target_label (ctk.CTkLabel): Label da GUI para mostrar o status do arquivo
        selected_delimiter_text (str): Delimitador selecionado na interface (ex: '; (Ponto e Vírgula)')
    """

    global GLOBAL_NUMBERS_LIST

    GLOBAL_NUMBERS_LIST = []
    logger.info("Abrindo seletor de arquivo CSV.")

    filepath = fd.askopenfilename(
        filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if not filepath:
        logger.warning("Selecao de arquivo CSV cancelada.")
        target_label.configure(text="Nenhum arquivo selecionado")
        return

    if selected_delimiter_text.startswith(';'):
        delimiter_char = ';'
    elif selected_delimiter_text.startswith(','):
        delimiter_char = ','
    else:
        delimiter_char = ';' 
        logger.warning(f"Delimitador invalido selecionado: {selected_delimiter_text}. Usando ';' como padrao.")
        
    logger.info(f"Tentando abrir CSV com delimitador: '{delimiter_char}'")

    with open(filepath, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter = delimiter_char)

        phone_column_name = None
        current_headers = [h.lower().strip() for h in csv_reader.fieldnames]

        for header_name in POSSIBLE_HEADERS:
            if header_name in current_headers:
                phone_column_name = current_headers[current_headers.index(header_name)]
                break

        if not phone_column_name:
            error_msg = f"Erro: Nenhuma coluna de telefone reconhecida no CSV. Esperava uma destas: {', '.join(POSSIBLE_HEADERS)}"
            logger.error(error_msg)
            target_label.configure(text=error_msg)
            return

        logger.info(f"Coluna de telefone identificada: '{phone_column_name}'.")

        file_name = filepath.split('/')[-1]
        new_file_label = f"Arquivo carregado: {file_name}"     
        target_label.configure(text=new_file_label)
        logger.info(f"Arquivo CSV '{file_name}' carregado com sucesso.")

        processed_count = 0
        for row in csv_reader:
            raw_number = row.get(phone_column_name, "").strip()
            
            if not raw_number:
                logger.warning(f"Aviso: Linha vazia ou sem numero na coluna '{phone_column_name}'.")
                continue

            try:
                parsed_number = phonenumbers.parse(raw_number, "BR") 
                
                if phonenumbers.is_valid_number(parsed_number):
                    formatted_number = phonenumbers.format_number(
                        parsed_number, 
                        phonenumbers.PhoneNumberFormat.E164
                    )
                    GLOBAL_NUMBERS_LIST.append(formatted_number)
                    logger.debug(f"Numero valido processado: {formatted_number}")
                    processed_count += 1
                else:
                    logger.warning(f"Aviso: Numero invalido/incompleto detectado: {raw_number}")

            except phonenumbers.phonenumberutil.NumberParseException as e:
                logger.warning(f"Aviso: Erro de parsing do numero '{raw_number}': {e}")

        logger.info(f"Total de {len(GLOBAL_NUMBERS_LIST)} numeros de telefone processados.")

def validate_and_send_image(textbox_widget, placeholder_text, state_label, progress_bar):
    """
    Valida a entrada de legenda da imagem e inicia o envio da imagem para todos os números.

    Parâmetros:
        textbox_widget (ctk.CTkTextbox): Caixa de texto contendo a legenda da imagem
        placeholder_text (str): Texto placeholder da caixa de texto
        state_label (ctk.CTkLabel): Label da GUI para mostrar status do envio
        progress_bar (ctk.CTkProgressBar): Barra de progresso da GUI
    """

    caption = textbox_widget.get("1.0", "end-1c") 
    
    if not GLOBAL_NUMBERS_LIST:
        error_msg = "Erro: Carregue um CSV antes de enviar."
        logger.error(error_msg)
        state_label.configure(text = error_msg)
        return
    
    if not GLOBAL_IMAGE_PATH:
        error_msg = "Erro: Carregue uma imagem antes de enviar."
        logger.error(error_msg)
        state_label.configure(text = error_msg)
        return

    state_label.configure(text = "Iniciando processo de envio de imagem...")
    logger.info("Validacao de envio de imagem bem-sucedida. Iniciando send_image_message.")

    progress_bar.configure(mode="determinate") 
    progress_bar.set(0)
    send_image_thread = threading.Thread(
        target=send_image_message,
        args=(GLOBAL_NUMBERS_LIST, GLOBAL_IMAGE_PATH, caption, state_label, progress_bar)
    )
    send_image_thread.start()

def validate_and_send(textbox_widget, placeholder_text, target_label, progress_bar):
    """
    Valida a mensagem de texto e inicia o envio para todos os números.

    Parâmetros:
        textbox_widget (ctk.CTkTextbox): Caixa de texto contendo a mensagem
        placeholder_text (str): Texto placeholder da caixa de texto
        target_label (ctk.CTkLabel): Label da GUI para mostrar status do envio
        progress_bar (ctk.CTkProgressBar): Barra de progresso da GUI
    """

    message = textbox_widget.get("1.0", "end-1c") 
    
    if message == placeholder_text or len(message.strip()) == 0:
        error_msg = "Erro de Validacao. Por favor, digite uma mensagem valida."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return

    if len(message) > 500:
        error_msg = "A mensagem ultrapassa o limite, por favor reduza-a!"
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return
    
    if not GLOBAL_NUMBERS_LIST:
        error_msg = "Erro de Validacao. Por favor, carregue um arquivo CSV valido."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return
    
    logger.info(f"Mensagem valida. Iniciando envio para {len(GLOBAL_NUMBERS_LIST)} destinatarios.")
    target_label.configure(text="Iniciando processo de envio...")

    progress_bar.configure(mode="determinate") 
    progress_bar.set(0)

    send_thread = threading.Thread(
        target=send_message, 
        args=(GLOBAL_NUMBERS_LIST, message, target_label, progress_bar)
    )
    send_thread.start()

def handle_focus_in(event, textbox_widget, placeholder_text):
    """
    Trata o evento de foco na caixa de texto, removendo o placeholder se presente.

    Parâmetros:
        event: Evento de foco
        textbox_widget (ctk.CTkTextbox): Caixa de texto
        placeholder_text (str): Texto placeholder
    """
    
    current_text = textbox_widget.get("1.0", "end-1c")
    if current_text == placeholder_text:
        textbox_widget.delete("1.0", "end")
        textbox_widget.configure(text_color=("black", "white")) 

def handle_focus_out(event, textbox_widget, placeholder_text):
    """
    Trata o evento de perda de foco na caixa de texto, reinserindo o placeholder se vazia.

    Parâmetros:
        event: Evento de perda de foco
        textbox_widget (ctk.CTkTextbox): Caixa de texto
        placeholder_text (str): Texto placeholder
    """
        
    current_text = textbox_widget.get("1.0", "end-1c")
    if current_text.strip() == "":
        textbox_widget.insert("1.0", placeholder_text)
        textbox_widget.configure(text_color=("gray70", "gray40"))

def update_char_count(event, textbox_widget, count_label):
    """
    Atualiza a contagem de caracteres de uma caixa de texto e altera a cor se exceder limite.

    Parâmetros:
        event: Evento de digitação
        textbox_widget (ctk.CTkTextbox): Caixa de texto
        count_label (ctk.CTkLabel): Label que mostra contagem de caracteres
    """
    
    mensagem = textbox_widget.get("1.0", "end-1c")
    current_length = len(mensagem)
    max_length = 500
    
    count_label.configure(text=f"{current_length}/{max_length}")

    if current_length > max_length:
        count_label.configure(text_color="red")
    else:
        count_label.configure(text_color=("gray50", "gray40"))

def go_back(current_window, parent_window, close_all=False):
    """
    Fecha a janela atual e retorna para a janela pai. Pode fechar todas as janelas se especificado.

    Parâmetros:
        current_window (ctk.CTkToplevel): Janela atual
        parent_window (ctk.CTk): Janela pai
        close_all (bool): Fecha também a janela pai se True
    """

    current_window.destroy()
    if close_all:
        parent_window.destroy()
    else:
        parent_window.deiconify()

def image_window(parent_window):
    """
    Cria a janela para envio de mensagens com imagem.

    Parâmetros:
        parent_window (ctk.CTk): Janela principal da aplicação
    """

    image_window = ctk.CTkToplevel()
    image_window.title("Envio de mensagens com imagem em massa")
    image_window.geometry("450x600")

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
    image_caption_textbox.bind("<FocusOut>", lambda event: handle_focus_out(event, image_caption_textbox, PLACEHOLDER_CAPTION))
    image_caption_textbox.bind("<KeyRelease>", lambda event: update_char_count(event, image_caption_textbox, count_caption))

    img_button = ctk.CTkButton(image_window, text="Selecionar Imagem", command=lambda: open_image_file(image_label))
    img_button.pack(pady=10)
    image_label = ctk.CTkLabel(image_window, text="Nenhuma imagem selecionada", wraplength=350)
    image_label.pack(pady=10)

    delimiter_label = ctk.CTkLabel(image_window, text="Escolha o delimitador do CSV:")
    delimiter_label.pack(pady=(10, 0))

    delimiter_options = ['; (Ponto e Vírgula)', ', (Vírgula)']
    image_window.delimiter_var = ctk.StringVar(value=delimiter_options[0]) 

    delimiter_menu = ctk.CTkOptionMenu(
        image_window, 
        values=delimiter_options, 
        variable=image_window.delimiter_var
    )
    delimiter_menu.pack(pady=(0, 10))

    arq_mensage = ctk.CTkLabel(image_window, text="Insira apenas arquivos CSV separados por ;")
    arq_mensage.pack(pady=10)
    arq_button = ctk.CTkButton(image_window, text="Selecionar Arquivo CSV", command=lambda: open_csv_file(file_label, image_window.delimiter_var.get()))
    arq_button.pack(pady=10)

    file_label = ctk.CTkLabel(image_window, text="Nenhum arquivo selecionado", wraplength=350)
    file_label.pack(pady=10)

    button_frame = ctk.CTkFrame(image_window)
    button_frame.pack(pady=20)
    back_button = ctk.CTkButton(button_frame, text="Voltar", command=lambda: go_back(image_window, parent_window))
    back_button.pack(side='left', padx=10)
    
    send_button = ctk.CTkButton(button_frame, text="Enviar Imagem", command=lambda: validate_and_send_image(image_caption_textbox, PLACEHOLDER_CAPTION, state_label, progress_bar))
    send_button.pack(side='left', padx=10)

    progress_bar = ctk.CTkProgressBar(image_window, orientation="horizontal")
    progress_bar.pack(pady=10, padx=20)
    progress_bar.set(0)

    state_label = ctk.CTkLabel(image_window, text="")
    state_label.pack(pady=10)
    
def simple_window(parent_window):
    """
    Cria a janela para envio de mensagens simples de texto.

    Parâmetros:
        parent_window (ctk.CTk): Janela principal da aplicação
    """

    simple_window = ctk.CTkToplevel()
    simple_window.title("Envio de mensagens simples em massa")
    simple_window.geometry("450x600")

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
    simple_textbox.bind("<FocusOut>", lambda event: handle_focus_out(event, simple_textbox, PLACEHOLDER_MSG))
    simple_textbox.bind("<KeyRelease>", lambda event: update_char_count(event, simple_textbox, count_label))

    delimiter_label = ctk.CTkLabel(simple_window, text="Escolha o delimitador do CSV:")
    delimiter_label.pack(pady=(10, 0))

    delimiter_options = ['; (Ponto e Vírgula)', ', (Vírgula)']
    simple_window.delimiter_var = ctk.StringVar(value=delimiter_options[0]) 

    delimiter_menu = ctk.CTkOptionMenu(
        simple_window, 
        values=delimiter_options, 
        variable=simple_window.delimiter_var
    )
    delimiter_menu.pack(pady=(0, 10))

    arq_mensage = ctk.CTkLabel(simple_window, text="Insira apenas arquivos CSV separados por ;")
    arq_mensage.pack(pady=10)
    arq_button = ctk.CTkButton(simple_window, text="Selecionar Arquivo CSV", command=lambda: open_csv_file(file_label, simple_window.delimiter_var.get()))
    arq_button.pack(pady=10)

    file_label = ctk.CTkLabel(simple_window, text="Nenhum arquivo selecionado", wraplength=350)
    file_label.pack(pady=10)

    button_frame = ctk.CTkFrame(simple_window)
    button_frame.pack(pady=20)

    back_button = ctk.CTkButton(button_frame, text="Voltar", command=lambda: go_back(simple_window, parent_window))
    back_button.pack(side='left', padx=10)

    send_button = ctk.CTkButton(button_frame, text="Enviar", command=lambda: validate_and_send(simple_textbox, PLACEHOLDER_MSG, state_label, progress_bar))
    send_button.pack(side='left', padx=10)

    progress_bar = ctk.CTkProgressBar(simple_window, orientation="horizontal")
    progress_bar.pack(pady=10, padx=20)
    progress_bar.set(0)

    state_label = ctk.CTkLabel(simple_window, text="")
    state_label.pack(pady=10)
    
def app_window():
    """
    Cria a janela principal da aplicação com opções de envio simples ou com imagem.
    """

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

setup_log()
app_window()