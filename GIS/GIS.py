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

#for i, col in enumerate(binary_columns):
    #print("%d: %s" % (i, col))

rename_dict = {
    # Stormwater management activities
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — construction or installation of structural practices for managing stormwater runoff":
        "Structural Practice Installation",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Other (please specify):":
        "Other Stormwater Activities",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Reviewing stormwater management plans in the site plans of proposed construction projects":
        "Stormwater Plan Review",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — My agency does not have stormwater management responsibilities":
        "No Stormwater Responsibility",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Maintaining stormwater infrastructure in a municipal separate storm sewer system (MS4) and/or combined sewer system (CSS)":
        "Infrastructure Maintenance",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Inspecting post-construction stormwater controls to ensure compliance with municipal stormwater ordinances or MS4 permit requirements":
        "Post-Construction Inspection",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Developing long-term plans for improvements to publicly-managed stormwater infrastructure":
        "Long-Term Infrastructure Planning",
    "Which of the following activities or responsibilities related to stormwater management are undertaken by your agency? Please check all that apply. — Engineering":
        "Engineering",

    # Jurisdiction areas (stormwater)
    "Does the geographical area of your agency's jurisdiction for managing stormwater runoff extend to municipalities within any of the following states? Please select all that apply. — Minnesota":
        "Jurisdiction: Minnesota",
    "Does the geographical area of your agency's jurisdiction for managing stormwater runoff extend to municipalities within any of the following states? Please select all that apply. — North Dakota":
        "Jurisdiction: North Dakota",

    # Stormwater control objectives in retrofit projects
    "What is the most common stormwater control objective(s) of  retrofit projects including  Green Infrastructure practices that have been or will be completed through the involvement of your agency? Please select all that apply. — Moderating peak runoff flow rate":
        "Moderate Peak Runoff Flow",
    "What is the most common stormwater control objective(s) of  retrofit projects including  Green Infrastructure practices that have been or will be completed through the involvement of your agency? Please select all that apply. — Reduction in runoff volume":
        "Reduce Runoff Volume",
    "What is the most common stormwater control objective(s) of  retrofit projects including  Green Infrastructure practices that have been or will be completed through the involvement of your agency? Please select all that apply. — trash/floatables":
        "Control Trash and Floatables",
    "What is the most common stormwater control objective(s) of  retrofit projects including  Green Infrastructure practices that have been or will be completed through the involvement of your agency? Please select all that apply. — Other (please describe)":
        "Other Control Objectives",
    "What is the most common stormwater control objective(s) of  retrofit projects including  Green Infrastructure practices that have been or will be completed through the involvement of your agency? Please select all that apply. — Improving runoff water quality (e.g. capturing suspended or soluble contaminants":
        "Improve Runoff Water Quality",

    # Private property structural practices recommended
    "Do the public educational/informational tools referred to in the question above recommend that private property owners construct or install any of the following structural practices to infiltrate or capture runoff discharged from the disconnected downspout? Please check all that apply. — Dry wells":
        "Dry Wells",
    "Do the public educational/informational tools referred to in the question above recommend that private property owners construct or install any of the following structural practices to infiltrate or capture runoff discharged from the disconnected downspout? Please check all that apply. — Rain barrels / cisterns":
        "Rain Barrels and Cisterns",
    "Do the public educational/informational tools referred to in the question above recommend that private property owners construct or install any of the following structural practices to infiltrate or capture runoff discharged from the disconnected downspout? Please check all that apply. — Rain gardens":
        "Rain Gardens",

    # Mosquito surveillance/control activities
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — such as the application of insecticides (“larvicides”)":
        "Larvicide Application",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Other (please specify):":
        "Other Mosquito Activities",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Adult mosquito surveillance (i.e. trapping of adult mosquitoes)":
        "Adult Mosquito Surveillance",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — the introduction or conservation of natural control agents (example: predaceous fish)":
        "Natural Control Agents",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — such as the distribution of public education materials to home owners and providing recommendations to other public agencies and private land developers on how to manage water resources to reduce or prevent mosquito production in aquatic habitats":
        "Mosquito Public Education",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Larval mosquito surveillance by inspection of stormwater structural practices or other aquatic habitats for the presence of larval mosquitoes":
        "Larval Mosquito Surveillance",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Larval mosquito control by direct interventions":
        "Direct Larval Control",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Adult mosquito control using aerial or ground based application of insecticides (“adulticides”)":
        "Adult Mosquito Control",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — or by the removal or physical modification of aquatic habitats (“source reduction”)":
        "Source Reduction",
    "Which of the following activities or responsibilities related to mosquito surveillance or control are undertaken by your agency? Please check all that apply. — Larval mosquito control by indirect means":
        "Indirect Larval Control",

    # Jurisdiction areas for mosquito control
    "Does the geographical area of your agency's jurisdiction for mosquito control or surveillance extend to municipalities within any of the following states? Please select all that apply. — Minnesota":
        "Mosquito Jurisdiction Minnesota",
    "Does the geographical area of your agency's jurisdiction for mosquito control or surveillance extend to municipalities within any of the following states? Please select all that apply. — North Dakota":
        "Mosquito Jurisdiction North Dakota",

    # Changes observed after green infrastructure implementation
    "Following the implementation of  Green Infrastructure practices in your agencyâ€™s jurisdiction, have you observed any changes in adjacent  structural practices or other aquatic habitats that previously supported mosquito production (e.g. â€œdownstreamâ€ stormwater catch basins)? Please check all that apply. — Duration stormwater runoff is retained in adjacent structural practices or other aquatic habitats":
        "Change in Runoff Retention Duration",
    "Following the implementation of  Green Infrastructure practices in your agencyâ€™s jurisdiction, have you observed any changes in adjacent  structural practices or other aquatic habitats that previously supported mosquito production (e.g. â€œdownstreamâ€ stormwater catch basins)? Please check all that apply. — Other (please describe)":
        "Other Changes Observed",
    "Following the implementation of  Green Infrastructure practices in your agencyâ€™s jurisdiction, have you observed any changes in adjacent  structural practices or other aquatic habitats that previously supported mosquito production (e.g. â€œdownstreamâ€ stormwater catch basins)? Please check all that apply. — Volume of stormwater collecting in adjacent structural practices or other aquatic habitats":
        "Change in Runoff Volume",
    "Following the implementation of  Green Infrastructure practices in your agencyâ€™s jurisdiction, have you observed any changes in adjacent  structural practices or other aquatic habitats that previously supported mosquito production (e.g. â€œdownstreamâ€ stormwater catch basins)? Please check all that apply. — No changes observed":
        "No Changes Observed",
}

def plot_agency_activity_frequency(csv_path):
    df = pd.read_csv(csv_path)

    df.rename(columns=rename_dict, inplace=True)

    binary_columns = [col for col in df.columns if '—' in col or col in rename_dict.values()]
    totals = df[binary_columns].sum().sort_values(ascending=False)

    cleaned_labels = totals.index  

    plt.figure(figsize=(14, 9))
    bars = plt.bar(cleaned_labels, totals.values, color=plt.cm.viridis(range(len(totals))))

    plt.title('Frequency of All Responses Across Agencies', fontsize=18, weight='bold')
    plt.ylabel('Number of Agencies', fontsize=14)

    plt.xticks(rotation=45, ha='right', fontsize=6)
    plt.subplots_adjust(bottom=0.35)  
    plt.tight_layout()

    save_dir = 'plots'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, 'agency_activity_frequency.png')
    plt.savefig(save_path, dpi=300)

    plt.show()

df.to_csv("cleaned_survey_data2.csv", index=False)
plot_agency_activity_frequency("cleaned_survey_data2.csv")

def load_and_prepare_df(path, rename_dict):
    df = pd.read_csv(path)
    df.rename(columns=rename_dict, inplace=True)
    return df

#Stormwater Management Activities Frequency Plot
import seaborn as sns
import numpy as np
import matplotlib.ticker as mticker
df = load_and_prepare_df("cleaned_survey_data2.csv", rename_dict)

stormwater_cols = [
    "Structural Practice Installation", "Other Stormwater Activities", "Stormwater Plan Review",
    "No Stormwater Responsibility", "Infrastructure Maintenance", "Post-Construction Inspection",
    "Long-Term Infrastructure Planning", "Engineering"
]

totals = df[stormwater_cols].sum().sort_values(ascending=True)

plt.figure(figsize=(10, 6))
colors = ["#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b", "#041e42"]
plt.barh(totals.index, totals.values, color=colors)

ax = plt.gca()
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))  
ax.xaxis.set_minor_locator(mticker.MultipleLocator(1))   

ax.grid(which='minor', axis='x', linestyle='--', alpha=0.3)  
ax.grid(which='major', axis='x', linestyle='-', alpha=0.1)  

plt.title("Stormwater Management Activities", fontsize=16, weight='bold')
plt.xlabel("Number of Agencies")
plt.ylabel("Activity")
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.tight_layout()

save_path = os.path.join("plots", "stormwater_activities.png")
plt.savefig(save_path, dpi=300)
plt.show()
print("Saved:", save_path)

#Stormwater Jurisdiction Area Frequency Plot

df = load_and_prepare_df("cleaned_survey_data2.csv", rename_dict)

jurisdiction_storm_cols = [
    "Jurisdiction: Minnesota", "Jurisdiction: North Dakota"
]

totals = df[jurisdiction_storm_cols].sum().sort_values(ascending=True)

plt.figure(figsize=(7, 4))
colors = ["#2ca02c", "#98df8a"]
plt.barh(totals.index, totals.values, color=colors)

plt.title("Stormwater Jurisdiction Areas", fontsize=16, weight='bold')
plt.xlabel("Number of Agencies")

ax = plt.gca()
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(1))

ax.grid(which='minor', axis='x', linestyle='--', alpha=0.3)
ax.grid(which='major', axis='x', linestyle='-', alpha=0.1)

plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.tight_layout()

save_path = os.path.join("plots", "stormwater_jurisdiction.png")
plt.savefig(save_path, dpi=300)
plt.show()