import json
from model.disease_model import Disease_Model
from plot.disease_dynamics_plot import plot_disease_dynamics
from plot.eta_evolution_plot import plot_eta_evolution
from plot.plot_line_graph import plot_line_graph
from plot.recovered_to_infected_ratio_plot import generate_ratio_plots
from tqdm import tqdm
import os

def load_parameters(filename):
    with open(filename, 'r') as file:
        params = json.load(file)
    return params

output_dir = 'results/line_graph_data'
if not os.path.exists(output_dir):        
    os.makedirs(output_dir)

def main():
    params = load_parameters('parameters/parameters.json')
    model = Disease_Model(**params)
    # Run the model
    for i in tqdm(range(100)): # Example: run for 100 steps
        model.step()
        #plot_disease_dynamics(model, i, plot_type='vaccine')
        plot_disease_dynamics(model, i,dpi=100)
        plot_eta_evolution(model, i, dpi=100)
    # Optionally: Collect and analyze data
    model_data = model.datacollector.get_model_vars_dataframe()
                    # Save the data to a CSV file
    model_data.to_csv(f'results/line_graph_data/line_graph_data_alpha_{model.alpha}.csv', index=False)
    plot_line_graph(f'results/line_graph_data/line_graph_data_alpha_{model.alpha}.csv', dpi = 100)
    generate_ratio_plots(alpha = model.alpha, file_path=f'results/line_graph_data/line_graph_data_alpha_{model.alpha}.csv', dpi = 100)
if __name__ == "__main__":
    main()

