import os
import time
from src.data_manager import load_data, save_data
from src.whatsapp_bot import WhatsAppBot
from datetime import datetime
import random


CSV_FILE = os.path.join("data", "LISTA_FINAL_SEGUNDA.csv") 
PROFILE_PATH = os.path.join(os.getcwd(), "config", "sessao_whatsapp")

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def run_auto_validation(df, bot, csv_path):
    
    pendentes = df[(df['Status'] == "") | (df['Status'].isna())]
    
    if pendentes.empty:
        print(f"\n{GREEN}No pending leads found! The list is finished.{RESET}")
        input("Press Enter to return to the menu...")
        return df

    fila = pendentes.head(10)
    total = len(fila)
    print(f"\n{GREEN}--- Starting validation for {total} contacts ---{RESET}")
    
    count = 0
    for index, row in fila.iterrows():
        count += 1
        empresa = str(row['Empresa'])
        whatsapp = str(row['WhatsApp'])
        
        print(f"\n[{count}/{total}] Sending to {empresa} ({whatsapp})...")
        
        mensagem = f"Olá {empresa}" 
        sucesso, status_msg = bot.send_message(whatsapp, mensagem)
        
        if sucesso:
            print(f"{GREEN}✅ {status_msg}{RESET}")
            df.loc[index, 'Status'] = "Validation Sent"
        else:
            print(f"{RED}❌ {status_msg}{RESET}")
            df.loc[index, 'Status'] = "Invalid Number"
            
        df.loc[index, 'Last_Contact'] = datetime.now().strftime("%d/%m/%Y")
        
        save_data(df, csv_path)
        
        if count < total:
            tempo_espera = random.randint(20, 40)
            print(f"Waiting {tempo_espera}s to avoid ban...")
            time.sleep(tempo_espera)
            
    print(f"\n{GREEN}=== Validation Finished ==={RESET}")
    input("Press Enter to return to the menu...")
    return df

def main():

    print(f"{YELLOW}--- Starting WhatsApp RPA ---{RESET}")
    
    print("Loading spreadsheet...")
    df = load_data(CSV_FILE)
    
    if df is None:
        print(f"{RED}Failed to load data. Please check the 'data' folder. Exiting...{RESET}")
        return

    print("Initializing browser...")
    bot = WhatsAppBot(PROFILE_PATH)
    bot.start_browser()

    while True:
        os.system('clear')
        print(f"{GREEN}=== MAIN MENU ==={RESET}")
        print("[ 1 ] Run Auto-Validation (Send Messages)")
        print("[ 0 ] Exit")
        
        choice = input("\nSelect an option > ")
        
        if choice == '1':
            df = run_auto_validation(df, bot, CSV_FILE)
            time.sleep(2)
            
        elif choice == '0':
            print(f"{YELLOW}Closing the bot and saving data...{RESET}")
            bot.close_browser()
            break
            
        else:
            print(f"{RED}Invalid option!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Program interrupted by user. Exiting...{RESET}")