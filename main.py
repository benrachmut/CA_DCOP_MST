
from Globals import *
from Problems import DCOP_MST
from general_communication_protocols import get_communication_protocols

global length
global width

def generate_dcop_mst():
    ans = []
    for agent_size in agents_sizes:
        for target_size in targets_sizes:
            for density in obstacle_densities:
                for size in map_sizes:
                    global width,length
                    width = size[0] # x
                    length  = size[1] # y


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


def create_communication_protocols():
    communication_protocols = get_communication_protocols(
        is_with_timestamp=is_with_timestamp, length=length, width=width,
        is_with_perfect_communication=is_with_perfect_communication, constants_loss_distance=constants_loss_distance,
        constants_delay_poisson_distance=constants_delay_poisson_distance,
        constants_delay_uniform_distance=constants_delay_uniform_distance,
        constants_loss_constant=constants_loss_constant,
        constants_delay_poisson=constants_delay_poisson,
        constants_delay_uniform=constants_delay_uniform)

    return communication_protocols


def run_dcop_msts(dcop_msts, communication_protocols):
    for dcop_mst in dcop_msts:
        for protocol in communication_protocols:
            mailer = get_mailer(protocol, dcop_mst) # TODO @ben
            dcop_mst.dcop_mst_meet_mailer(mailer) # TODO @ben
            mailer.mailer_meets_Dcop(dcop_mst.id_) # TODO @ben
            dcop_mst.initilize_and_start_agents()
            dcop_mst.infrom_all_agents_upon_TimeStamp(protocol,agents)# TODO @ben
            start_mailer(mailer, dcop)
            sava_mailer_info(mailer)

if __name__ == '__main__':
    dcop_msts = generate_dcop_mst()
    communication_protocols = create_communication_protocols()
    run_dcop_msts(dcop_msts,communication_protocols)

