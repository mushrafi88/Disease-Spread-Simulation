import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd
import os

def generate_heatmap_for_folder(output_dir='results/heatmap_images', interval=50, dpi=500, alphas=[0.2, 0.5, 0.8]):
    mpl.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})

    vmin_1, vmax_1 = 0.2, 0.95  # Adjust these values as needed for strain 1
    vmin_2, vmax_2 = 0.15, 0.9  # Adjust for strain 2
    vmin_3, vmax_3 = 0.5, 0.95  # Adjust for total infection

    interpolation = 'nearest'  # 'nearest' or 'bicubic'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fig, axes = plt.subplots(3, 3, figsize=(30, 30), gridspec_kw={'left': 0.08, 'bottom': 0.06})

    plt.figtext(0.475, 0.03, 'Vaccine Effectiveness Strain 2', ha='center', fontsize=24)
    plt.figtext(0.03, 0.475, 'Vaccine Effectiveness Strain 1', va='center', rotation='vertical', fontsize=24)

    for i, alpha in enumerate(alphas):
        file_name = f'heatmap_alpha_{alpha}.csv'
        
        df = pd.read_csv(os.path.join('results/heatmap_data', file_name))

        for j in range(3):
            ax = axes[i, j]
            heatmap_data = df.pivot("vaccine_effectiveness_strain_1", "vaccine_effectiveness_strain_2", f"final_size_strain_{j+1}" if j < 2 else "total_infection")
            vmin, vmax = (vmin_1, vmax_1) if j == 0 else (vmin_2, vmax_2) if j == 1 else (vmin_3, vmax_3)
            cax = ax.imshow(heatmap_data.values, interpolation=interpolation, origin='lower',
                            extent=[0, 1, 0, 1], cmap='rainbow', vmin=vmin, vmax=vmax)

            if i == 0:
                ax.set_title(f'{"Strain " + str(j+1) if j < 2 else "Total Infection"}', fontsize=20)
            if j == 0:
                ax.set_ylabel(f'$\\alpha = {alpha}$', fontsize=24, rotation=90, labelpad=20)

    plt.subplots_adjust(wspace=0.1, hspace=0.0)

    norm = Normalize(vmin=0, vmax=1)
    scalar_map = ScalarMappable(norm=norm, cmap='rainbow')
    cbar = fig.colorbar(scalar_map, ax=axes.ravel().tolist(), location='right', fraction=0.02, pad=0.025)
    cbar.set_label('Final Epidemic Size', fontsize=18, labelpad=10)

    plt.savefig(f'{output_dir}/heatmap.png', dpi=dpi, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_heatmap_for_folder()

