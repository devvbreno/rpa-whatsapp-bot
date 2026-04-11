import pandas as pd
import urllib.parse
from datetime import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'LISTA_FINAL_SEGUNDA.csv'
PROFILE_PATH = os.path.join(os.getcwd(), "sessao_whatsapp")

MENSAGEM_BASE = (
    "Olá {empresa}! Tudo bem?\n\n"
    "{personalizacao}\n\n"
    "Pra fugir do padrão de fotos estáticas e destacar a oferta de vocês, criei esse exemplo de Video Motion.\n\n"
    "É um diferencial que retém MUITO mais atenção. Vejam a prévia:"
)

VERDE = "\033[92m"
AMARELO = "\033[93m"
CYAN = "\033[96m"
VERMELHO = "\033[91m"
RESET = "\033[0m"

def iniciar_navegador():
    print(f"{AMARELO}Iniciando navegador (Perfil Salvo)...{RESET}")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    print(f"{VERDE}>> Aguardando carregamento... (8s) <<{RESET}")
    time.sleep(8)
    return driver

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV):
        print(f"{VERMELHO}Arquivo não encontrado!{RESET}")
        return None
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
        print(f"{VERMELHO}ERRO: Feche o arquivo Excel!{RESET}")
        time.sleep(2)
        salvar_dados(df)

def processar_leads(driver):
    df = carregar_dados()
    ultimo_lead_index = None 
    
    while True:
        os.system('clear')
        print(f"{VERDE}=== MODO LINHA DE PRODUÇÃO (V6.0 - STATUS VOLTAR) ==={RESET}")
        
        pendentes = df[ 
            (df['Status'].isna()) | (df['Status'] == "") | 
            (df['Status'].astype(str).str.strip() == "nan") |
            (df['Status'].astype(str).str.strip() == "")
        ]
        
        if pendentes.empty:
            print("Lista finalizada!")
            break

        index = pendentes.index[0]
        row = pendentes.iloc[0]
        
        empresa = str(row['Empresa'])
        whatsapp = str(row['WhatsApp'])
        site = str(row['Website'])
        obs_atual = str(row['Observacoes']) if str(row['Observacoes']) != 'nan' else ""

        print(f"🏢 {empresa} | 📱 {whatsapp}")
        print(f"🌐 {site}")
        print("-" * 40)

        # Abre site automático
        if len(site) > 5 and site != 'nan':
            try:
                if len(driver.window_handles) == 1:
                    driver.execute_script(f"window.open('{site}', '_blank');")
            except: pass

        proximo = False
        while not proximo:
            print(f"\n[Enter] 🚀 Enviar | [1] ✏️ Editar Num | [2] 🌐 Site | [0] Pular | [V] 🔙 Desfazer Anterior")
            acao = input("Opção > ").upper()

            if acao == 'V': # DESFAZER O ANTERIOR (GLOBAL)
                if ultimo_lead_index is not None:
                    print(f"{VERMELHO}Desfazendo ação anterior...{RESET}")
                    df.loc[ultimo_lead_index, 'Status'] = ""
                    salvar_dados(df)
                    proximo = True 
                else:
                    print("❌ Não há anterior para voltar.")

            elif acao == '': # TENTAR ENVIAR
                personalizacao = obs_atual
                if not personalizacao:
                    personalizacao = input("Personalização rápida (Enter para msg padrão): ")

                msg_final = MENSAGEM_BASE.format(empresa=empresa, personalizacao=personalizacao)
                texto_codificado = urllib.parse.quote(msg_final)
                link = f"https://web.whatsapp.com/send?phone={whatsapp}&text={texto_codificado}"
                
                driver.get(link)
                
                # --- MENU DE CONFIRMAÇÃO DO ENVIO (AQUI ESTÁ O QUE VOCÊ PEDIU) ---
                print(f"\n{AMARELO}>>> O WHATSAPP ABRIU. DEU CERTO? <<<{RESET}")
                print("[Enter] ✅ Enviado (Arraste o vídeo)")
                print("[E]     ⚠️  ERRO / VOLTAR (Número inválido, quero corrigir)")
                print("[I]     🗑️  IGNORADO (Número ruim, quero desistir desse)")
                print("[N]     🤝  Negociando | [R] Recusou")
                
                resp = input("Status > ").upper()
                
                if resp == 'E':
                    print(f"{VERMELHO}Voltando para edição...{RESET}")
                    continue # <--- ISSO É O PULO DO GATO: Volta pro menu desse mesmo cliente
                
                # Se não foi erro, salvamos os dados do envio
                df.loc[index, 'Link WhatsApp'] = link
                df.loc[index, 'Data Ultimo Contato'] = datetime.now().strftime("%d/%m/%Y")
                if personalizacao: df.loc[index, 'Observacoes'] = personalizacao

                if resp == 'R':
                    df.loc[index, 'Status'] = 'Recusou'
                    df.loc[index, 'Motivo Recusa'] = input("Motivo: ")
                elif resp == 'N':
                    df.loc[index, 'Status'] = 'Negociando'
                elif resp == 'I':
                    df.loc[index, 'Status'] = 'Ignorado'
                else:
                    df.loc[index, 'Status'] = 'Enviado'
                
                salvar_dados(df)
                ultimo_lead_index = index 
                proximo = True

            elif acao == '1': # EDITAR NÚMERO
                novo = input("Novo Número: ")
                df.loc[index, 'WhatsApp'] = novo
                whatsapp = novo
                salvar_dados(df)
                print("✅ Número corrigido!")

            elif acao == '2': # REABRIR SITE
                if len(site) > 5 and site != 'nan':
                    driver.execute_script(f"window.open('{site}', '_blank');")
                    print("🔄 Site reaberto.")

            elif acao == '0': # PULAR
                df.loc[index, 'Status'] = "Pular"
                salvar_dados(df)
                ultimo_lead_index = index
                proximo = True

if __name__ == "__main__":
    driver = iniciar_navegador()
    processar_leads(driver)