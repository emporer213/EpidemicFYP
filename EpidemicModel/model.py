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
        self.work_loc_num = round(N / 3)
        self.home_loc_num = round(N / 2)
        self.work_locations = []
        self.home_locations = []
        self.running = True
        self.num_agents = N
        self.space = ContinuousSpace(width, height, False)
        self.schedule = RandomActivation(self)
        self.disease_model = SEIRModel(infection_radius=2.018)
        self.steps = 0
        self.train_lines = []
        self.train_list = []
        self.num_train_lines = train_line_num
        self.area_list = [Area((2000, 2050), 0.1, 100),     # City of London
                          Area((3000, 1800), 3.8, 300),       # Barking and Dagenham
                          Area((1800, 800), 7.2, 500),        # Barnet
                          Area((3500, 2500), 4.7, 400),       # Bexley
                          Area((1200, 1300), 6.3, 300),       # Brent
                          Area((2800, 3200), 6.3, 600),       # Bromley
                          Area((1900, 1800), 4.5, 200),       # Camden
                          Area((2000, 3200), 7.4, 500),       # Croydon
                          Area((800, 2000), 6.8, 400),        # Ealing
                          Area((2000, 500), 6.3, 500),        # Enfield
                          Area((2800, 2200), 5.1, 400),       # Greenwich
                          Area((2100, 1900), 5.0, 200),         # Hackney
                          Area((1500, 2100), 3.7, 200),       # Hammersmith and Fullham
                          Area((2000, 1000), 5.2, 300),       # Haringey
                          Area((800, 1000), 4.8, 400),        # Harrow
                          Area((3400, 1500), 4.8, 600),       # Havering
                          Area((600, 2000), 5.5, 600),        # Hillingdon
                          Area((700, 2200), 5.1, 400),        # Hounslow
                          Area((1950, 1900), 4.2, 200),       # Islington
                          Area((1800, 2050), 3.2, 190)]      # Kensington
                          #Area((1000, 1000), 5, 100),
                          #Area((1000, 1000), 5, 100)]

        self.agent_ids = 1

        for l in range(0, self.work_loc_num):
            self.work_locations.append((random.randrange(self.space.width - 10), random.randrange(self.space.height - 10)))

        for lh in range(0, self.home_loc_num):
            self.home_locations.append((random.randrange(self.space.width - 10), random.randrange(self.space.height - 10)))

        self.generate_transport_net(stn_limit_rng)

        pop_gen(N, self)

        self.datacollector = DataCollector(
            model_reporters={"Number of Infected": compute_infections, "Number of Healthy": compute_healthy},
            agent_reporters={}  # An agent attribute
        )
        self.agent_datacollector = DataCollector(
            model_reporters={},
            agent_reporters={"Infected State": "state_when_infected"}
        )

    def generate_transport_net(self, stn_limit):
        central_line = TrainLine([])
        central_station = Station(self.space.center, central_line)
        central_line.station_list.append(central_station)
        self.space.place_station(central_station, central_station.pos)
        for al in self.area_list:
            train_line = TrainLine([])
            station_list = [central_station]
            index = 0
            for s in range(0, random.randrange(stn_limit[0], stn_limit[1])):
                new_station_pos = self.calculate_station_move(station_list[index].pos, al.location, 350)
                if self.space.out_of_bounds(new_station_pos):
                    break

                if self.space.get_distance(al.location, new_station_pos) < 10:
                    break

                x, y = new_station_pos
                if x > 3900 or x < 100:
                    break

                if y > 3900 or y < 100:
                    break

                new_station = Station(new_station_pos, line=train_line)
                station_list.append(new_station)
                self.space.place_station(new_station, new_station.pos)
                index += 1
            train_line.station_list = station_list
            self.train_lines.append(train_line)

            try:
                station_list[0].connections.append(Connection(station_list[1], station_list[0], train_line, 1))
            except IndexError:
                continue
            for i in range(1, (len(station_list) - 1)):
                station_list[i].connections.append(Connection(station_list[i-1], station_list[i], train_line, 0))
                station_list[i].connections.append(Connection(station_list[i+1], station_list[i], train_line, 1))
            last_index = len(station_list) - 1
            station_list[last_index].connections.append(Connection(station_list[last_index-1], station_list[last_index],
                                                                   train_line, 0))

            for i in range(1, round(len(station_list)/3)):
                    st = train_line.station_list[i]
                    self.agent_ids += 1
                    tr = Train(st, self, 66, self.agent_ids, train_line)
                    self.space.place_agent(tr, st.pos)
                    self.train_list .append(tr)
                    st.train_list.append(tr)

    def calculate_agent_move(self, current_pos, dest_pos, speed):
        velocity = self.space.get_heading(current_pos, dest_pos)
        velocity /= np.linalg.norm(velocity)
        distance = self.space.get_distance(current_pos, dest_pos)
        if distance < speed:
            speed = speed / distance
        new_position = current_pos + velocity * speed
        if self.space.out_of_bounds(new_position):
            x, y = new_position
            if self.space.out_of_bounds((x, 0)):
                x *= -1
            if self.space.out_of_bounds((0, y)):
                y *= -1
            new_position = x, y
        return new_position

    def calculate_station_move(self, current_pos, dest_pos, speed):
        velocity = self.space.get_heading(current_pos, dest_pos)
        velocity /= np.linalg.norm(velocity)
        new_position = current_pos + velocity * speed
        if self.space.out_of_bounds(new_position):
            x, y = new_position
            if self.space.out_of_bounds((x, 0)):
                x *= -1
            if self.space.out_of_bounds((0, y)):
                y *= -1
            new_position = x, y
        return new_position

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1

    def save_data(self, filename):
        data_collector = self.datacollector
        self.agent_datacollector.collect(self)
        agent_datacollector = self.agent_datacollector
        agent_dataframe = agent_datacollector.get_agent_vars_dataframe()
        model_dataframe = data_collector.get_model_vars_dataframe()
        filename += ".xlsx"
        writer = pd.ExcelWriter(filename)
        agent_dataframe.to_excel(writer, sheet_name='Agent Vars')
        model_dataframe.to_excel(writer, sheet_name='Model Vars')
        writer.save()


def pop_gen(pop_size, model):
    for al in model.area_list:
        pop_range = round((pop_size/100) * al.percentage)
        for i in range(pop_range):
            velocity = np.random.random(2) * 2 - 1
            a = EpiAgent(model.agent_ids, model, velocity, 10)
            model.schedule.add(a)
            x, y = rand_loc(al.location, al.location_radius, model)
            model.space.place_agent(a, (x, y))

            a.home = random.choice(model.home_locations)
            a.work = random.choice(model.work_locations)

            if model.space.get_distance(a.home, a.work) < 200:
                a.use_transport = False

            a.current_final_dest = a.work
            a.get_transport_goals()

            al.agents.append(a)
            model.agent_ids += 1
    for i in range(5):
        patient_zero = random.choice(model.schedule.agents)
        patient_zero.health_state = model.disease_model.health_state_dictionary.get("Infected")[1]


def rand_loc(area_location, area_radius, model):
    x_loc_range = (area_location[0] - area_radius, area_location[0] + area_radius)
    y_loc_range = (area_location[1] - area_radius, area_location[1] + area_radius)

    x = random.randrange(x_loc_range[0], x_loc_range[1])
    y = random.randrange(y_loc_range[0], y_loc_range[1])

    while (x - area_location[0]) ** 2 + (y - area_location[1]) ** 2 > area_radius ** 2:
        x = random.randrange(x_loc_range[0], x_loc_range[1])
        y = random.randrange(y_loc_range[0], y_loc_range[1])
    if model.space.out_of_bounds((x, y)):
        rand_loc(area_location, area_radius, model)

    return x, y
