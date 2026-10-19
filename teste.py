import requests, time, json, os, pandas as pd

PASTA = r"C:\Users\Usuario\mineracao"
os.makedirs(PASTA, exist_ok=True)

BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

DATA_INICIAL = "20250301"
DATA_FINAL   = "20250307"
UF = "RS"
MODALIDADES = [6]          # 6 = pregão eletrônico
TAMANHO = 50

def pegar_pagina(params, tentativas=6):
    """Faz a requisição; se der 429 (excesso), espera e tenta de novo."""
    for i in range(tentativas):
        r = requests.get(BASE, params=params, timeout=60)
        if r.status_code == 429:
            espera = 10 * (i + 1)
            print(f"   429 - esperando {espera}s e tentando de novo...")
            time.sleep(espera)
            continue
        return r
    return r

registros = []

for mod in MODALIDADES:
    params = {"dataInicial": DATA_INICIAL, "dataFinal": DATA_FINAL,
              "codigoModalidadeContratacao": mod, "uf": UF,
              "pagina": 1, "tamanhoPagina": TAMANHO}
    while True:
        r = pegar_pagina(params)
        if r.status_code == 204:           # sem resultados
            print(f"Modalidade {mod}: sem registros")
            break
        if r.status_code != 200:
            print(f"Modalidade {mod}, página {params['pagina']}: status {r.status_code}")
            break
        dados = r.json()
        registros += dados.get("data", [])
        print(f"Modalidade {mod} - página {params['pagina']}/{dados.get('totalPaginas')} "
              f"- total registros': {len(registros)}")
        if params["pagina"] >= dados.get("totalPaginas", 1):
            break
        params["pagina"] += 1
        time.sleep(1)   #pausa entre as requesições pra não bloquear 

#salvar como json e csv
caminho_json = os.path.join(PASTA, "contratacoes_rs.json")
caminho_csv  = os.path.join(PASTA, "contratacoes_rs.csv")

with open(caminho_json, "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False)

df = pd.json_normalize(registros)
df.to_csv(caminho_csv, index=False, encoding="utf-8-sig", sep=";")

#print("JSON salvo em:", caminho_json)
print("CSV salvo em: ", caminho_csv)
print("Tabela:", df.shape)