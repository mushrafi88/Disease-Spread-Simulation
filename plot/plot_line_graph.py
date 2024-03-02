import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
import os

# Define the color scheme globally
color_scheme = {
    'Infected_strain_1': '#377eb8',
    'Infected_strain_2': '#e41a1c',
    'Vaccinated': '#4daf4a',
    'Susceptible': '#984ea3', 
    'Recovered_strain_1': '#ff7f00',
    'Recovered_strain_2': '#f781bf'
}

output_dir = 'results/line_graph_images'
if not os.path.exists(output_dir):        
    os.makedirs(output_dir)

# Function to smooth data
def smooth_data(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def plot_line_graph(file_path, output_file=None, dpi=700):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Read data
    df = pd.read_csv(file_path)

    # Plot settings
    linestyles = ['--', '-.', '--', ':', (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]
    custom_lines = [Line2D([0], [0], color=color_scheme[category], lw=3, linestyle=linestyle) 
                    for category, linestyle in zip(color_scheme.keys(), linestyles)]

    # Plot each category
    for category, linestyle in zip(color_scheme.keys(), linestyles):
        ax.plot(smooth_data(df[category], 2), label=category.replace('_', ' ').title(),
                color=color_scheme[category], linestyle=linestyle, linewidth=3)

    # Extract mutation rate from file path for the title
    ax.set_title(f'Line graph', fontsize=16)

    # Configure axis and grid
    ax.set_xlabel('Epidemic Season')
    ax.set_ylabel('Population Count')
    ax.set_xticks(range(0, 201, 20))
    ax.set_xticklabels(range(0, int(201/10) + 1, 2))
    ax.set_xlim(0, 200)
    ax.set_ylim(0, df.max().max() + 100)  # Adjust y-limit to max value + 100 for some space
    ax.grid(False)

    # Add legend
    ax.legend(custom_lines, [category.replace('_', ' ').title() for category in color_scheme.keys()],
              loc='upper right', title='Categories')

    # Adjust layout and save/show the plot
    plt.tight_layout()
    plt.savefig(f'{output_dir}/line_graph.png', dpi=dpi, bbox_inches='tight')
    # Close the figure to free memory
    plt.close(fig)

