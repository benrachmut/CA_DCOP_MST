import abc
import threading
from abc import ABC
from Entities import *
from general_communication_protocols import *





if __name__ == '__main__':
    
    a1 = AgentSimulation("1",Location(0,0),domain=["a","b"])
    a2 = AgentSimulation("2",Location(10,10),domain=["a","b"])
    a3 = AgentSimulation("3",Location(5,5),domain=["a","b"])

    a1.neighbours_ids_list=["2","3"]
    a2.neighbours_ids_list=["1","3"]
    a3.neighbours_ids_list=["2","3"]

    algo_agents = [AgentArseni(a1,value="a"), AgentArseni(a2,value="b"), AgentArseni(a3,value="a")]




    protocol  = get_communication_protocols(constants_delay_uniform = [1000])
    pass


