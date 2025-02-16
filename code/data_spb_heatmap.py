import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

# Data URLs
url_data_Arbocel_A    = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Arbocel_A.csv"
url_data_Arbocel_B    = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Arbocel_B.csv"
url_data_MCC          = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_MCC.csv"
url_data_Wheat_Starch = "https://raw.githubusercontent.com/TjabbeN/SPB/refs/heads/main/data/data_Wheat_Starch.csv"

# DataFrames
df_data_Arbocel_A    = pd.read_csv(url_data_Arbocel_A, delimiter=";")
df_data_Arbocel_B    = pd.read_csv(url_data_Arbocel_B, delimiter=";")
df_data_MCC          = pd.read_csv(url_data_MCC, delimiter=";")
df_data_Wheat_Starch = pd.read_csv(url_data_Wheat_Starch, delimiter=";")

# Wood translation mapping
wood_translation = {
    'birne': 'Pear',
    'apfel': 'Apple',
    'esche': 'Ash',
    'kastanie': 'Chestnut',
    'rotbuche': 'Red beech',
    'ahorn': 'Maple'
}

def translate_wood_label(label, mapping):
    parts = label.split('_')
    if parts[0] in mapping:
        parts[0] = mapping[parts[0]]
    return "_".join(parts)

def plot_heatmap(ax, df, title, wood_map=None):
    """
    Clean the DataFrame and plot an annotated heatmap on the provided Axes.
    Also saves a reference to the colorbar as an attribute of the axis.
    """
    # Copy DataFrame and replace '-' with NaN
    df_clean = df.copy()
    df_clean.replace('-', np.nan, inplace=True)
    
    # Convert score columns to numeric
    for col in df_clean.columns[1:]:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Set first column as index (wood type labels)
    index_col = df_clean.columns[0]
    df_clean.set_index(index_col, inplace=True)
    
    # Optionally translate wood type labels
    if wood_map is not None:
        df_clean.index = [translate_wood_label(label, wood_map) for label in df_clean.index]
    
    # Create heatmap with imshow
    im = ax.imshow(df_clean.values, cmap='YlGnBu', vmin=0, vmax=10)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(df_clean.columns)))
    ax.set_xticklabels(df_clean.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(df_clean.index)))
    ax.set_yticklabels(df_clean.index, fontsize=8)
    
    # Annotate each cell, with white text for values 8 and 9
    for i in range(df_clean.shape[0]):
        for j in range(df_clean.shape[1]):
            value = df_clean.iloc[i, j]
            if np.isnan(value):
                text = ""
            else:
                text = f"{value:.0f}"
            text_color = "white" if (not np.isnan(value) and value in [8, 9]) else "black"
            ax.text(j, i, text, ha="center", va="center", color=text_color, fontsize=8)
    
    # Draw white horizontal borders between wood groups.
    wood_labels = df_clean.index.tolist()
    wood_groups = [label.split('_')[0] for label in wood_labels]
    for i in range(len(wood_groups) - 1):
        if wood_groups[i] != wood_groups[i+1]:
            ax.hlines(y=i + 0.5, xmin=-0.5, xmax=len(df_clean.columns)-0.5, colors='white', linewidth=2)
    
    ax.set_title(title, fontsize=10)
    
    # Create and store the colorbar.
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("cleaning effectiveness (0-10)", fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    ax.my_colorbar = cbar  # Store reference for later use

# Create a 2x2 grid of subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
plot_heatmap(axs[0, 0], df_data_Arbocel_A, "Arbocel A", wood_map=wood_translation)
plot_heatmap(axs[0, 1], df_data_Arbocel_B, "Arbocel B", wood_map=wood_translation)
plot_heatmap(axs[1, 0], df_data_MCC, "MCC", wood_map=wood_translation)
plot_heatmap(axs[1, 1], df_data_Wheat_Starch, "Wheat Starch", wood_map=wood_translation)

plt.tight_layout()
plt.show()

# IMPORTANT: Update the renderer so that all positions are finalized.
plt.draw()

# Save each subplot (axis + its colorbar) as an SVG file.
for i, ax in enumerate(axs.flatten()):
    renderer = fig.canvas.get_renderer()
    bbox_ax = ax.get_tightbbox(renderer)
    
    # Get the colorbar's bounding box if it exists.
    if hasattr(ax, "my_colorbar"):
        bbox_cb = ax.my_colorbar.ax.get_tightbbox(renderer)
        # Combine both bounding boxes using Bbox.union with a list.
        bbox = Bbox.union([bbox_ax, bbox_cb])
    else:
        bbox = bbox_ax

    # Convert the bounding box from display coordinates to inches.
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(f"subplot_{i+1}.svg", bbox_inches=bbox)
