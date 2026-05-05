from itertools import pairwise

def create_initial_solution(runner):
    
    solution = {
        "part1" : [],
        "part2" : [-1],
        "part3" : [-1],
        "part4" : [-1],
        }
        
    truck_times_copy = runner.truck_times.copy()
    truck_times_copy[: , 0]= -1

    solution["part1"].append(0)
    furthest_node = truck_times_copy[solution["part1"][-1]].argmax()
    truck_times_copy[: , furthest_node]= -1
    solution["part1"].append(int(furthest_node))
    
    for n in range(runner.n_nodes-2):
        furthest_node = truck_times_copy[solution["part1"][-1]].argmax()
        truck_times_copy[: , furthest_node]= -1

        min_path_length = float('inf')
        for i,j in pairwise(solution["part1"]):
            path_lenght = runner.truck_times[i][furthest_node]
            path_lenght += runner.truck_times[furthest_node][j]

            if path_lenght < min_path_length:
                best_insert = solution["part1"].index(j)
        

        solution["part1"].insert(best_insert, int(furthest_node))
    solution["part1"].append(0)

    return solution