import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import os
import json
from model.disease_model import Disease_Model
from plot.heatmap_image_generator import generate_heatmap_for_folder 

def load_parameters(filename):
    with open(filename, 'r') as file:
        params = json.load(file)
    return params

def run_simulation(param_overrides, epochs):
    base_params = load_parameters('parameters/parameters.json')
    # Update base_params with the overrides, excluding 'epochs'
    base_params.update(param_overrides)
    
    model = Disease_Model(**base_params)
    for _ in range(epochs):
        model.step()
    
    final_size_strain_1 = model.count_infected_strain_1() / model.num_agents
    final_size_strain_2 = model.count_infected_strain_2() / model.num_agents
    
    return {
        "vaccine_effectiveness_strain_1": base_params['vaccine_effectiveness_strain_1'],
        "vaccine_effectiveness_strain_2": base_params['vaccine_effectiveness_strain_2'],
        "final_size_strain_1": final_size_strain_1,
        "final_size_strain_2": final_size_strain_2,
        "total_infection": final_size_strain_1 + final_size_strain_2
    }

def generate_heatmaps(base_params, epochs=75, output_dir='results/heatmap_data', interval=10, alphas=[0.2, 0.5, 0.8]):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    vaccine_effectiveness_strain_1_values = np.linspace(0, 1, num=interval)
    vaccine_effectiveness_strain_2_values = np.linspace(0, 1, num=interval)
    
    for alpha in alphas:
        simulation_params = [
            ({"vaccine_effectiveness_strain_1": ve1,
              "vaccine_effectiveness_strain_2": ve2,
              "alpha": alpha}, epochs)
            for ve1 in vaccine_effectiveness_strain_1_values
            for ve2 in vaccine_effectiveness_strain_2_values
        ]
        
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_simulation, param[0], param[1]) for param in simulation_params]
            results = [f.result() for f in tqdm(futures, total=len(futures))]
        
        results_df = pd.DataFrame(results)
        results_df.to_csv(f'{output_dir}/heatmap_alpha_{alpha}.csv', index=False)
        generate_heatmap_for_folder()

if __name__ == "__main__":
    base_params = load_parameters('parameters/parameters.json')
    generate_heatmaps(base_params, epochs=40, interval=10)

