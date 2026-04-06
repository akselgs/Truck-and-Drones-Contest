from FeasibiltyCheck import SolutionFeasibility
from CalCulateTotalArrivalTime import CalCulateTotalArrivalTime
import copy



class SolutionRunner(CalCulateTotalArrivalTime, SolutionFeasibility):
    def __init__(
        self,
        solution: dict,
        truck_times,
        drone_times,
        flight_range_limit: float,
        n_nodes: int,
        depot_index: int = 0,
        max_iterations: int = 10,
        convergence_threshold: float = 1.0,
        n_drones: int = 2,
        
    ):
        """
        Wraps feasibility check + total cost calculation in one object.
        """
        self.solution = solution
        self.truck_times = truck_times
        self.drone_times = drone_times
        self.flight_range  = flight_range_limit
        self.depot_index = depot_index
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.n_drones = n_drones
        self.n_nodes=n_nodes

        n_nodes = truck_times.shape[0]

        # Create feasibility checker based on the instance
        self.feasibility = SolutionFeasibility(
            #n_nodes=n_nodes,
            n_nodes=truck_times.shape[0],
            n_drones=n_drones,
            depot_index=depot_index,
            drone_times=drone_times,
            flight_range=flight_range_limit,
        )

    def run(self, debug=False):

  
        def debug_print(*args, **kwargs):
            if debug:
                print(*args, **kwargs)
        """
        1) Check feasibility
        2) If infeasible: print message and return None
        3) If feasible: compute total waiting/arrival time and return it
        """
        sol = self.solution
        f = self.feasibility

        #print("=== FEASIBILITY CHECK ===")
        truck_ok = f.is_truck_route_feasible(sol)
        complete_ok = f.is_complete_solution(sol)
        parts_ok = f.are_parts_consistent(sol)
        drones_ok = f.are_all_drone_trips_feasible(sol)
        global_ok = f.is_solution_feasible(sol)

        debug_print("Truck feasible   :", truck_ok)
        debug_print("Complete         :", complete_ok)
        debug_print("Parts consistent :", parts_ok)
        debug_print("Drone trips OK   :", drones_ok)

        if not global_ok:
            debug_print("\nCannot calculate the total cost, since the solution is not feasible.")
            debug_print("GLOBAL FEASIBLE  :", global_ok)
            return {'error': '', 'feasible': False, 'objective': 0.0} 

        # If we get here, the solution is feasible → compute total waiting time
        total, arr, dep, feas = self.calculate_total_waiting_time(
            solution=sol
        )
        
        if not feas:
           debug_print("GLOBAL FEASIBLE  :", feas) 
           debug_print("Flight range limits on one of the drones is not satisfied") 
           return {'error': '', 'feasible': False, 'objective': 0.0}  

        debug_print("GLOBAL FEASIBLE  :", feas) 
        debug_print("Total objective:", float(total))
        return {'error': '', 'feasible': True, 'objective': total}#total, arr, dep

    def copy(self):
        return(
            SolutionRunner(
                solution = copy.deepcopy(self.solution),
                truck_times = self.truck_times,
                drone_times = self.drone_times,
                flight_range_limit = self.flight_range,
                depot_index= self.depot_index,
                max_iterations=self.max_iterations,
                convergence_threshold=self.convergence_threshold,
                n_drones=self.n_drones,
            )
        )