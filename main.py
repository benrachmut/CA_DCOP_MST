
from Globals import *
from Problems import DCOP_MST




def generate_dcop_mst():
    ans = []
    for agent_size in agents_sizes:
        for target_size in targets_sizes:
            for density in obstacle_densities:
                for size in map_sizes:
                    for sensing_range in sensing_ranges:
                        for moving_range in moving_ranges:
                            for cred_constant in cred_constants:
                                for req_constant in req_constants:
                                    for moving_speed in moving_speeds:
                                        for rep in range(reps):
                                            dcop_mst = DCOP_MST(rep,algorithm,agent_size, target_size, density, size, sensing_range, moving_range,
                                                  cred_constant, req_constant,moving_speed)
                                            ans.append(dcop_mst)
    return ans


if __name__ == '__main__':
    dcop_msts = generate_dcop_mst()
    #communication_protocols = create_communication_protocols()
    #run_dcop_msts(dcop_msts,communication_protocols)

