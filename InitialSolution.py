
from SolutionRunner import SolutionRunner
from Common import read_data


def create_initial_runner(filename):

    n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)
    depot_index = 0
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(0,n_nodes))
    nodes_list.append(0)
    
    initial_solution = {
        "part1" : nodes_list,
        "part2" : [-1],
        "part3" : [-1],
        "part4" : [-1]
    }

    return SolutionRunner(
        solution=initial_solution,
        truck_times=truck_times,
        drone_times=drone_times,
        flight_range_limit=flight_range,
        depot_index=depot_index,
        max_iterations=10,
        convergence_threshold=1.0,
        n_drones=n_drones,
    )
