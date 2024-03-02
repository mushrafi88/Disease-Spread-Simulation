import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
import os

def plot_disease_dynamics(model, step, dpi, plot_type='vaccine'):
    """
    Plot the disease dynamics for a given model state.

    Parameters:
    - model: The model instance.
    - step: The current simulation step (used for file naming).
    - plot_type: 'vaccine' or 'recovered' to determine the plot focus.
    """
    # Define colors and bounds
    cmap = mcolors.ListedColormap(['#D3D3D3', '#FFA500', '#00008B', '#e30e0e', '#FF00FF', '#32CD32'])
    bounds = [-1, 0, 1, 2, 3, 4, 5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # Ensure the output directory exists
    if not os.path.exists('results/agent_dynamics_images'):
            os.makedirs('results/agent_dynamics_images')

    output_dir = 'results/agent_dynamics_images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create the grid
    plt.figure(figsize=(10, 10))
    grid = np.full((model.grid.width, model.grid.height), -1)  # Initialize grid with -1 for empty locations
    for agent in model.schedule.agents:
        x, y = agent.pos
        if agent.infected_strain_1 and not (agent.vaccinated or agent.recovered_strain_1 or agent.recovered_strain_2):
            grid[x][y] = 2
        elif agent.infected_strain_2:
            grid[x][y] = 3
        elif (agent.recovered_strain_1 or agent.recovered_strain_2) and plot_type == 'recovered':
            grid[x][y] = 4
        elif agent.vaccinated and plot_type == 'vaccine':
            grid[x][y] = 1
        elif not (agent.vaccinated or agent.infected_strain_1 or agent.infected_strain_2):  # Susceptible (not vaccinated or infected)
            grid[x][y] = 0

    # Plot the grid
    plt.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
    plt.axis('on')
    plt.xticks([])  # Hide x-axis ticks
    plt.yticks([])  # Hide y-axis ticks

    # Save the figure
    plt.savefig(f'{output_dir}/image_{plot_type}_{step:03d}.png', dpi=dpi)
    plt.close()

