import pandas as pd

caminho = r"C:\Users\Usuario\mineracao\contratacoes_sm_rs_260101_261019.csv"
df = pd.read_csv(caminho, sep=";")
print("Tamanho:", df.shape)

#só as que tem valor estimado e homologado
df = df[(df["valorTotalEstimado"] > 0) & (df["valorTotalHomologado"] > 0)].copy()
print("Homologadas:", df.shape)

# diferença e % de economia
df["economia_abs"] = df["valorTotalEstimado"] - df["valorTotalHomologado"]
df["economia_pct"] = df["economia_abs"] / df["valorTotalEstimado"] * 100
print(df[["valorTotalEstimado", "valorTotalHomologado", "economia_pct"]].describe())