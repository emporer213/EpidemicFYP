from mesa.visualization.ModularVisualization import VisualizationElement


class SimpleCanvas(VisualizationElement):
    local_includes = ["simple_continuous_canvas.js"]
    agent_portrayal_method = None
    trainPortrayal_method = None
    stationPortrayal_method = None
    canvas_height = 500
    canvas_width = 500

    def __init__(self, agent_portrayal_method, train_portrayal_method, station_portrayal_method, canvas_height=500,
                 canvas_width=500):
        '''
        Instantiate a new SimpleCanvas
        '''
        self.agent_portrayal_method = agent_portrayal_method
        self.trainPortrayal_method = train_portrayal_method
        self.stationPortrayal_method = station_portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = ("new Simple_Continuous_Module({}, {})".
                       format(self.canvas_width, self.canvas_height))
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        for agent in model.schedule.agents:
            portrayal = self.agent_portrayal_method(agent)
            x, y = self.calc_portrayal_xy(agent.pos, model)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)

        for trainLine in model.train_lines:
            for station in trainLine.station_list:
                for train in station.train_list:
                    train_portrayal = self.trainPortrayal_method(train)
                    x, y = self.calc_portrayal_xy(train.pos, model)
                    train_portrayal["x"] = x
                    train_portrayal["y"] = y
                    space_state.append(train_portrayal)
                station_portrayal = self.stationPortrayal_method
                x, y = self.calc_portrayal_xy(station.pos, model)
                station_portrayal["x"] = x
                station_portrayal["y"] = y
                space_state.append(station_portrayal)

        return space_state

    def calc_portrayal_xy(self, pos, model):
        x, y = pos
        x = ((x - model.space.x_min) /
             (model.space.x_max - model.space.x_min))
        y = ((y - model.space.y_min) /
             (model.space.y_max - model.space.y_min))
        return x, y
