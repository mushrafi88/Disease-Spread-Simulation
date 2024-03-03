import streamlit as st
import json
from model.disease_model import Disease_Model
from plot.disease_dynamics_plot import plot_disease_dynamics
from plot.eta_evolution_plot import plot_eta_evolution
from plot.plot_line_graph import plot_line_graph
from plot.recovered_to_infected_ratio_plot import generate_ratio_plots
import imageio
import os
from PIL import Image
from pathlib import Path 

# Load parameters from JSON file
def load_parameters():
    params_path = Path('parameters/parameters.json')
    with params_path.open('r') as file:
        params = json.load(file)
    return params

params = load_parameters()

def create_gif(epoch_count, model_alpha, image_type, output_gif_path='results/output.gif', base_images_folder='results/agent_dynamics_images'):
    images = []
    images_folder = os.path.join(base_images_folder, image_type)  # Adjust path based on image type
    for i in range(epoch_count):
        image_path = os.path.join(images_folder, f'image_{image_type}_{model_alpha}_{i:03d}.png')
        images.append(imageio.imread(image_path))
    imageio.mimsave(output_gif_path, images, fps=1)  # Adjust fps as needed

# Main simulation function, adapted to run from Streamlit inputs
def run_simulation(params, epochs):
    model = Disease_Model(**params)  # Initialize the model with parameters
    output_dir = 'results/line_graph_data'
    if not os.path.exists(output_dir):        
        os.makedirs(output_dir) 
    for i in range(epochs):  # Loop for the specified number of epochs
        model.step()
        plot_disease_dynamics(model, i,dpi=100)
        plot_eta_evolution(model, i, dpi=100)
        # Your plotting/saving code here, adjusted as needed
        
    # After running the simulation, collect and process results
    model_data = model.datacollector.get_model_vars_dataframe()
    model_data.to_csv(f'results/line_graph_data/line_graph_data_alpha_{model.alpha}.csv', index=False)
    plot_line_graph(f'results/line_graph_data/line_graph_data_alpha_{model.alpha}.csv', dpi=100)
    
    # Create GIFs for each category of images
    gif_output_paths = {
        'vaccinated': f'results/vaccinated_alpha_{params["alpha"]}.gif',
        'recovered': f'results/recovered_alpha_{params["alpha"]}.gif',
        'eta_evolution': f'results/eta_evolution_alpha_{params["alpha"]}.gif'
    }
    
    for image_type, output_path in gif_output_paths.items():
        create_gif(epochs, params['alpha'], image_type, output_path, base_images_folder='results/agent_dynamics_images')

st.title('Game-Theoretic Disease Spread Simulation')

# Editable parameters form
with st.form(key='parameters_form'):
    # Create a UI element for each parameter
    for param, value in params.items():
        if isinstance(value, bool):
            params[param] = st.checkbox(f"{param}", value)
        elif isinstance(value, int):
            params[param] = st.number_input(f"{param}", value=value, format="%d")
        elif isinstance(value, float):
            params[param] = st.number_input(f"{param}", value=value, step=0.001, format="%.3f")
        elif isinstance(value, (list, dict)):  # Example for handling complex types, adjust as needed
            # For complex types, you might want to use text_area and parse the input as JSON
            raw_json = st.text_area(f"{param}", value=json.dumps(value))
            params[param] = json.loads(raw_json)
        else:
            st.text_input(f"{param}", value=str(value))
    
    epochs = st.slider('Epochs', min_value=10, max_value=1000, value=50)
    submit_button = st.form_submit_button(label='Run Simulation')

if submit_button:
    model_specific_params = {k: v for k, v in params.items() if k != 'epochs'}
    run_simulation(model_specific_params, epochs)
    m_alpha = params['alpha']
    strain_1_plot, strain_2_plot = generate_ratio_plots(alpha = m_alpha, file_path=f'results/line_graph_data/line_graph_data_alpha_{m_alpha}.csv', dpi = 500)
    # Display the output GIF
    st.image(f'results/vaccinated_alpha_{params["alpha"]}.gif', caption='Vaccinated Agents Dynamics')
    st.image(f'results/recovered_alpha_{params["alpha"]}.gif', caption='Recovered Agents Dynamics')
    st.image(f'results/eta_evolution_alpha_{params["alpha"]}.gif', caption='Eta Evolution Dynamics')

    # Display the plots in Streamlit
    st.image(strain_1_plot, caption='Recovered to Infected Ratio Over Time for Strain 1')
    st.image(strain_2_plot, caption='Recovered to Infected Ratio Over Time for Strain 2')



