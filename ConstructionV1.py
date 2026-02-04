from main import read_data


filename = "Truck_Drone_Contest.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)

def initialize(n_nodes):
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(n_nodes+1))

    nodes_list.pop(0)#Generate list of customers we have served.
    served_customers = []

    return nodes_list

nodes_list = initialize(n_nodes)
#Main loop:
for nodes in range(1,n_nodes+1):
    truck_times

    drone_candidates

    



print(truck_times)