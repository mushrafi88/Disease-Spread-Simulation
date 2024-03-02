from mesa import Agent
import random
import numpy as np

class Person(Agent):
    def __init__(self,
                 unique_id,
                 model,
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
                 agent_jump_radius_h):
        super().__init__(unique_id, model)
        self.transmissibility_strain_1 = transmissibility_strain_1
        self.transmissibility_strain_2 = transmissibility_strain_2
        self.level_of_movement = level_of_movement
        self.infection_radius = infection_radius
        self.incubation_period_strain_1 = incubation_period_strain_1
        self.incubation_period_strain_2 = incubation_period_strain_2
        self.incubation_countdown_strain_1 = 0
        self.incubation_countdown_strain_2 = 0

        self.eta_min = eta_min
        self.eta = eta_min
        self.eta_max = eta_max

        self.vaccine_effectiveness_strain_1 = vaccine_effectiveness_strain_1
        self.vaccine_effectiveness_strain_2 = vaccine_effectiveness_strain_2
        self.natural_immunity_effectiveness_strain_1 = natural_immunity_effectiveness_strain_1
        self.natural_immunity_effectiveness_strain_2 = natural_immunity_effectiveness_strain_2

        self.vaccine_delay = vaccine_delay
        self.vaccine_countdown = 0
        self.mutation_rate = mutation_rate
        self.std_spread = std_spread
        self.transmission_chain_length = 0

        self.vaccine_immune_strain_1 = False
        self.vaccine_immune_strain_2 = False
        self.natural_immune_strain_1 = False
        self.natural_immune_strain_2 = False
        self.infected_strain_1 = False
        self.infected_strain_2 = False
        self.vaccinated = False
        self.recovered = False
        self.recovered_strain_1 = False
        self.recovered_strain_2 = False
        
        self.large_jump_probability = large_jump_probability 
        self.can_make_large_jump = random.random() < self.large_jump_probability 
        self.agent_jump_radius_l = agent_jump_radius_l 
        self.agent_jump_radius_h = agent_jump_radius_h  
        self.vaccination_count = 0
        self.vaccination_duration = 0

        self.mean_disease_duration_strain_1 = mean_disease_duration_strain_1
        self.mean_disease_duration_strain_2 = mean_disease_duration_strain_2
        self.mean_vaccine_immunity_duration_strain_1 = mean_vaccine_immunity_duration_strain_1
        self.mean_vaccine_immunity_duration_strain_2 = mean_vaccine_immunity_duration_strain_2
        self.mean_natural_immunity_duration_strain_1 = mean_natural_immunity_duration_strain_1
        self.mean_natural_immunity_duration_strain_2 = mean_natural_immunity_duration_strain_2
        self.vaccine_mean_disease_cutoff_time_strain_1 = vaccine_mean_disease_cutoff_time_strain_1
        self.vaccine_mean_disease_cutoff_time_strain_2 = vaccine_mean_disease_cutoff_time_strain_2
        self.natural_mean_disease_cutoff_time_strain_1 = natural_mean_disease_cutoff_time_strain_1
        self.natural_mean_disease_cutoff_time_strain_2 = natural_mean_disease_cutoff_time_strain_2

        # initializations
        self.vaccine_immunity_duration_strain_1 = 0
        self.vaccine_immunity_duration_strain_2 = 0
        self.natural_immunity_duration_strain_1 = 0
        self.natural_immunity_duration_strain_2 = 0
        self.vaccine_immunity_disease_cutoff_time_strain_1 = 0
        self.vaccine_immunity_disease_cutoff_time_strain_2 = 0
        self.natural_immunity_disease_cutoff_time_strain_1 = 0
        self.natural_immunity_disease_cutoff_time_strain_2 = 0

    def init_duration(self, attr_name, mean):
        std_dev = int(mean * self.std_spread)
        alpha = (mean / std_dev) ** 2
        beta = mean / (std_dev ** 2)
        duration = int(round(random.gammavariate(alpha, 1 / beta), 0))
        setattr(self, attr_name, duration)

    def vaccinate(self):
        if random.uniform(0,1) < self.eta:
            if not self.vaccinated:
                self.vaccinated = True
                self.vaccine_countdown = self.vaccine_delay
                self.vaccination_count += 1
                self.vaccination_duration = (self.mean_vaccine_immunity_duration_strain_1 + self.vaccine_delay)

    def move(self):
        if self.can_make_large_jump:
          current_x, current_y = self.pos
          jump_radius = random.uniform(self.agent_jump_radius_l, self.agent_jump_radius_h)  # Radius between 5 and 8
          angle = random.uniform(0, 2 * np.pi)  # Random angle

          # Calculate potential new position
          new_x = int(current_x + jump_radius * np.cos(angle))
          new_y = int(current_y + jump_radius * np.sin(angle))

          # Ensure the new position is within grid boundaries
          new_x = max(0, min(new_x, self.model.grid.width - 1))
          new_y = max(0, min(new_y, self.model.grid.height - 1))
          new_pos = (new_x, new_y)
          self.model.grid.move_agent(self, new_pos)
        else:
            # Existing movement logic for normal movement
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            if possible_steps and random.uniform(0, 1) < self.level_of_movement:
                new_pos = random.choice(possible_steps)
                self.model.grid.move_agent(self, new_pos)

        #self.model.grid.move_agent(self, new_pos)

    def infect(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=self.infection_radius)
        neighbors.append(self.pos)
        if self.incubation_countdown_strain_1 <= 0 or self.incubation_countdown_strain_2 <=0:
            for cell in neighbors:
                cellmates = self.model.grid.get_cell_list_contents([cell])
                for inhabitant in cellmates:
                    if inhabitant.infected_strain_1 or inhabitant.infected_strain_2:
                        continue
                     # Check for infection by second strain if the infecting agent has it
                    if self.infected_strain_2 and not (inhabitant.vaccine_immune_strain_2 or inhabitant.natural_immune_strain_2) and random.uniform(0,1) < self.transmissibility_strain_2:
                        inhabitant.infected_strain_2 = True
                        inhabitant.init_duration('disease_duration_strain_2', self.mean_disease_duration_strain_2)
                        inhabitant.recovered_strain_2 = False  # Increment the transmission chain length
                # Check for infection by first strain only if the infecting agent has it
                    if self.infected_strain_1 and not (inhabitant.vaccine_immune_strain_1 or inhabitant.natural_immune_strain_1) and random.uniform(0,1) < self.transmissibility_strain_1:
                        if self.transmission_chain_length > self.model.mutation_threshold and random.uniform(0,1) < self.mutation_rate:
                            inhabitant.infected_strain_2 = True
                            inhabitant.init_duration('disease_duration_strain_2', self.mean_disease_duration_strain_2)
                            inhabitant.recovered_strain_2 = False
                            inhabitant.transmission_chain_length = 0
                        else:
                            inhabitant.infected_strain_1 = True
                            inhabitant.init_duration('disease_duration_strain_1', self.mean_disease_duration_strain_1)
                            inhabitant.recovered_strain_1 = False
                            inhabitant.transmission_chain_length = self.transmission_chain_length + 1

    def step(self):
        if self.vaccine_countdown > 0:
            self.vaccine_countdown -= 1
            if self.vaccine_countdown <= 0:
                if random.uniform(0,1) < self.vaccine_effectiveness_strain_1:
                    self.vaccine_immune_strain_1 = True
                    self.init_duration('vaccine_immunity_duration_strain_1', self.mean_vaccine_immunity_duration_strain_1)

                if random.uniform(0,1) < self.vaccine_effectiveness_strain_2:
                    self.vaccine_immune_strain_2 = True
                    self.init_duration('vaccine_immunity_duration_strain_2', self.mean_vaccine_immunity_duration_strain_2)

        if self.infected_strain_1:
            self.recovered_strain_1 = False
            self.incubation_countdown_strain_1 -= 1
            if self.incubation_countdown_strain_1 <= 0:
                self.infect()
                if (self.vaccine_immune_strain_1 and self.natural_immune_strain_1) or (self.vaccine_immune_strain_1 and not self.natural_immune_strain_1):
                    self.init_duration('vaccine_immunity_disease_cutoff_time_strain_1', self.vaccine_mean_disease_cutoff_time_strain_1)
                    self.disease_duration_strain_1 -= self.vaccine_immunity_disease_cutoff_time_strain_1
                if (self.natural_immune_strain_1 and not self.vaccine_immune_strain_1):
                    self.init_duration('natural_immunity_disease_cutoff_time_strain_1', self.natural_mean_disease_cutoff_time_strain_1)
                    self.disease_duration_strain_1 -= self.natural_immunity_disease_cutoff_time_strain_1
                if not (self.vaccine_immune_strain_1 or self.natural_immune_strain_1):
                    self.disease_duration_strain_1 -= 1
                if self.disease_duration_strain_1 <= 0:
                    self.infected_strain_1 = False
                    self.recovered_strain_1 = True
                    if not (self.vaccine_immune_strain_1 or self.natural_immune_strain_1) and (random.uniform(0,1) < self.natural_immunity_effectiveness_strain_1):
                        self.natural_immune_strain_1 = True
                        self.init_duration('natural_immunity_duration_strain_1', self.mean_natural_immunity_duration_strain_1)
                    else:
                        self.natural_immune_strain_1 = False
        if self.infected_strain_2:
            self.recovered_strain_2 = False
            self.incubation_countdown_strain_2 -= 1
            if self.incubation_countdown_strain_2 <= 0:
                self.infect()
                if (self.vaccine_immune_strain_2 and self.natural_immune_strain_2) or (self.vaccine_immune_strain_2 and not self.natural_immune_strain_2):
                    self.init_duration('vaccine_immunity_disease_cutoff_time_strain_2', self.vaccine_mean_disease_cutoff_time_strain_2)
                    self.disease_duration_strain_2 -= self.vaccine_immunity_disease_cutoff_time_strain_2
                if (self.natural_immune_strain_2 and not self.vaccine_immune_strain_2):
                    self.init_duration('natural_immunity_disease_cutoff_time_strain_2', self.natural_mean_disease_cutoff_time_strain_2)
                    self.disease_duration_strain_2 -= self.natural_immunity_disease_cutoff_time_strain_2
                if not (self.vaccine_immune_strain_2 or self.natural_immune_strain_2):
                    self.disease_duration_strain_2 -= 1
                if self.disease_duration_strain_2 <= 0:
                    self.infected_strain_2 = False
                    self.recovered_strain_2 = True
                    if not (self.vaccine_immune_strain_2 or self.natural_immune_strain_2) and (random.uniform(0,1) < self.natural_immunity_effectiveness_strain_2):
                        self.natural_immune_strain_2 = True
                        self.init_duration('natural_immunity_duration_strain_2', self.mean_natural_immunity_duration_strain_2)
                    else:
                        self.natural_immune_strain_2 = False

        if self.natural_immune_strain_1 or self.vaccine_immune_strain_1:
            self.natural_immune_strain_1 = False
            self.natural_immunity_duration_strain_1 = 0
        if self.natural_immune_strain_2 or self.vaccine_immune_strain_2:
            self.natural_immune_strain_2 = False
            self.natural_immunity_duration_strain_2 = 0

        if self.natural_immune_strain_1:
            self.natural_immunity_duration_strain_1 -= 1
            if self.natural_immunity_duration_strain_1 <= 0:
                self.natural_immune_strain_1 = False

        if self.natural_immune_strain_2:
            self.natural_immunity_duration_strain_2 -= 1
            if self.natural_immunity_duration_strain_2 <= 0:
                self.natural_immune_strain_2 = False

        if self.vaccine_immune_strain_1:
            self.vaccine_immunity_duration_strain_1 -= 1
            if self.vaccine_immunity_duration_strain_1 <= 0:
                self.vaccine_immune_strain_1 = False

        if self.vaccine_immune_strain_2:
            self.vaccine_immunity_duration_strain_2 -= 1
            if self.vaccine_immunity_duration_strain_2 <= 0:
                self.vaccine_immune_strain_2 = False

        if self.vaccinated:
            self.vaccination_duration -= 1
            if self.vaccination_duration <=0:
                self.vaccinated = False
        self.move()



