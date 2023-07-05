import random

from Algorithms import DSA_ASY, DSA_SY
from Globals import *


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

        self.map = self.create_map()
        self.agents = self.create_agents()
        self.targets = self.create_targets()
        seed = (self.id_+1)*100 + self.agent_size * 10+self.target_size*1000+ self.density*10000
        self.rand = random.Random(seed)
    def create_map(self):
        x = self.size[0]
        y = self.size[1]
        # todo Arseni
        pass


    def create_agents(self):
        ans = []
        for i in range(self.agent_size):
            node = self.rand.choice(self.map)
            if self.algorithm == Algorithm.DSA_ASY:
               ans.append(DSA_ASY(node))
            if self.algorithm == Algorithm.DSA_SY:
               ans.append(DSA_SY(node))

    def dcop_mst_meet_mailer(self):
        pass
        #TODO ben



                   # Code to create the agents based on self.agent_size, self.map, self.sensing_range, and self.moving_range
    # Return the created agents

    def create_targets(self):
        pass
# Code to create the targets based on self.target_size and self.map
# Return the created targets

    # Example usage:
