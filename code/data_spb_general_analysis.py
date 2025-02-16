import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from apply_graph_styling import apply_graph_styling

# Data URLs
url_data_Arbocel_A    = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Arbocel_A.csv"
url_data_Arbocel_B    = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Arbocel_B.csv"
url_data_MCC          = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_MCC.csv"
url_data_Wheat_Starch = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Wheat_Starch.csv"

# Dataframes
df_data_Arbocel_A = pd.read_csv(url_data_Arbocel_A, delimiter=";")
df_data_Arbocel_B = pd.read_csv(url_data_Arbocel_B, delimiter=";")
df_data_MCC = pd.read_csv(url_data_MCC, delimiter=";")
df_data_Wheat_Starch = pd.read_csv(url_data_Wheat_Starch, delimiter=";")

# wWod translation mapping
wood_translation = {
    'birne': 'Pear',
    'apfel': 'Apple',
    'esche': 'Ash',
    'kastanie': 'Chestnut',
    'rotbuche': 'Red Beech',
    'ahorn': 'Maple'
}

def translate_wood_label(label, mapping):
    parts = label.split('_')
    if parts[0] in mapping:
        parts[0] = mapping[parts[0]]
    return "_".join(parts)

# Rename the first column to "wood" for consistency.
df_data_Arbocel_A.rename(columns={df_data_Arbocel_A.columns[0]: 'wood'}, inplace=True)
df_data_Arbocel_B.rename(columns={df_data_Arbocel_B.columns[0]: 'wood'}, inplace=True)
df_data_MCC.rename(columns={df_data_MCC.columns[0]: 'wood'}, inplace=True)
df_data_Wheat_Starch.rename(columns={df_data_Wheat_Starch.columns[0]: 'wood'}, inplace=True)

# Add a column indicating the cleaning particle.
df_data_Arbocel_A['particle'] = 'Arbocel A'
df_data_Arbocel_B['particle'] = 'Arbocel B'
df_data_MCC['particle'] = 'MCC'
df_data_Wheat_Starch['particle'] = 'Wheat Starch'

# Combine the four dataframes vertically.
df_all = pd.concat([df_data_Arbocel_A, df_data_Arbocel_B, df_data_MCC, df_data_Wheat_Starch], ignore_index=True)

# Melt the dataframe to long format so that each row is a single measurement.
# 'wood' and 'particle' are identifier columns; the rest are soiling types.
soiling_cols = [col for col in df_all.columns if col not in ['wood', 'particle']]
df_long = df_all.melt(id_vars=['wood', 'particle'], 
                      value_vars=soiling_cols, 
                      var_name='soiling', 
                      value_name='effectiveness')

# Convert the "effectiveness" column to numeric (non-numeric values become NaN).
df_long['effectiveness'] = pd.to_numeric(df_long['effectiveness'], errors='coerce')
# Optionally, drop rows where the effectiveness is NaN.
df_long.dropna(subset=['effectiveness'], inplace=True)

# Apply the translation mapping to the wood column.
df_long['wood'] = df_long['wood'].apply(lambda x: translate_wood_label(x, wood_translation))

# Create new columns for grouping:
# - "wood_group": the prefix of the translated wood type (e.g., "Pear" from "Pear_t")
# - "side": the suffix (e.g., "t" or "q") for further analysis.
df_long['wood_group'] = df_long['wood'].apply(lambda x: x.split('_')[0])
df_long['side'] = df_long['wood'].apply(lambda x: x.split('_')[1] if '_' in x else np.nan)

# -------------------------------
# ANALYSIS 
# -------------------------------

# 1. Which cleaning particle was MOST effective on each wood group (t+q)?
eff_by_wood = df_long.groupby(['wood_group', 'particle'])['effectiveness'].mean().reset_index()
best_by_wood = eff_by_wood.loc[eff_by_wood.groupby('wood_group')['effectiveness'].idxmax()]
print("Best cleaning particle by wood group:")
print(best_by_wood)
print("#########################")

# 2. Which cleaning particle was LEAST effective on each wood group? 
eff_by_wood = df_long.groupby(['wood_group', 'particle'])['effectiveness'].mean().reset_index()
best_by_wood = eff_by_wood.loc[eff_by_wood.groupby('wood_group')['effectiveness'].idxmin()]
print("\nWorst cleaning particle by wood group:")
print(best_by_wood)
print("#########################")

# 3. For each soiling type, which cleaning particle was MOST effective?
eff_by_soiling = df_long.groupby(['soiling', 'particle'])['effectiveness'].mean().reset_index()
best_by_soiling = eff_by_soiling.loc[eff_by_soiling.groupby('soiling')['effectiveness'].idxmax()]
print("\nBest cleaning particle by soiling type:")
print(best_by_soiling)
print("#########################")

# 4. For each soiling type, which cleaning particle was LEAST effective?
eff_by_soiling = df_long.groupby(['soiling', 'particle'])['effectiveness'].mean().reset_index()
worst_by_soiling = eff_by_soiling.loc[eff_by_soiling.groupby('soiling')['effectiveness'].idxmin()]
print("\nWorst cleaning particle by soiling type:")
print(worst_by_soiling)
print("#########################")

# 5. Average effectiveness by side ("t" vs "q") for each cleaning particle.
eff_by_side = df_long.groupby(['side', 'particle'])['effectiveness'].mean().reset_index()
print("\nAverage effectiveness by side and particle:")
print(eff_by_side)
print("#########################")

# 6. Average effectiveness for each cleaning particle.
eff_mean = df_long.groupby('particle')['effectiveness'].mean().reset_index()
print("\nAverage effectiveness particles:")
print(eff_mean)
print("#########################")


# ------------
# Graphs
# ------------

column_map = {
    "Arbocel A": "#CF4C48",
    "Arbocel B": "#242B5F",
    "MCC": "#D6B863",
    "Wheat Starch": "#A0A0A0"
}

# Graph 1: Average Effectiveness by Wood Type.
group_by_wood = df_long.groupby(['wood_group', 'particle'])['effectiveness'].mean().unstack()
fig, ax = plt.subplots(figsize=(10, 6))
group_by_wood.plot(kind='bar', ax=ax)
apply_graph_styling(ax, column_color_map=column_map)

ax.set_title("Average Effectiveness by Wood Type")
ax.set_xlabel("Wood Type")
ax.set_ylabel("Average Effectiveness")
ax.legend(title="Cleaning Particle", bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0.)

plt.tight_layout()
plt.show()

# Graph 2: Average Effectiveness by Soiling Type.
custom_soiling_order = ["2H", "4B", "8B", "SN", "BA", "MB", "PP", "GO", "LI"]

group_by_soiling = df_long.groupby(['soiling', 'particle'])['effectiveness'].mean().unstack()
# Reindex the DataFrame to your desired order
group_by_soiling = group_by_soiling.reindex(custom_soiling_order)
fig, ax = plt.subplots(figsize=(10, 6))
group_by_soiling.plot(kind='bar', ax=ax)
apply_graph_styling(ax, column_color_map=column_map)

ax.set_title("Average Effectiveness by Soiling Type")
ax.set_xlabel("Soiling Type")
ax.set_ylabel("Average Effectiveness")
ax.legend(title="Cleaning Particle", bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0.)

plt.tight_layout()
plt.show()

# Graph 3: Average Effectiveness by Side ("t" vs "q").
group_by_side = df_long.groupby(['side', 'particle'])['effectiveness'].mean().unstack()
fig, ax = plt.subplots(figsize=(6, 6))
group_by_side.plot(kind='bar', ax=ax)
apply_graph_styling(ax, column_color_map=column_map)

ax.set_title("Average Effectiveness by Side")
ax.set_xlabel("Side (t = transverse, q = cross-section)")
ax.set_ylabel("Average Effectiveness")
ax.legend(title="Cleaning Particle", bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0.)

plt.tight_layout()
plt.show()

# Graph 4: Overall Average Effectiveness by Cleaning Particle.
overall_eff = df_long.groupby('particle')['effectiveness'].mean()
fig, ax = plt.subplots(figsize=(6, 6))
overall_eff.plot(kind='bar', ax=ax)
apply_graph_styling(ax, single_data_color="#CF4C48")

ax.set_title("Average Effectiveness of Particles")
ax.set_xlabel("Cleaning Particle")
ax.set_ylabel("Average Effectiveness")

plt.tight_layout()
plt.show()

