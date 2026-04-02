import copy
from OneReinsert import one_reinsert
import random
import math

def sim_ann(initial_runner, iterations):
    candidate_runner = copy.deepcopy(initial_runner)
    best_runner = copy.deepcopy(initial_runner)
    incumbent_runner = copy.deepcopy(initial_runner)
    incumbent_split = iterations // 100
    rand = random.randint(0,100)
    rand = rand/100
    delta_w = []
    t_f = 0.1

    result = initial_runner.run()
    if result["feasible"]:
        best_solution = initial_runner.solution
        best_objective = result["objective"]
        incumbent_solution = initial_runner.solution
        incumben_objective = result["objective"]
    else:
        print("ERROR- Initial result is not feasible")

    for w in range(incumbent_split):
        if (w % 100 == 0):
            print()
            print("Iteration", w)
        candidate_runner.solution = one_reinsert(incumbent_runner)
        candidate_result = candidate_runner.run(debug=False)
        incumbent_result = incumbent_runner.run()
        delta_e = candidate_result["objective"] - incumbent_result["objective"]
        if candidate_result["feasible"] and (delta_e < 0):
            incumbent_runner.solution = copy.deepcopy(candidate_runner.solution)
            incumbent_result = incumbent_runner.run()
            best_result = best_runner.run()
            if incumbent_result["objective"] < best_result["objective"]:
                best_runner.solution = copy.deepcopy(incumbent_runner.solution)
                print()
                print("New best solution found")
                print(best_runner.solution)
                best_result = best_runner.run(debug = True)

        elif candidate_result["feasible"]:
            if rand < 0.8: 
                incumbent_runner.solution = copy.deepcopy(candidate_runner.solution)
            delta_w.append(delta_e)
    if len(delta_w) == 0:
        print("Delta W empty. Adding number to avoid adding by zero")
        delta_w.append(2)
    delta_avg = sum(delta_w)/len(delta_w)
    t_0 = (-1 * delta_avg)/(math.log(0.8))
    alpha = (t_f / t_0) ** (1/(iterations - incumbent_split))
    t = t_0
    
    for i in range(iterations - incumbent_split):
        if (i % 100 == 0):
            print()
            print("Iteration", i + incumbent_split)
        #print("incumb")
        #print(incumbent_runner.solution)
        candidate_runner.solution = one_reinsert(incumbent_runner)
        #print("cand")
        #print(candidate_runner.solution)
        candidate_result = candidate_runner.run()
        incumbent_result = incumbent_runner.run()
        delta_e = candidate_result["objective"] - incumbent_result["objective"]
        try: 
            p = math.exp(-1*delta_e/t) 
        except:
            print("ERROR")
            print(alpha)
            print(delta_e)
            print(t)
            print(t_0)
            return "ERROR"
        if candidate_result["feasible"] and (delta_e < 0):
            incumbent_runner.solution = copy.deepcopy(candidate_runner.solution)
            incumbent_result = incumbent_runner.run()
            #best_result = best_runner.run()
            
            if incumbent_result["objective"] < best_result["objective"]:
                best_runner.solution = copy.deepcopy(incumbent_runner.solution)
                print()
                print("New best solution found")
                print(best_runner.solution)
                best_result = best_runner.run(debug = True)
        elif candidate_result["feasible"] and (rand <  p):
            if delta_e != 0:
                incumbent_runner.solution = copy.deepcopy(candidate_runner.solution)
                print()
                print("=======================")
                print("Worse solution explored")
                print(incumbent_runner.solution)
                incumbent_result = incumbent_runner.run(debug = True)
                print("Delta E", delta_e)
                print("=======================")

        t = alpha * t

    return best_runner