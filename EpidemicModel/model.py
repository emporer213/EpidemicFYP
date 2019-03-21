# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
import random
import pandas as pd
from EpidemicModel.DiseaseModel import *
from EpidemicModel.EpiAgent import EpiAgent
from EpidemicModel.Transport import *


def compute_infections(model):
    human_agents = [agent for agent in model.schedule.agents if agent.type == 0]
    agents_infected = [agent.health_state for agent in human_agents if agent.health_state ==
                       model.disease_model.health_state_dictionary.get("Infected")[1]]
    return len(agents_infected)


def compute_healthy(model):
    human_agents = [agent for agent in model.schedule.agents if agent.type == 0]
    agents_healthy = [agent.health_state for agent in human_agents if (agent.health_state ==
                      model.disease_model.health_state_dictionary.get("Recovered")[1]) or
                      (agent.health_state == model.disease_model.health_state_dictionary.get("Susceptible")[1])]
    return len(agents_healthy)


class Area:

    def __init__(self, location, percentage, location_radius):
        self.location = location
        self.percentage = percentage
        self.location_radius = location_radius
        self.agents = []


class SimModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height, train_line_num=5, stn_limit_rng=(5, 12), wrk_location_num=20):
        self.work_loc_num = wrk_location_num
        self.home_loc_num = round(N / 2)
        self.work_locations = []
        self.home_locations = []
        self.running = True
        self.num_agents = N
        self.space = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.disease_model = SEIRModel(infection_radius=10)
        self.steps = 0
        self.train_lines = []
        self.train_list = []
        self.num_train_lines = train_line_num
        self.area_list = [Area((250, 250), 20, 50),
                          Area((50, 50), 30, 75),
                          Area((300, 50), 15, 25),
                          Area((400, 400), 15, 25),
                          Area((500, 600), 20, 50)]

        self.agent_ids = 1

        for l in range(0, self.work_loc_num):
            self.work_locations.append((random.randrange(self.space.width), random.randrange(self.space.height)))

        for lh in range(0, self.home_loc_num):
            self.home_locations.append((random.randrange(self.space.width), random.randrange(self.space.height)))

        self.generate_transport_net(stn_limit_rng)

        pop_gen(N, self)

        '''
        # Create Agents
        for i in range(self.num_agents):
            a = EpiAgent(i, self)
            self.schedule.add(a)
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
        '''

        self.datacollector = DataCollector(
            model_reporters={"Rate of Infection": compute_infections, "Decline of Health": compute_healthy},
            agent_reporters={"Infected": "health_state", "Movement": "pos"}  # An agent attribute
        )

    def generate_transport_net(self, stn_limit):
        for al in self.area_list:
            station_list = [Station(al.location)]
            index = 0
            for s in range(0, random.randrange(stn_limit[0], stn_limit[1])):
                new_station_pos = self.calculate_move(station_list[index].pos, self.space.center, 30)
                new_station = Station(new_station_pos)
                new_station.prev_station = station_list[index]
                station_list[index].next_station = new_station
                station_list.append(new_station)
                index += 1
            self.train_lines.append(TrainLine(station_list))

            for st in station_list:
                if random.choice((True, False)):
                    self.agent_ids += 1
                    tr = Train(None, st, self, 8, self.agent_ids)
                    self.space.place_agent(tr, st.pos)
                    self.train_list .append(tr)
                    st.train_list.append(tr)

    def calculate_move(self, current_pos, dest_pos, speed):
        velocity = self.space.get_heading(current_pos, dest_pos)
        velocity /= np.linalg.norm(velocity)
        new_position = current_pos + velocity * speed
        return new_position

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1

    def save_data(dataframe, file_name):
        writer = pd.ExcelWriter(file_name + '.xlsx')
        dataframe.to_excel(writer, 'DataFrame')
        writer.save()


def pop_gen(pop_size, model):
    for al in model.area_list:
        pop_range = round((pop_size/100) * al.percentage)
        for i in range(pop_range):
            velocity = np.random.random(2) * 2 - 1
            a = EpiAgent(model.agent_ids, model, velocity, 2)
            model.schedule.add(a)
            x = random.randrange(al.location[0] - al.location_radius, al.location[0] + al.location_radius)
            y = random.randrange(al.location[1] - al.location_radius, al.location[1] + al.location_radius)
            while (x - al.location[0]) ** 2 + (y - al.location[1]) ** 2 > al.location_radius ** 2:
                x = random.randrange(al.location[0] - al.location_radius, al.location[0] + al.location_radius)
                y = random.randrange(al.location[1] - al.location_radius, al.location[1] + al.location_radius)
            model.space.place_agent(a, (x, y))

            a.home = random.choice(model.home_locations)
            a.work = random.choice(model.work_locations)
            a.current_final_dest = a.work

            al.agents.append(a)
            model.agent_ids += 1

    patient_zero = random.choice(model.schedule.agents)
    patient_zero.health_state = model.disease_model.health_state_dictionary.get("Infected")[1]
