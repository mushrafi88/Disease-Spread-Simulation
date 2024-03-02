from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from model.agent import Person
import random
import os
import multiprocessing
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd

class Disease_Model(Model):
    def __init__(self,
                 N,
                 width,
                 height,
                 initial_infection,
                 initial_immunity,
                 transmissibility_strain_1,
                 transmissibility_strain_2,
                 level_of_movement,
                 mean_disease_duration_strain_1,
                 mean_disease_duration_strain_2,
                 infection_radius, #vaccine_coverage removed
                 incubation_period_strain_1,
                 incubation_period_strain_2,
                 vaccine_effectiveness_strain_1,
                 vaccine_effectiveness_strain_2,
                 natural_immunity_effectiveness_strain_1,
                 natural_immunity_effectiveness_strain_2,
                 eta_min,
                 eta_max,
                 alpha,
                 vaccine_start_epoch,
                 mean_vaccine_immunity_duration_strain_1,
                 mean_vaccine_immunity_duration_strain_2,
                 mean_natural_immunity_duration_strain_1,
                 mean_natural_immunity_duration_strain_2,
                 vaccine_mean_disease_cutoff_time_strain_1,
                 vaccine_mean_disease_cutoff_time_strain_2,
                 natural_mean_disease_cutoff_time_strain_1,
                 natural_mean_disease_cutoff_time_strain_2,
                 mutation_rate,
                 mutation_threshold,
                 vaccine_delay,
                 std_spread,
                 large_jump_probability,
                 agent_jump_radius_l,
                 agent_jump_radius_h,
                 min_vaccine_coverage,  #new
                 max_vaccine_coverage,
                 eta_update,
                 local_eta_update,
                 nash_table,
                 nash_table_epoch,
                 neighborhood_radius_l,
                 neighborhood_radius_h
                 ):     #new
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
          #changed
        self.current_step = 0
        self.prev_vaccination_rate = 0
        self.vaccine_start_epoch = vaccine_start_epoch
        self.mutation_rate = mutation_rate
        self.mutation_threshold = mutation_threshold
        self.eta_max = eta_max
        self.eta_min = eta_min
        self.alpha = alpha
        self.eta_update = eta_update
        self.local_eta_update = local_eta_update
        self.nash_table = nash_table
        self.nash_table_epoch = nash_table_epoch
        self.min_vaccine_coverage = min_vaccine_coverage
        self.max_vaccine_coverage = max_vaccine_coverage
        self.min_vaccination_num = int(self.min_vaccine_coverage*self.num_agents)
        self.max_vaccination_num = int(self.max_vaccine_coverage*self.num_agents)
        self.neighborhood_radius_l = neighborhood_radius_l 
        self.neighborhood_radius_h = neighborhood_radius_h 
        for i in range(self.num_agents):
            a = Person(i,
                       self,
                       transmissibility_strain_1,
                       transmissibility_strain_2,
                       level_of_movement,
                       infection_radius,
                       incubation_period_strain_1,
                       incubation_period_strain_2,
                       eta_min,
                       eta_max,
                       vaccine_delay,
                       mutation_rate,
                       mean_disease_duration_strain_1,
                       mean_disease_duration_strain_2,
                       vaccine_effectiveness_strain_1,
                       vaccine_effectiveness_strain_2,
                       natural_immunity_effectiveness_strain_1,
                       natural_immunity_effectiveness_strain_2,
                       mean_vaccine_immunity_duration_strain_1,
                       mean_vaccine_immunity_duration_strain_2,
                       mean_natural_immunity_duration_strain_1,
                       mean_natural_immunity_duration_strain_2,
                       vaccine_mean_disease_cutoff_time_strain_1,
                       vaccine_mean_disease_cutoff_time_strain_2,
                       natural_mean_disease_cutoff_time_strain_1,
                       natural_mean_disease_cutoff_time_strain_2,
                       std_spread,
                       large_jump_probability,
                       agent_jump_radius_l,
                       agent_jump_radius_h)
            self.schedule.add(a)

            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        # Infect about 10% of the population
        agents_to_immune = random.sample(self.schedule.agents, int(initial_immunity * self.num_agents))
        agents_to_infect = random.sample(self.schedule.agents, int(initial_infection * self.num_agents))

        #disease_duration_params
        std_dev_disease_strain_1 = int(mean_disease_duration_strain_1*0.15)
        alpha_1_disease = (mean_disease_duration_strain_1/std_dev_disease_strain_1) ** 2
        beta_1_disease = mean_disease_duration_strain_1/(std_dev_disease_strain_1**2)

        #immunity duration
        std_dev_immunity_strain_1 = int(mean_natural_immunity_duration_strain_1*0.35)
        alpha_1_immunity = (mean_natural_immunity_duration_strain_1/std_dev_immunity_strain_1) ** 2
        beta_1_immunity = mean_natural_immunity_duration_strain_1/(std_dev_immunity_strain_1**2)

        for a in agents_to_immune:
            a.natural_immune_strain_1 = True
            a.natural_immunity_duration_strain_1 = int(round(random.gammavariate(alpha_1_immunity, 1/beta_1_immunity),0))

        for a in agents_to_infect:
            a.infected_strain_1 = True
            a.natural_immune_strain_1 = False
            a.disease_duration_strain_1 = int(round(random.gammavariate(alpha_1_disease, 1/beta_1_disease),0))

        self.datacollector = DataCollector({
        "Infected_strain_1": self.count_infected_strain_1,
        "Infected_strain_2": self.count_infected_strain_2,
        "Susceptible": self.count_susceptible,
        "Vaccinated": self.count_vaccinated,
        "Recovered_strain_1": self.count_recovered_strain_1,
        "Recovered_strain_2": self.count_recovered_strain_2,
    })

    def count_recovered_strain_1(self):
        return sum([1 for a in self.schedule.agents if a.recovered_strain_1])

    def count_recovered_strain_2(self):
        return sum([1 for a in self.schedule.agents if a.recovered_strain_2])

    def vaccinate(self):
        non_vaccinated_agents = [a for a in self.schedule.agents if not a.vaccinated]
        num_non_vaccinated = len(non_vaccinated_agents)
        num_to_vaccinate = int(random.uniform(self.min_vaccination_num,self.max_vaccination_num))
        if num_to_vaccinate > num_non_vaccinated:
          num_to_vaccinate = num_non_vaccinated

        # make sure that the sample size does not exceed the non vaccinayed agents
        agents_to_attempt_vaccination = random.sample(non_vaccinated_agents, k=num_to_vaccinate)
        #if (self.count_vaccinated() / self.num_agents) < 0.75:
        for a in agents_to_attempt_vaccination:
            a.vaccinate()

    def count_infected_strain_1(self):
        return sum([1 for a in self.schedule.agents if a.infected_strain_1])

    def count_infected_strain_2(self):
        return sum([1 for a in self.schedule.agents if a.infected_strain_2])

    def count_susceptible(self):
        return sum([1 for a in self.schedule.agents if not a.infected_strain_1 and not a.infected_strain_2 and not a.vaccinated])

    def count_vaccinated(self):
        return sum([1 for a in self.schedule.agents if a.vaccinated])

    def count_infected(self):
        return sum([1 for a in self.schedule.agents if a.infected_strain_1 or a.infected_strain_2])

    def get_neighbors_within_radius(self, agent, radius):
      neighbors = self.grid.get_neighbors(agent.pos, moore=True, include_center=False, radius=radius)
      return neighbors

    def calculate_agent_statistics(self, agent):
        # Get the neighbors within a random radius between 2 and 9
        neighbors = self.get_neighbors_within_radius(agent, random.randint(1,5))
        total_neighbors = len(neighbors)

        # Count the neighbors based on their vaccination and infection status
        vaccinated_immune_neighbors = sum([1 for n in neighbors if n.vaccinated and (n.vaccine_immune_strain_1 or n.vaccine_immune_strain_2)])
        vaccinated_infected_neighbors = sum([1 for n in neighbors if n.vaccinated and (n.infected_strain_1 or n.infected_strain_2)])
        non_vaccinated_immune_neighbors = sum([1 for n in neighbors if not n.vaccinated and not (n.infected_strain_1 or n.infected_strain_2)])
        non_vaccinated_infected_neighbors = sum([1 for n in neighbors if not n.vaccinated and (n.infected_strain_1 or n.infected_strain_2)])

        # Calculate the fractions
        VIM = vaccinated_immune_neighbors / total_neighbors if total_neighbors else 0
        VI = vaccinated_infected_neighbors / total_neighbors if total_neighbors else 0
        NVIM = non_vaccinated_immune_neighbors / total_neighbors if total_neighbors else 0
        NVI = non_vaccinated_infected_neighbors / total_neighbors if total_neighbors else 0
        #Norm = (VIM+VI+NVIM+NVI)
        
        return {
            'AgentID': agent.unique_id,
            'total_neighbors': total_neighbors,
            'VIM': VIM,
            'VI': VI,
            'NVIM': NVIM,
            'NVI': NVI
        }

    def calculate_neighborhood_statistics_parallel(self):
        print("Starting neighborhood statistics calculation...")
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            stats_list = pool.map(self.calculate_agent_statistics, tqdm(self.schedule.agents, desc="Calculating Statistics"))
        # Convert the list of dictionaries to a Pandas DataFrame
        stats_df = pd.DataFrame(stats_list)
        # Now write the DataFrame to a CSV file
        if not os.path.exists('results/nash_table_data'):
            os.makedirs('results/nash_table_data')
        stats_df.to_csv(f'results/nash_table_data/neighborhood_stats_mutation_{self.mutation_rate}_alpha_{self.alpha}_epoch_{self.nash_table_epoch}.csv', index=False)

    def step(self):
        self.current_step += 1
        if self.current_step >= self.vaccine_start_epoch:
            if self.eta_update:
                if self.local_eta_update:
                    for agent in self.schedule.agents:
                       neighbors = self.get_neighbors_within_radius(agent, random.randint(self.neighborhood_radius_l,self.neighborhood_radius_h))
                       vaccinated_neighbors = sum([1 for n in neighbors if n.vaccinated])
                       infected_neighbors = sum([1 for n in neighbors if n.infected_strain_1 or n.infected_strain_2])
                       total_neighbors = len(neighbors)
                       local_vaccination_rate = vaccinated_neighbors / total_neighbors if total_neighbors > 0 else 0
                       local_infection_rate = infected_neighbors / total_neighbors if total_neighbors > 0 else 0

                       k = self.alpha * local_vaccination_rate + (1 - self.alpha) * local_infection_rate
                       agent.eta = min(self.eta_max, max(k, self.eta_min))
                    self.vaccinate()
                else:
                    global_vaccination_rate = self.count_vaccinated() / self.num_agents
                    global_infection_rate = self.count_infected() / self.num_agents
                    for agent in self.schedule.agents:
                       k = self.alpha * global_vaccination_rate + (1 - self.alpha) * global_infection_rate
                       agent.eta = min(self.eta_max, max(k, self.eta_min))
                    self.vaccinate()
            else:
                self.vaccinate()
            #self.vaccine_coverage * (1 - self.vaccine_coverage / self.max_vaccine_coverage)
        if self.nash_table and self.current_step == self.nash_table_epoch:
            self.calculate_neighborhood_statistics_parallel()
        self.datacollector.collect(self)
        self.schedule.step()
