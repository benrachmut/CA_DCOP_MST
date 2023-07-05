from enum import Enum


class Algorithm(Enum):
    DSA_ASY = 1
    DSA_SY = 1

algorithm = Algorithm.DSA_ASY
agents_sizes = [10,20,30]
targets_sizes = [10,20,30]
obstacle_densities =[0]
map_sizes = [(30,30)]
sensing_ranges = [10]
moving_ranges = [10]


cred_constants = [30]
req_constants = [100]
moving_speeds = [(10,20)]

max_nclo = 1000
reps = 100