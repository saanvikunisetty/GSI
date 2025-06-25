import pandas as pd
df = pd.read_csv("survey.csv")
#print(df)

df.columns = [col.split(":")[0].strip() for col in df.columns]
#print(df.columns)

df = df.drop(columns=["Status", 
                      "Contact ID", 
                      "Link Name", 
                      "URL Variable", 
                      "Invite Status",
                      "Survey Batch",
                      "Email",
                      "First Name",
                      "Last Name",
                      "Start of Survey" 
                      "Time Started"], 
                      errors='ignore')

multi_select_cols = [
    col for col in df.columns 
    if "please select all" in col.lower() or "please check all" in col.lower()
]

#print("Multi-select columns:", multi_select_cols)

import re
from html import unescape

for col in multi_select_cols:
    all_options = set()
    df[col] = df[col].fillna('')
    for entry in df[col]:
        options = [opt.strip() for opt in re.split(',|;', entry) if opt.strip()]
        all_options.update(options)
    new_cols = []
    for option in all_options:
        cleaned_option = unescape(re.sub(r'<.*?>', '', option))
        new_col_name = col + " — " + cleaned_option
        df[new_col_name] = df[col].apply(lambda x: 1 if option in x else 0)
        new_cols.append(new_col_name)
    print("Options for: " + col)
    for name in new_cols:
        short = name.replace(col + " — ", "")
        print("- " + short)
    print(df[new_cols].head().T)