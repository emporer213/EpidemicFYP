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
        self.space = ContinuousSpace(width, height, False)
        self.schedule = RandomActivation(self)
        self.disease_model = SEIRModel(infection_radius=10)
        self.steps = 0
        self.train_lines = []
        self.train_list = []
        self.num_train_lines = train_line_num
        self.area_list = [Area((1000, 100), 10, 100),
                          Area((2000, 100), 10, 75),
                          Area((3000, 100), 15, 100),
                          Area((1000, 1000), 20, 200),
                          Area((2000, 2500), 15, 250),
                          Area((3000, 3000), 10, 100),
                          Area((2000, 3000), 15, 100),
                          Area((1000, 3500), 5, 100)]

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
        central_line = TrainLine([])
        central_station = Station(self.space.center, central_line)
        central_line.station_list.append(central_station)
        self.space.place_station(central_station, central_station.pos)
        for al in self.area_list:
            train_line = TrainLine([])
            station_list = [central_station]
            index = 0
            for s in range(0, random.randrange(stn_limit[0], stn_limit[1])):
                new_station_pos = self.calculate_move(station_list[index].pos, al.location, 200)
                if self.space.out_of_bounds(new_station_pos):
                    break

                if self.space.get_distance(al.location, new_station_pos) < 1:
                    break
                new_station = Station(new_station_pos, line=train_line)
                station_list.append(new_station)
                self.space.place_station(new_station, new_station.pos)
                index += 1
            train_line.station_list = station_list
            self.train_lines.append(train_line)

            station_list[0].connections.append(Connection(station_list[1], station_list[0], train_line, 1))
            for i in range(1, (len(station_list) - 1)):
                station_list[i].connections.append(Connection(station_list[i-1], station_list[i], train_line, 0))
                station_list[i].connections.append(Connection(station_list[i+1], station_list[i], train_line, 1))
            last_index = len(station_list) - 1
            station_list[last_index].connections.append(Connection(station_list[last_index-1], station_list[last_index],
                                                                   train_line, 0))

            for st in station_list:
                if random.choice((True, False)):
                    self.agent_ids += 1
                    tr = Train(st, self, 8, self.agent_ids, train_line)
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
            x, y = rand_loc(al.location, al.location_radius, model)
            model.space.place_agent(a, (x, y))

            a.home = random.choice(model.home_locations)
            a.work = random.choice(model.work_locations)
            a.current_final_dest = a.work

            al.agents.append(a)
            model.agent_ids += 1

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
