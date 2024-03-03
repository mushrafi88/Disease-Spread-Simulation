import pandas as pd
import matplotlib.pyplot as plt 

def generate_ratio_plots(alpha, dpi, file_path):
    df = pd.read_csv(file_path)

    # Calculate the recovered to infected ratio for both strains
    df['Recovered_to_Infected_Ratio_Strain_1'] = df['Recovered_strain_1'] / df['Infected_strain_1']
    df['Recovered_to_Infected_Ratio_Strain_2'] = df['Recovered_strain_2'] / df['Infected_strain_2']

    # Replace any infinite values with NaN
    df.replace([float('inf'), -float('inf')], pd.NA, inplace=True)

    # Plot for Strain 1
    plt.figure(figsize=(8, 5))
    plt.plot(df['Recovered_to_Infected_Ratio_Strain_1'], label='Recovered to Infected Ratio (Strain 1)',
             color='blue', linewidth=2, linestyle='-', markersize=4)
    plt.xlabel('Time Steps')
    #plt.xlim(0, 340)
    plt.ylabel('Recovered to Infected Ratio')
    plt.grid(False)
    plt.legend()
    strain_1_plot_path = f"results/R_vs_I_strain_1_alpha_{alpha}.png"
    plt.savefig(strain_1_plot_path, bbox_inches='tight', dpi=dpi)
    plt.close()

    # Plot for Strain 2
    plt.figure(figsize=(8, 5))
    average_ratio_strain_2 = df['Recovered_to_Infected_Ratio_Strain_2'][150:300].mean()
    plt.axhline(y=average_ratio_strain_2, color='r', linestyle='-', label='Average Ratio (Strain 2)', linewidth=2)
    plt.plot(df['Recovered_to_Infected_Ratio_Strain_2'], label='Recovered to Infected Ratio (Strain 2)',
             color='green', linewidth=2, linestyle='-', markersize=4)
    plt.xlabel('Time Steps')
    #plt.xlim(0, 340)
    plt.ylim(0, 1)
    plt.ylabel('Recovered to Infected Ratio')
    plt.grid(False)
    plt.legend()
    plt.text(0.0, average_ratio_strain_2 + 0.02, f' {average_ratio_strain_2:.2f}', color='black')
    strain_2_plot_path = f"results/R_vs_I_strain_2_alpha_{alpha}.png"
    plt.savefig(strain_2_plot_path, bbox_inches='tight', dpi=dpi)
    plt.close()

    return strain_1_plot_path, strain_2_plot_path

