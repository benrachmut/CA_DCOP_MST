from Problems import *


def distance_nodes(node1, node2):
    return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

###----All is using---###
def calculate_remained_coverage(dcop_mst:DCOP_MST):
    rem_cov_value = 0
    for target in dcop_mst.targets:
        target_req = target.req
        for agent in dcop_mst.agents:
            if distance_nodes(target.node, agent.node) <= agent.sensing_range:
                target_req = min(0, target_req - agent.cred)
        rem_cov_value += target_req
    return rem_cov_value

def calculate_movement_counter(dcop_mst:DCOP_MST):
    ans = 0
    for agent in dcop_mst.agents:
        ans += agent.movement_counter # todo @BEN
    return ans

def get_measurments():
    ans = {}
    ans["Remained_Coverage"] = calculate_remained_coverage
    ans["Movement_Counter"] = calculate_movement_counter

    return ans


