import pandas as pd
df = pd.read_csv("survey.csv")
#print(df)

df.columns = [col.split(":")[0].strip() for col in df.columns]
print(df.columns)