import requests, time, json, os, pandas as pd

PASTA = r"C:\Users\Usuario\mineracao"
os.makedirs(PASTA, exist_ok=True)

BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

DATA_INICIAL = "20260101"
DATA_FINAL   = "20261019"
UF = "RS"
MODALIDADES = [6]          # 6 = pregão eletrônico
TAMANHO = 50
MUNICIPIO_IBGE = 4316907   # Santa maria

#salvar como json e csv
caminho_json = os.path.join(PASTA, "contratacoes_sm_rs_260101_261019.json")
caminho_csv  = os.path.join(PASTA, "contratacoes_sm_rs_260101_261019.csv")

def pegar_pagina(params, tentativas=8):
    """Faz a requisição; se der 429 (excesso), timeout e erro de conexão, espera e tenta de novo."""
    for i in range(tentativas):
        try:
            r = requests.get(BASE, params=params, timeout=(15, 90))
            if r.status_code == 429:
                espera = 10 * (i + 1)
                print(f"   429 - esperando {espera}s")
                time.sleep(espera)
                continue
            return r
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as e:
            espera = 15 * (i + 1)
            print(f"   falha de conexão ({type(e).__name__}) - esperando {espera}s")
            time.sleep(espera)
    return None   # desistiu

def salvar(registros):
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False)
        
    pd.json_normalize(registros).to_csv(caminho_csv, index=False,
                                        encoding="utf-8-sig", sep=";")


registros = []

for mod in MODALIDADES:
    params = {"dataInicial": DATA_INICIAL, "dataFinal": DATA_FINAL,
              "codigoModalidadeContratacao": mod, "uf": UF,
              "codigoMunicipioIbge": MUNICIPIO_IBGE,
              "pagina": 1, "tamanhoPagina": TAMANHO}
    while True:
        r = pegar_pagina(params)
        if r is None:
            print(f"Desisti na modalidade {mod}, página {params['pagina']}")
            break
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
        salvar(registros)   #salva a cada pg
        if params["pagina"] >= dados.get("totalPaginas", 1):
            break
        params["pagina"] += 1
        time.sleep(1)   #pausa entre as requesições pra não bloquear 



print("terminado, total de registros:", len(registros))
print("CSV:", caminho_csv)