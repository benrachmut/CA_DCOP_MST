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


# --- communication_protocols ---
cenralized_always_discovers_without_delay = None
is_with_timestamp = False
is_with_perfect_communication = False
constants_loss_distance = [] # e^-(alpha*d)
constants_delay_poisson_distance = [] # Pois(alpha^d) 1000, 10000, 100000
constants_delay_uniform_distance=[] # U(0, alpha^d) 50000

constants_loss_constant=[] # prob
constants_delay_poisson = [100]# Pois(lambda)
constants_delay_uniform=[] # U(0,UB) #---

