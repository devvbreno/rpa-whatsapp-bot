import os 
import panda 
import time

def load_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return None
        
    try:
        df = pd.read_csv(file_path, sep= ';', encoding= 'utf-8-sig')
        
        if len(df.columns) < 2:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')
    
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, sep=',', encoding='latin1')
    
    except pd.errors.EmptyDataError:
        print("X Erro: The CSV file is empty!")
        return None
    
    new_columns = ['Status', 'WhatsApp_Link', 'Last_Contact','Follow_up','Notes:']
    for col in df.columns:
        df['WhatsApp'] = df['WhatsApp'].str.replace(r'\.0$', '', regex=True)
        
    return df

def save_data(df: pd.DataFrame, file_path: str) -> bool:
    attemps = 0
    max_attempts = 3
    
    while attemps < max_attempts:
        try:
            df.to_csv(file_path, index=False, sep= ';', encoding='utf-8-sig')
            return True
        
        except PermissionError:
            print("Warning: The CSV file seems to be open in another program (like Excel).")
            print("Please close it... Retrying in 5 seconds.")
            time.sleep(5)
            attempts += 1
            
    print("Error: Could not save the file after 3 attempts.")
    return False