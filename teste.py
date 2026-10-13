import requests, time, pandas as pd

BASE = "https://pncp.gov.br/api/consulta/v1/contratos"
params = {"dataInicial": "20240101", "dataFinal": "20240131",
          "pagina": 1, "tamanhoPagina": 50}
registros = []

while True:
    r = requests.get(BASE, params=params, timeout=60)
    if r.status_code != 200:
        break
    dados = r.json()
    registros += dados.get("data", [])
    if params["pagina"] >= dados.get("totalPaginas", 1):
        break
    params["pagina"] += 1
    time.sleep(0.3)  # evita bloqueio por excesso de requisições

df = pd.json_normalize(registros)
df.to_parquet("contratos_2024_01.parquet")
