from Solution import Solution
from main import read_data, SolutionRunner, parse_solution



def create_initial_runner(filename):

    n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)
    depot_index = 0
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(0,n_nodes))
    nodes_list.append(0)
    
    initial_solution = Solution(nodes_list,[],[],[],[],[],[])

    return SolutionRunner(
        parse_solution(initial_solution.to_solution_string()),
        truck_times=truck_times,
        flight_time_matrix=drone_times,
        flight_range_limit=flight_range,
        depot_index=depot_index,
        max_iterations=10,
        convergence_threshold=1.0,
        n_drones=n_drones,
    )

example_filename = "Truck_Drone_Contest_new.txt"
initial_runner = create_initial_runner(example_filename)
print(initial_runner.run())
