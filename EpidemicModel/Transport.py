import numpy as np
from mesa import Agent


class TrainLine:

    def __init__(self, station_list, station_limit = 7):
        self.station_list = station_list
        self.station_limit = station_limit


class Train(Agent):

    def __init__(self, passengers, current_station, pos, model, speed, unique_id):
        super().__init__(unique_id, model)
        self.passengers = passengers
        self.current_station = current_station
        self.direction = 1

        if self.direction == 1:
            if current_station.next_station is not None:
                self.next_station = current_station.next_station
            else:
                self.next_station = current_station.prev_station
                self.direction = 0
        else:
            if current_station.prev_station is not None:
                self.next_station = current_station.prev_station
            else:
                self.next_station = current_station.next_station
                self.direction = 1

        self.type = 1
        self.pos = pos
        self.velocity = None
        self.heading = None
        self.speed = speed
        self.model = model
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
            self.next_station = self.current_station.next_station
            self.wait_timer = 1

        if self.wait_timer != 0:
            self.wait_timer -= 1
        else:
            self.move()


class Station(Agent):

    def __init__(self, pos, unique_id, model):
        super().__init__(unique_id, model)
        self.train_list = []
        self.pos = pos
        self.next_station = None
        self.prev_station = None
        self.type = 2
