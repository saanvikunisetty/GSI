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
        cleaned_entry = re.sub(r'<.*?>', '', entry)
        cleaned_entry = re.sub(r'title=".*?"', '', cleaned_entry)
        cleaned_entry = re.sub(r'["“”]', '', cleaned_entry)
        cleaned_entry = unescape(cleaned_entry)
        options = [opt.strip() for opt in re.split(',|;', cleaned_entry) if opt.strip()]
        all_options.update(options)
    
    new_cols = []
    for option in all_options:
        new_col_name = col + " — " + option
        df[new_col_name] = df[col].apply(lambda x: 1 if option in x else 0)
        new_cols.append(new_col_name)
    
    #print("\nOptions for:", col)
    for name in new_cols:
        short = name.replace(col + " — ", "")
        #print("-", short)
    
    #print("\nBinary columns created:")
    #print(df[new_cols].columns.tolist())
    #print("\nFirst few rows:")
    #print(df[new_cols].head().T)

#df.to_csv('cleaned_survey_data1.csv', index=False)

#Plot 1:
import matplotlib.pyplot as plt
binary_columns = [col for col in df.columns if '—' in col]
totals = df[binary_columns].sum().sort_values(ascending=False)
