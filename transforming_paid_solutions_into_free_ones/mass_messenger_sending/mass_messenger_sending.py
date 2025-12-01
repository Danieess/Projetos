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

POSSIBLE_HEADERS = ["telefone", "phone", "cellphone", "celular", "whatsapp", "contato", "numero", "número", "phonenumber", "phone_number", "mobile", "mobile_number"]
GLOBAL_NUMBERS_LIST = []
GLOBAL_IMAGE_PATH = None
MAX_MESSAGE_LEN = 500
SLEEP_BETWEEN_MESSAGES = 2
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
        os.makedirs(os.path.join(os.getcwd(), logger_dir))

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

def execute_send_process_unified(list_numbers, target_label, progress_bar=None, message_text=None, image_path=None, caption_text=None):
    """
    Unifica o processo de envio de mensagens simples ou com imagem.

    Parâmetros:
        list_numbers (list): Lista de números de telefone no formato E.164.
        target_label (ctk.CTkLabel): Label da GUI para mostrar status.
        progress_bar (ctk.CTkProgressBar, opcional): Barra de progresso para atualizar envio.
        message_text (str, opcional): Texto da mensagem simples (se modo simples).
        image_path (str, opcional): Caminho do arquivo de imagem (se modo imagem).
        caption_text (str, opcional): Legenda da imagem (se modo imagem).
    """
    
    is_image_mode = image_path is not None
    
    # Acessa a variável global SLEEP_BETWEEN_MESSAGES
    global SLEEP_BETWEEN_MESSAGES 

    # --- Validações e Configurações ---
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
    
    if is_image_mode and (not image_path or not os.path.exists(image_path)):
        error_msg = "ERRO: Caminho de imagem invalido ou arquivo inexistente."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return

    # --- Inicialização da API e Loop de Envio ---
    whats = WhatsApp(phone_id = PHONE_ID, token = TOKEN)
    mode_desc = "imagens" if is_image_mode else "mensagens de texto"
    logger.info(f"Iniciando o envio de {mode_desc} para {len(list_numbers)} destinatarios.")
    
    sucess_count, fail_count = 0, 0
    total_numbers = len(list_numbers)

    for index, number in enumerate(list_numbers):
        status_msg = f"Enviando {'imagem' if is_image_mode else 'texto'} ({index + 1}/{len(list_numbers)}): {number}"
        target_label.configure(text=status_msg)
        target_label.update_idletasks() 
        
        try:
            if is_image_mode:
                # Método para imagem
                response = whats.send_image(to=number, image=image_path, caption=caption_text)
            else:
                # Método para texto
                response = whats.send_message_text(to=number, message=message_text)

            # Extração de ID de resposta EXATA do seu código original
            messages = response.get("messages", [])
            msg_id = messages[0].get("id", "N/A") if messages else "N/A"
            
            logger.info(f"Sucesso para {number}. ID: {msg_id}")
            sucess_count += 1
            time.sleep(SLEEP_BETWEEN_MESSAGES) 

        except Exception as e:
            logger.error(f"Ocorreu um erro ao enviar para {number}: {e}", exc_info=True)
            fail_count += 1

        if progress_bar:
            progress = (index + 1) / total_numbers
            progress_bar.set(progress)
            target_label.update_idletasks()

    # --- Finalização ---
    sucess_msg = f"Processo concluido. Sucessos: {sucess_count}, Falhas: {fail_count}"
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
    file_name = os.path.basename(filepath)
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

    with open(filepath, mode='r', encoding='utf-8-sig') as file:
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

def validate_and_send_unified(textbox_widget, placeholder_text, target_label, progress_bar, is_image_mode: bool):
    """
    Unifica a validação e início do processo de envio para mensagens simples ou com imagem.

    Parâmetros:
        textbox_widget (ctk.CTkTextbox): O widget de texto/legenda.
        placeholder_text (str): O texto de placeholder original.
        target_label (ctk.CTkLabel): O label da GUI para mostrar o status.
        progress_bar (ctk.CTkProgressBar): A barra de progresso da GUI.
        is_image_mode (bool): Define se o modo é de imagem (True) ou simples (False).
    """

    content = textbox_widget.get("1.0", "end-1c").strip()
    
    # --- 1. Validações Específicas do Modo Simples ---
    if not is_image_mode:
        if content == placeholder_text or len(content) == 0:
            error_msg = "Erro de Validacao. Por favor, digite uma mensagem valida."
            logger.error(error_msg)
            target_label.configure(text = error_msg)
            return

        if len(content) > MAX_MESSAGE_LEN:
            error_msg = "A mensagem ultrapassa o limite, por favor reduza-a!"
            logger.error(error_msg)
            target_label.configure(text = error_msg)
            return

    # --- 2. Validação Comum: Lista de Números ---
    if not GLOBAL_NUMBERS_LIST:
        # A mensagem de erro é ligeiramente diferente dependendo do modo, mas o resultado é o mesmo
        error_msg = "Erro de Validacao. Por favor, carregue um arquivo CSV valido." if not is_image_mode else "Erro: Carregue um CSV antes de enviar."
        logger.error(error_msg)
        target_label.configure(text = error_msg)
        return

    # --- 3. Validações Específicas do Modo Imagem ---
    if is_image_mode:
        if not GLOBAL_IMAGE_PATH:
            error_msg = "Erro: Carregue uma imagem antes de enviar."
            logger.error(error_msg)
            target_label.configure(text = error_msg)
            return
        
        # Define parâmetros para o modo imagem
        start_message = "Iniciando processo de envio de imagem..."
        log_message = "Validacao de envio de imagem bem-sucedida. Iniciando send_image_message."

    # --- 4. Define parâmetros para o Modo Simples ---
    else:
        start_message = "Iniciando processo de envio..."
        log_message = f"Mensagem valida. Iniciando envio para {len(GLOBAL_NUMBERS_LIST)} destinatarios."
        

    # --- 5. Lógica de Envio Comum (Inicia a Thread) ---
    logger.info(log_message)
    target_label.configure(text=start_message)

    progress_bar.configure(mode="determinate") 
    progress_bar.set(0)

    send_thread = threading.Thread(target=execute_send_process_unified, args=(
            GLOBAL_NUMBERS_LIST,             # list_numbers
            target_label,                    # target_label
            progress_bar,                    # progress_bar
            content if not is_image_mode else None, # message_text
            GLOBAL_IMAGE_PATH if is_image_mode else None, # image_path
            content if is_image_mode else None       # caption_text
        )
    )
    send_thread.start()

def handle_focus_event(event, textbox_widget, placeholder_text, action_type: str):
    """
    Trata os eventos de foco (FocusIn e FocusOut) para um CTkTextbox unificado.

    Parâmetros:
        event: Evento de foco (fornecido automaticamente pelo Tkinter bind)
        textbox_widget (ctk.CTkTextbox): A caixa de texto alvo.
        placeholder_text (str): O texto placeholder original.
        action_type (str): 'in' para FocusIn, 'out' para FocusOut.
    """
    
    current_text = textbox_widget.get("1.0", "end-1c")
    default_color = ("gray70", "gray40")
    active_color = ("black", "white")

    if action_type == "in":
        # Lógica original do handle_focus_in
        if current_text == placeholder_text:
            textbox_widget.delete("1.0", "end")
            textbox_widget.configure(text_color=active_color)
    
    elif action_type == "out":
        # Lógica original do handle_focus_out
        if not current_text:
            textbox_widget.insert("1.0", placeholder_text)
            textbox_widget.configure(text_color=default_color)

def update_char_count(event, textbox_widget, count_label):
    """
    Atualiza a contagem de caracteres de uma caixa de texto e altera a cor se exceder limite.

    Parâmetros:
        event: Evento de digitação
        textbox_widget (ctk.CTkTextbox): Caixa de texto
        count_label (ctk.CTkLabel): Label que mostra contagem de caracteres
    """
    
    global MAX_MESSAGE_LEN

    mensagem = textbox_widget.get("1.0", "end-1c")
    current_length = len(mensagem)
    
    count_label.configure(text=f"{current_length}/{MAX_MESSAGE_LEN}")

    if current_length > MAX_MESSAGE_LEN:
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

def create_sender_window(parent_window, is_image_mode: bool):
    """
    Cria uma janela unificada para envio de mensagens, 
    alternando entre modo simples (False) e modo imagem (True).
    """
    
    mode_name = "Imagem" if is_image_mode else "Simples"
    logger.info(f"Abrindo janela no modo: {mode_name}")

    sender_window = ctk.CTkToplevel(parent_window)
    sender_window.geometry("450x600")

    if is_image_mode:
        sender_window.title("Envio de mensagens com imagem em massa")
        PLACEHOLDER_MSG = f"Digite a legenda da imagem (max {MAX_MESSAGE_LEN} chars)..."

    else:
        sender_window.title("Envio de mensagens simples em massa")
        PLACEHOLDER_MSG = "Digite aqui sua mensagem..."

        
    sender_window.protocol("WM_DELETE_WINDOW", lambda: go_back(sender_window, parent_window, close_all=True))

    # === WIDGETS COMUNS E CONDICIONAIS ===
    label_text = "Legenda da Imagem (Opcional):" if is_image_mode else "Mensagem:"
    caption_label = ctk.CTkLabel(sender_window, text=label_text)
    caption_label.pack(pady=10)

    text_height = 100 if is_image_mode else 150
    textbox = ctk.CTkTextbox(sender_window, width=400, height=text_height, wrap="word", border_width=2, corner_radius=10, text_color=("gray70", "gray40"))
    textbox.pack(pady=10)

    count_label = ctk.CTkLabel(sender_window, text=f"0/{MAX_MESSAGE_LEN}", font=ctk.CTkFont(size=12), text_color=("gray50", "gray40"))
    count_label.pack(anchor='e', padx=25)

    textbox.insert("0.0", PLACEHOLDER_MSG)
    textbox.bind("<FocusIn>", lambda event: handle_focus_event(event, textbox, PLACEHOLDER_MSG, action_type="in"))
    textbox.bind("<FocusOut>", lambda event: handle_focus_event(event, textbox, PLACEHOLDER_MSG, action_type="out"))
    textbox.bind("<KeyRelease>", lambda event: update_char_count(event, textbox, count_label))

    # --- Seção Específica para Imagem ---
    image_label = None 
    if is_image_mode:
        img_button = ctk.CTkButton(sender_window, text="Selecionar Imagem", command=lambda: open_image_file(image_label))
        img_button.pack(pady=10)
        image_label = ctk.CTkLabel(sender_window, text="Nenhuma imagem selecionada", wraplength=350)
        image_label.pack(pady=10)

    # === WIDGETS DE CSV (Comuns) ===
    delimiter_label = ctk.CTkLabel(sender_window, text="Escolha o delimitador do CSV:")
    delimiter_label.pack(pady=(10, 0))

    delimiter_options = ['; (Ponto e Vírgula)', ', (Vírgula)']
    sender_window.delimiter_var = ctk.StringVar(value=delimiter_options[0]) 

    delimiter_menu = ctk.CTkOptionMenu(sender_window, values=delimiter_options, variable=sender_window.delimiter_var)
    delimiter_menu.pack(pady=(0, 10))

    arq_mensage = ctk.CTkLabel(sender_window, text="Insira apenas arquivos CSV separados por ; ou ,")
    arq_mensage.pack(pady=10)
    
    file_label = ctk.CTkLabel(sender_window, text="Nenhum arquivo selecionado", wraplength=350)
    
    arq_button = ctk.CTkButton(sender_window, text="Selecionar Arquivo CSV", command=lambda: open_csv_file(file_label, sender_window.delimiter_var.get()))
    arq_button.pack(pady=10)
    
    file_label.pack(pady=10)

    # === FRAME DE BOTÕES E STATUS (Comuns) ===
    button_frame = ctk.CTkFrame(sender_window)
    button_frame.pack(pady=20)
    
    back_button = ctk.CTkButton(button_frame, text="Voltar", command=lambda: go_back(sender_window, parent_window))
    back_button.pack(side='left', padx=10)
    
    send_button_text = "Enviar Imagem" if is_image_mode else "Enviar"
    
    progress_bar = ctk.CTkProgressBar(sender_window, orientation="horizontal")
    target_label = ctk.CTkLabel(sender_window, text="")
    
    send_button = ctk.CTkButton(button_frame, text=send_button_text, command=lambda: validate_and_send_unified(textbox, PLACEHOLDER_MSG, target_label, progress_bar, is_image_mode))
    send_button.pack(side='left', padx=10)

    progress_bar.pack(pady=10, padx=20)
    progress_bar.set(0)

    target_label.pack(pady=10)
    
    sender_window.update() 
    parent_window.withdraw()

def app_window():
    """
    Cria a janela principal da aplicação.
    """

    ctk.set_appearance_mode("system")
    app_window = ctk.CTk()
    app_window.title("Envio de mensagens em massa")
    app_window.geometry("350x250")
   
    mensagem_simple = ctk.CTkLabel(app_window, text="Mensagem simples")
    mensagem_simple.pack(pady=10)
    button_simple = ctk.CTkButton(app_window, text="Simples", command=lambda: create_sender_window(app_window, is_image_mode=False))
    button_simple.pack(pady=10)
   
    mensagem_image = ctk.CTkLabel(app_window, text="Mensagem com imagem")
    mensagem_image.pack(pady=20)
    button_image = ctk.CTkButton(app_window, text="Imagem", command=lambda: create_sender_window(app_window, is_image_mode=True))
    button_image.pack(pady=10)
    
    app_window.mainloop()

setup_log()
app_window()