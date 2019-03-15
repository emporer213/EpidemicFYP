from mesa import Agent
import random
import numpy as np
import traceback


class EpiAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, velocity, speed):
        super().__init__(unique_id, model)
        self.health_state = 1
        self.infected_step = self.model.steps
        self.velocity = velocity
        self.speed = speed

    def move(self):
        """new_position_x = self.pos[0] + random.randrange(-8, 8)
        new_position_y = self.pos[1] + random.randrange(-8, 8)"""
        other_agent = random.choice(self.model.schedule.agents)
        self.velocity = self.model.space.get_heading(self.pos, other_agent.pos )
        self.velocity /= np.linalg.norm(self.velocity)
        new_position = self.pos + self.velocity * self.speed
        try:
            self.model.space.move_agent(self, new_position)
        except:
            print(self.unique_id, " ", self.velocity, " ")
            traceback.print_exc()

    def step(self):
        self.move()
        if self.health_state == self.model.disease_model.health_state_dictionary.get("Infected")[1]:
            self.model.disease_model.infect(self)
            infection_duration = self.model.disease_model.health_state_dictionary.get("Infected")[0]
            if (self.model.steps - self.infected_step) > infection_duration:
                self.health_state = self.model.disease_model.health_state_dictionary.get("Recovered")[1]

        elif self.health_state == self.model.disease_model.health_state_dictionary.get("Exposed")[1]:
                exposed_duration = self.model.disease_model.health_state_dictionary.get("Exposed")[0]
                if (self.model.steps - self.exposed_step) > exposed_duration:
                    self.health_state = self.model.disease_model.health_state_dictionary.get("Infected")[1]
                    self.infected_step = self.model.steps


class Area:

    def __init__(self, location, percentage, location_radius):
        self.location = location
        self.percentage = percentage
        self.location_radius = location_radius
        self.agents = []


def pop_gen(pop_size, model):
    agent_id = 1
    area_list = [Area((250, 250), 20, 50),
                 Area((50, 50), 30, 75),
                 Area((300, 50), 15, 25),
                 Area((400, 400), 15, 25),
                 Area((500, 600), 20, 50)]
    for al in area_list:
        pop_range = round((pop_size/100) * al.percentage)
        for i in range(pop_range):
            velocity = np.random.random(2) * 2 - 1
            a = EpiAgent(agent_id, model, velocity, 2)
            model.schedule.add(a)
            x = random.randrange(al.location[0] - al.location_radius, al.location[0] + al.location_radius)
            y = random.randrange(al.location[1] - al.location_radius, al.location[1] + al.location_radius)
            model.space.place_agent(a, (x, y))
            al.agents.append(a)
            agent_id += 1

    patient_zero = random.choice(model.schedule.agents)
    patient_zero.health_state = model.disease_model.health_state_dictionary.get("Infected")[1]



