import json
from model.disease_model import Disease_Model
from plot.disease_dynamics_plot import plot_disease_dynamics
from tqdm import tqdm

def load_parameters(filename):
    with open(filename, 'r') as file:
        params = json.load(file)
    return params

def main():
    params = load_parameters('parameters/parameters.json')
    model = Disease_Model(**params)
    # Run the model
    for i in tqdm(range(100)): # Example: run for 100 steps
        model.step()
        #plot_disease_dynamics(model, i, plot_type='vaccine')
        plot_disease_dynamics(model, i, plot_type='recovered',dpi=100)
    # Optionally: Collect and analyze data

if __name__ == "__main__":
    main()

