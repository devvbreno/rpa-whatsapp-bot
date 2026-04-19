import pandas as pd
from src.data_manager import load_data

def test_load_data_creates_new_columns(tmp_path):
    """
    Testa se a função load_data consegue ler um CSV simples
    e criar automaticamente as colunas de controle do robô.
    """
    # 1. SETUP (Preparação): Criamos um arquivo CSV falso em uma pasta temporária
    arquivo_falso = tmp_path / "planilha_teste.csv"
    arquivo_falso.write_text("Empresa;WhatsApp\nEmpresa A;11999999999.0", encoding="utf-8")

    # 2. ACTION (Ação): Chamamos a sua função passando o caminho do arquivo falso
    df = load_data(str(arquivo_falso))

    # 3. ASSERT (Verificação): O teste verifica se a função fez o que prometeu
    
    # O DataFrame não pode ser None
    assert df is not None 
    assert "Empresa" in df.columns
    
    # O robô deve ter criado as colunas novas
    assert "Status" in df.columns
    assert "WhatsApp_Link" in df.columns
    
    assert df.iloc[0]["WhatsApp"] == "11999999999"