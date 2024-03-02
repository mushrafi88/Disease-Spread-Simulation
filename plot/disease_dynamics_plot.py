import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
import os

def plot_disease_dynamics(model, step, dpi):
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
        os.makedirs('results/agent_dynamics_images/recovered')
        os.makedirs('results/agent_dynamics_images/vaccinated')

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
        elif agent.vaccinated:
            grid[x][y] = 1
        elif (agent.recovered_strain_1 or agent.recovered_strain_2):
            grid[x][y] = 4
        elif not (agent.vaccinated or agent.infected_strain_1 or agent.infected_strain_2):  # Susceptible (not vaccinated or infected)
            grid[x][y] = 0
  
    # Plot the grid
    plt.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
    plt.title('Disease Spread Simulation (Vaccine) Step: ' + str(step)) 
    labels = ['Empty', 'Susceptible', 'Vaccinated', 'Infected with Strain 1', 'Infected with Strain 2', 'Recovered']
    colors = ['#D3D3D3', '#FFA500', '#00008B', '#e30e0e', '#FF00FF', '#32CD32']  # Light Grey, Bright Orange, Deep Sky Blue, Crimson Red, Medium Orchid, Lime Green

    patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]
    plt.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, ncol=len(labels),fontsize='small')
    plt.axis('on')
    plt.xticks([])  # Hide x-axis ticks
    plt.yticks([])  # Hide y-axis ticks

    # Save the figure
    plt.savefig(f'{output_dir}/vaccinated/image_vaccine_{step:03d}.png', dpi=dpi, bbox_inches='tight')
    plt.close() 
    # recovered 
    plt.figure(figsize=(10, 10))
    grid = np.full((model.grid.width, model.grid.height), -1)  # Initialize grid with -1 for empty locations
    for agent in model.schedule.agents:
        x, y = agent.pos
        if agent.infected_strain_1 and not (agent.vaccinated or agent.recovered_strain_1 or agent.recovered_strain_2):
            grid[x][y] = 2
        elif agent.infected_strain_2:
            grid[x][y] = 3
        elif (agent.recovered_strain_1 or agent.recovered_strain_2):
            grid[x][y] = 4
        elif agent.vaccinated:
            grid[x][y] = 1
        elif not (agent.vaccinated or agent.infected_strain_1 or agent.infected_strain_2):  # Susceptible (not vaccinated or infected)
            grid[x][y] = 0
    img = plt.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
    plt.title('Disease Spread Simulation (Recovered) Step: ' + str(step))
    labels = ['Empty', 'Susceptible', 'Vaccinated', 'Infected with Strain 1', 'Infected with Strain 2', 'Recovered']
    colors = ['#D3D3D3', '#FFA500', '#00008B', '#e30e0e', '#FF00FF', '#32CD32']  # Light Grey, Bright Orange, Deep Sky Blue, Crimson Red, Medium Orchid, Lime Green

    patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]
    plt.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, ncol=len(labels),fontsize='small')
    plt.axis('on')  # Turn on the axis
    plt.xticks([])  # Hide x-axis ticks
    plt.yticks([])

    plt.savefig(f'{output_dir}/recovered/image_recovered_{step:03d}.png', dpi=dpi, bbox_inches='tight')
    plt.close()


