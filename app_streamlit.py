import streamlit as st
import json
from model.disease_model import Disease_Model
from plot.disease_dynamics_plot import plot_disease_dynamics
from plot.eta_evolution_plot import plot_eta_evolution
from plot.plot_line_graph import plot_line_graph
import imageio
import os
from PIL import Image

# Function to load parameters, potentially modified to take arguments from Streamlit UI
def load_parameters(filename):
    with open(filename, 'r') as file:
        params = json.load(file)
    return params

# Assuming your images are saved in 'results/images/' and follow a naming convention 'output_epoch_{i}.png'
def create_gif(epoch_count, output_gif_path='results/output.gif', images_folder='results/eta_evolution_images'):
    images = []
    for i in range(epoch_count):
        image_path = os.path.join(images_folder, f'alpha_{model.alpha}_image_{i:03d}.png')
        images.append(imageio.imread(image_path))
    imageio.mimsave(output_gif_path, images, fps=1)  # Adjust fps to control speed of the GIF

# Your main simulation function, adapted to run from Streamlit inputs
def run_simulation(params):
    model = Disease_Model(**params)
    output_dir = 'results/line_graph_data'
    if not os.path.exists(output_dir):        
        os.makedirs(output_dir)
    for i in range(params['epochs']): # Use the epoch parameter from the UI
        model.step()
        # Depending on your plotting functions, you might need to adapt them
        # to save the figures instead of showing them directly.
    model_data = model.datacollector.get_model_vars_dataframe()
    model_data.to_csv(f'results/line_graph_data_alpha_{model.alpha}.csv', index=False)
    plot_line_graph(f'results/line_graph_data_alpha_{model.alpha}.csv', dpi = 100)
    # Generate or save your output GIF here, after the simulation

# Streamlit UI
st.title('Game-Theoretic Disease Spread Simulation')

# Form for parameters
with st.form(key='parameters_form'):
    alpha = st.number_input('Alpha', value=0.1)
    epochs = st.slider('Epochs', min_value=10, max_value=1000, value=50)
    submit_button = st.form_submit_button(label='Run Simulation')

if submit_button:
    params = {'alpha': alpha, 'epochs': epochs}
    run_simulation(params)
    # After simulation, create the GIF
    create_gif(epochs, 'results/output.gif')

    # Display the output GIF
    st.image('results/output.gif', caption='Simulation Results')
