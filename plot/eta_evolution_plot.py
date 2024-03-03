import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import cm

def plot_eta_evolution(model, step, dpi=700):
    """
    Plots the evolution of eta values for each agent in the model.

    Parameters:
    - model: Instance of Disease_Model.
    - step: Current step in the simulation.
    - dpi: Dots per inch for the output image.
    """
    # Ensure the output directory exists
    output_dir = 'results/agent_dynamics_images/eta_evolution'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize the eta grid
    eta_grid = np.full((model.grid.width, model.grid.height), 0.2)  # Use 0.2 for cells without agents

    # Populate the grid with eta values
    for agent in model.schedule.agents:
        x, y = agent.pos
        eta_grid[x, y] = agent.eta

    # Plotting
    plt.figure(figsize=(10, 10))
    cmap = cm.get_cmap('rainbow_r')
    img = plt.imshow(eta_grid, cmap=cmap, interpolation='nearest', vmin=0, vmax=1.0)
    plt.title(r"Evolution of $\eta$  Values  - Step: " + str(step))
    cbar = plt.colorbar(img, orientation='horizontal', pad=0.05, aspect=30, shrink=0.5)
    cbar.set_label(r'$\eta$ value', labelpad=-40, y=0.45, rotation=0)

    plt.axis('on')  # Hide axes
    plt.xticks([])
    plt.yticks([])

    # Save the plot
    plt.savefig(f'{output_dir}/image_eta_evolution_{model.alpha}_{step:03d}.png', dpi=dpi, bbox_inches='tight')
    plt.close()  # Close the figure to free memory

