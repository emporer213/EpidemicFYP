class Train:

    def __init__(self, passengers, current_station, next_station, pos, model):
        self.passengers = passengers
        self.current_station = current_station
        self.next_station = next_station
        self.pos = pos
        self.heading = None
        self.model = model

    def calculate_heading(self):
        self.heading = self.model.space.get_heading(self.pos, self.next_station.pos)




