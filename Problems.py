import random
import numpy as np

from Algorithms import DSA_ASY, DSA_SY
from Globals import *


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = f'{x}_{y}'
        self.node_neighbors = []

class Target:
    def __init__(self,i, req, node, current_coverage = 0):
        self.req = req
        self.node = node
        self.current_coverage = current_coverage
        self.name = f'target_{i}'


class DCOP_MST:
    def __init__(self, dcop_mst_id , algorithm, agent_size, target_size, density, size, sensing_range, moving_range,
                 cred_constant, req_constant, moving_speed):
        self.id_ = dcop_mst_id
        self.algorithm = algorithm
        self.agent_size = agent_size
        self.target_size = target_size
        self.density = density
        self.size = size
        self.sensing_range = sensing_range
        self.moving_range = moving_range
        self.cred_constant = cred_constant
        self.req_constant = req_constant
        self.moving_speed = moving_speed


        self.seed = (self.id_+1)*100 + self.agent_size * 10+self.target_size*1000+ self.density*10000
        np.random.seed(self.seed)
        self.rand = random.Random( self.seed)

        self.map_obstacle = None
        self.nodes_list = []
        self.nodes_dict = {}
        self.create_map()
        self.agents = []
        self.targets = []
        self.create_entities()



    def create_map(self):

        x = self.size[0]
        y = self.size[1]

        probabilities = [1-self.density, self.density]
        self.map_obstacle = np.random.choice([0, 1], size=(x, y), p=probabilities)
        # create nodes
        self.create_nodes(x,y)
        self.create_node_neighbors()


    def create_entities(self):
        selected_nodes = self.rand.sample(self.nodes_list, self.agent_size+self.target_size)
        self.create_agents(selected_nodes)
        self.create_targets(selected_nodes)




    def dcop_mst_meet_mailer(self):
        pass
        #TODO ben



                   # Code to create the agents based on self.agent_size, self.map, self.sensing_range, and self.moving_range
    # Return the created agents



    def create_nodes(self, x, y):
        for i_x in range(x):
            for i_y in range(y):
                if not self.map_obstacle[i_x, i_y]:
                    new_node = Node(x, y)
                    self.nodes_list.append(new_node)
                    self.nodes_dict[new_node.name] = new_node

    def create_node_neighbors(self):
        # add neighbours
        for node in self.nodes_list:
            keys_to_check = [
                f'{node.x}_{node.y + 1}',
                f'{node.x}_{node.y - 1}',
                f'{node.x - 1}_{node.y}',
                f'{node.x + 1}_{node.y}'
            ]
            for key in keys_to_check:
                if key in self.nodes_dict:
                    node.node_neighbors(self.nodes_dict[key])

    def create_agents(self, selected_nodes):
        for i in range(self.agent_size):
            selected_node = selected_nodes.pop()
            if self.algorithm == Algorithm.DSA_ASY:
                self.agents.append(DSA_ASY( i, selected_node))
            if self.algorithm == Algorithm.DSA_SY:
                self.agents.append(DSA_SY(i, selected_node))

    def create_targets(self, selected_nodes):

        for i in range(self.target_size):
            selected_node = selected_nodes.pop()
            new_target = Target(i = i, req = self.req_constant,node = selected_node)
            self.targets.append(new_target)


# Code to create the targets based on self.target_size and self.map
# Return the created targets

    # Example usage:
