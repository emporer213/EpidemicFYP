# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from EpidemicModel.SimpleContinuousModule import SimpleCanvas
from EpidemicModel.model import SimModel
from EpidemicModel.ButtonModule import ButtonModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Color": "grey",
                 "LineColor": "grey"}
    if agent.type == 0:
        if agent.health_state == agent.model.disease_model.health_state_dictionary.get("Infected")[1]:
            portrayal["Color"] = "red"
            portrayal["LineColor"] = "red"
            portrayal["Layer"] = 0
            portrayal["r"] = 2
        elif agent.health_state == agent.model.disease_model.health_state_dictionary.get("Recovered")[1]:
            portrayal["Color"] = "green"
            portrayal["LineColor"] = "green"
            portrayal["Layer"] = 1
            portrayal["r"] = 3
        elif agent.health_state == agent.model.disease_model.health_state_dictionary.get("Exposed")[1]:
            portrayal["Color"] = "yellow"
            portrayal["LineColor"] = "yellow"
            portrayal["Layer"] = 2
            portrayal["r"] = 2.5
        else:
            portrayal["r"] = 3

        if agent.is_at_work():
            portrayal["LineColor"] = "orange"
        elif agent.is_at_home():
            portrayal["LineColor"] = "blue"
        return portrayal

    return portrayal


def station_portrayal(station):
    portrayal = {
        "Shape": "circle",
        "Filled": "True",
        "Color": "MidnightBlue",
        "Layer": 2,
        "LineColor": "MidnightBlue",
        "r": 5
    }
    return portrayal


def train_portrayal(train):
    portrayal = {
        "Shape": "rect",
        "Color": "PaleTurquoise",
        "LineColor": "PaleTurquoise",
        "Layer": 3,
        "w": 0.025,
        "h": 0.01
    }
    return portrayal


infected_chart = ChartModule([{"Label": "Rate of Infection",
                               "Color": "Red"}, {"Label": "Decline of Health", "Color": "Green"}],
                             data_collector_name='datacollector')
n_slider = UserSettableParameter('slider', "Number of Agents", 2000, 2, 10000, 1)
space = SimpleCanvas(agent_portrayal, train_portrayal, station_portrayal, canvas_height=1000, canvas_width=1000)
save_button = ButtonModule()
server = ModularServer(SimModel,
                       [space, infected_chart, save_button],
                       "Sim Model",
                       {"N": 1000, "width": 1000, "height": 1000})
