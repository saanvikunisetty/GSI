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
import os

def clean_label(label):
    stop_phrases = [
        "which of the following", "please select all that apply", "options for",
        "are undertaken by your agency", "referred to in the question above",
        "does the geographical area of your agency's jurisdiction", "please check all that apply",
        "please select all that apply", "most common", "following the implementation of",
        "have you observed any changes in", "the question above", "please select one"
    ]

    stopwords = set([
        "the", "of", "and", "to", "a", "in", "for", "that", "with", "by",
        "on", "your", "are", "or", "is", "as", "at", "this", "from", "which",
        "any", "such", "above", "have", "been", "will", "be", "through", "other",
        "please", "select", "all", "applicable"
    ])

    label = label.lower()
    for phrase in stop_phrases:
        label = label.replace(phrase, "")
    label = re.sub(r"\s+", " ", label).strip()

    if "—" in label:
        label = label.split("—")[-1].strip()
    elif ":" in label:
        label = label.split(":")[-1].strip()
    elif "(" in label and ")" in label:
        label = re.sub(r"\(.*?\)", "", label).strip()

    words = [w for w in re.findall(r"\w+", label) if w not in stopwords]

    label = " ".join(words[:5])
    label = label.title()
    return label

def plot_agency_activity_frequency(csv_path):
    df = pd.read_csv(csv_path)
    binary_columns = [col for col in df.columns if '—' in col]
    totals = df[binary_columns].sum().sort_values(ascending=False)

    cleaned_labels = [clean_label(str(lbl)) for lbl in totals.index]

    plt.figure(figsize=(14, 9))
    bars = plt.bar(cleaned_labels, totals.values, color=plt.cm.viridis(range(len(totals))))

    plt.title('Frequency of Selected Activities Across Agencies', fontsize=18, weight='bold')
    plt.ylabel('Number of Agencies', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.tight_layout()

    save_dir = 'plots'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, 'agency_activity_frequency.png')
    plt.savefig(save_path, dpi=300)
    print("Plot saved to", save_path)

    plt.show()

#plot_agency_activity_frequency("cleaned_survey_data1.csv")

for i, col in enumerate(binary_columns):
    print("%d: %s" % (i, col))