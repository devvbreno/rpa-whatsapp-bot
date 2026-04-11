import pandas as pd
import urllib.parse
from datetime import datetime
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'LISTA_FINAL_SEGUNDA.csv'
PROFILE_PATH = os.path.join(os.getcwd(), "sessao_whatsapp")
LIMITE_TESTE = 15

SAUDACOES = [
    "Oi", "Olá", "Opa, tudo bem?", "Oi, tudo bom?", 
    "Bom dia", "Olá, tudo bem?", "Opa"
]

# --- TEMPOS (ANTIBAN) ---
TEMPO_MIN = 40
TEMPO_MAX = 80
QTD_BLOCO = 5
PAUSA_LONGA_MIN = 115 
PAUSA_LONGA_MAX = 145

VERDE = "\033[92m"
AMARELO = "\033[93m"
CYAN = "\033[96m"
VERMELHO = "\033[91m"
RESET = "\033[0m"

def iniciar_navegador():
    print(f"{AMARELO}Iniciando Modo Seguro (Correção de Seletor)...{RESET}")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    print(f"{VERDE}>> Aguarde o WhatsApp carregar (20s)... <<{RESET}")
    time.sleep(20)
    return driver

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return None
    try:
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        if len(df.columns) < 2: df = pd.read_csv(ARQUIVO_CSV, sep=',', encoding='utf-8')
    except:
        df = pd.read_csv(ARQUIVO_CSV, sep=',', encoding='latin1')

    cols_novas = ['Status', 'Link WhatsApp', 'Data Ultimo Contato', 'Data Follow-up', 'Observacoes', 'Motivo Recusa']
    for col in cols_novas:
        if col not in df.columns: df[col] = ""
    
    cols_texto = ['Observacoes', 'Status', 'Link WhatsApp', 'Motivo Recusa', 'WhatsApp']
    for col in cols_texto:
        if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')

    df['WhatsApp'] = df['WhatsApp'].str.replace(r'\.0$', '', regex=True)
    return df

def salvar_dados(df):
    try:
        df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    except PermissionError:
        print(f"{VERMELHO}ERRO: Feche o Excel!{RESET}")
        time.sleep(5)
        salvar_dados(df)

def executar_teste_seguro(driver):
    df = carregar_dados()
    
    pendentes = df[ 
        (df['Status'].isna()) | (df['Status'] == "") | 
        (df['Status'].astype(str).str.strip() == "nan") |
        (df['Status'].astype(str).str.strip() == "")
    ]
    
    if pendentes.empty:
        print("Lista vazia.")
        return

    fila_teste = pendentes.head(LIMITE_TESTE)
    total = len(fila_teste)
    
    print(f"{CYAN}--- INICIANDO TESTE COM {total} CONTATOS ---{RESET}")
    
    contagem = 0
    enviados_no_bloco = 0
    
    for index, row in fila_teste.iterrows():
        contagem += 1
        enviados_no_bloco += 1
        
        empresa = str(row['Empresa'])
        whatsapp = str(row['WhatsApp'])
        msg_escolhida = random.choice(SAUDACOES)
        
        print(f"[{contagem}/{total}] Enviando para {empresa}...")

        texto_codificado = urllib.parse.quote(msg_escolhida)
        link = f"https://web.whatsapp.com/send?phone={whatsapp}&text={texto_codificado}"
        driver.get(link)
        
        try:
            # --- A MÁGICA ACONTECE AQUI ---
            wait = WebDriverWait(driver, 35)
            
            # 1. Esperamos o painel principal (#main) aparecer. Isso garante que o chat abriu.
            wait.until(EC.presence_of_element_located((By.ID, "main")))

            # 2. Buscamos a caixa de texto ESPECÍFICA do rodapé do chat
            # O seletor CSS agora é: "dentro do id main -> procure o footer -> procure o div editável"
            caixa_texto = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#main footer div[contenteditable="true"]')
            ))
            
            # Pausa humana
            time.sleep(random.randint(3, 6)) 
            
            # Envia o ENTER na caixa certa
            caixa_texto.send_keys(Keys.ENTER)
            
            # Atualiza status
            df.loc[index, 'Status'] = "Validacao Enviada"
            df.loc[index, 'Data Ultimo Contato'] = datetime.now().strftime("%d/%m/%Y")
            salvar_dados(df)
            
            # Pausas
            if enviados_no_bloco >= QTD_BLOCO:
                tempo_pausa = random.randint(PAUSA_LONGA_MIN, PAUSA_LONGA_MAX)
                print(f"{AMARELO}☕ Pausa Longa... ({tempo_pausa}s){RESET}")
                time.sleep(tempo_pausa)
                enviados_no_bloco = 0
            else:
                tempo_espera = random.randint(TEMPO_MIN, TEMPO_MAX)
                print(f"{VERDE}✅ Ok! Esperando {tempo_espera}s...{RESET}")
                time.sleep(tempo_espera)

        except Exception as e:
            # Se não achou o #main, é porque o número é inválido ou a internet caiu
            if "main" in str(e) or "footer" in str(e):
                print(f"{VERMELHO}❌ Número Inválido (Chat não abriu).{RESET}")
                df.loc[index, 'Status'] = "Numero Invalido"
            else:
                print(f"{VERMELHO}⚠️ Erro genérico: {e}{RESET}")
                df.loc[index, 'Status'] = "Erro Tecnico"
            
            salvar_dados(df)
            time.sleep(5)

    print(f"\n{VERDE}=== TESTE FINALIZADO ==={RESET}")

if __name__ == "__main__":
    try:
        driver = iniciar_navegador()
        executar_teste_seguro(driver)
    except KeyboardInterrupt:
        print("\nParando...")