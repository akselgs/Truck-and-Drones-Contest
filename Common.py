import numpy as np
import json

n_drones = 2 #fixed
drone_capacity = 1 #fixed
depot_index=0 #fixed

def copy_solution(solution: dict):
    solution_copy = solution.copy()
    solution_copy["part1"] = solution["part1"][:]
    solution_copy["part2"] = solution["part2"][:]
    solution_copy["part3"] = solution["part3"][:]
    solution_copy["part4"] = solution["part4"][:]

    return solution_copy

def parse_solution(values: str):
    """
    values: string like "1,2,3,|,10,20,|,5,6,|,100,200"
            or "1,2,3|10,20|5,6|100,200"
    returns: {"part1": [...], "part2": [...], "part3": [...], "part4": [...]}
    """

    if not isinstance(values, str):
        raise TypeError(f"Expected string from Go, got {type(values)}")

    s = values.strip()

    # normalize around pipes: ",|," or ",|" or "|," -> "|"
    s = s.replace(",|,", "|").replace(",|", "|").replace("|,", "|")

    parts = s.split("|")
    if len(parts) != 4:
        raise ValueError(f"Expected 4 parts separated by '|', got {len(parts)} parts: {parts}")

    def parse_int_list(part: str):
        # split by comma, ignore empty chunks (can happen after normalization)
        chunks = [c.strip() for c in part.split(",") if c.strip() != ""]
        return [int(c) for c in chunks]

    return {
        "part1": parse_int_list(parts[0]),
        "part2": parse_int_list(parts[1]),
        "part3": parse_int_list(parts[2]),
        "part4": parse_int_list(parts[3]),
    }

def read_data(filename: str):
    truck_times = []
    drone_times = []
    hash_count=0
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line[0]!="#":
               row = list(map(float, line.strip().split()))
               if hash_count == 1:
                  n_customers = int(row[0])
               if hash_count == 2:
                  flight_range = int(row[0])
               elif hash_count == 3:
                  truck_times.append(row)
               elif hash_count == 4:
                  drone_times.append(row) 
            else:
               hash_count+=1
            
    n_nodes = n_customers+1 
    truck_times=np.array(truck_times)
    drone_times=np.array(drone_times)

    return n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range,  drone_capacity

def save_to_file(filename: str, solution, objective, this_run_best_objective, all_time_best_objective):

    #Best this run:
    if objective < this_run_best_objective:
        with open("solutions/" + filename[5:-4] + "_current.json", "w") as current:
            json.dump({
                "part1" : solution["part1"],
                "part2" : solution["part2"],
                "part3" : solution["part3"],
                "part4" : solution["part4"],
                }, current)
        this_run_best_objective = objective

    #New all time best
    if objective < all_time_best_objective:
        print("NEW ALL TIME BEST!")
        with open("solutions/" + filename[5:-4] + "_best.json", "w") as best:
            json.dump({
                "part1" : solution["part1"],
                "part2" : solution["part2"],
                "part3" : solution["part3"],
                "part4" : solution["part4"],
                }, best)
        all_time_best_objective = objective
        print(all_time_best_objective)
            
def load_best(filename: str):
    path = "solutions/" + filename[5:-4] + "_best.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # no best yet
    