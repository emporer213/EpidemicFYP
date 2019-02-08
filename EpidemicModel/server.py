# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from EpidemicModel.model import MoneyModel


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal


chat = ChartModule([{"Label": "Gini",
                     "Color": "Black"}],
                   data_collector_name='datacollector')
n_slider = UserSettableParameter('slider', "Number of Agents", 100, 2, 200, 1)
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(MoneyModel,
                       [grid, chat],
                       "Money Model",
                       {"N": n_slider, "width": 10, "height": 10})
