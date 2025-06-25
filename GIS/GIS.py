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

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

plt.figure(figsize=(14, 9))

colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(totals)))

bars = totals.plot(kind='bar', color=colors, edgecolor='black', linewidth=0.8)

plt.title('Frequency of Selected Activities Across Agencies', fontsize=20, weight='bold', pad=20)
plt.suptitle('Survey of Agency Responsibilities and Practices', fontsize=14, y=0.93, alpha=0.7)
plt.ylabel('Number of Agencies', fontsize=16, weight='bold')
plt.xlabel('Activity', fontsize=16, weight='bold')

plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)

plt.grid(axis='y', linestyle='--', alpha=0.6)

for bar in bars.patches:
    height = bar.get_height()
    bars.annotate(str(int(height)),
                  xy=(bar.get_x() + bar.get_width() / 2, height),
                  xytext=(0, 5), 
                  textcoords="offset points",
                  ha='center', va='bottom',
                  fontsize=11,
                  fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.95]) 

import os
if not os.path.exists('plots'):
    os.makedirs('plots')
plt.savefig('plots/agency_activity_frequency.png', dpi=300)
plt.show()
