import numpy as np
from mesa import Agent


class TrainLine:

    def __init__(self, station_list):
        self.station_list = station_list


class Train(Agent):

    def __init__(self, passengers, current_station, next_station, pos, model, speed, unique_id, line, current_index):
        super().__init__(unique_id, model)
        self.passengers = passengers
        self.current_station_index = current_index
        self.current_station = current_station
        self.next_station = next_station
        self.pos = pos
        self.velocity = None
        self.heading = None
        self.speed = speed
        self.model = model
        self.train_line = line
        self.wait_timer = 1

    def calculate_heading(self):
        self.heading = self.model.space.get_heading(self.pos, self.next_station.pos)

    def move(self):
        self.calculate_heading()
        self.velocity = self.heading
        self.velocity /= np.linalg.norm(self.velocity)
        new_position = self.pos + self.velocity * self.speed
        self.model.space.move_agent(self, new_position)

    def step(self):
        if self.pos == self.next_station.pos:
            self.current_station = self.next_station
            self.current_station_index += 1
            self.next_station = self.train_line.station_list[self.current_station_index]
            self.wait_timer = 1

        if self.wait_timer != 0:
            self.wait_timer -= 1
        else:
            self.move()


class Station:

    def __init__(self, pos):
        self.train_list = None
        self.pos = pos
