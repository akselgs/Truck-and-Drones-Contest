import copy
from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution

def sim_ann(runner, iterations):
    split = iterations // 100
    rand = random.randint(0,100)
    rand = rand/100
    delta_w = []
    t_f = 0.1

    result = runner.run()
    if result["feasible"]:
        best_solution = copy_solution(runner.solution)
        best_objective = result["objective"]
        incumbent_solution = copy_solution(runner.solution)
        incumbent_objective = result["objective"]
        early_stop_counter = 0
    else:
        print("ERROR- Initial result is not feasible")


    for w in range(split):
        rand = random.randint(0,100)
        rand = rand/100
        
        if (w % 100 == 0):
            print()
            print("Iteration", w)
            print("Random:", rand)

        rand_op = random.randint(0,2)
        if rand_op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif rand_op == 1:
            print("op 2")
        else:
            print("op 3")

        if not candidate_solution:
            print("No insertion positions found, continuing to next iteration from calibration-split.")
            continue
        candidate_feasible = runner.is_solution_feasible(candidate_solution)

        delta_e = candidate_objective - incumbent_objective
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            if incumbent_objective < best_objective:
                best_solution =copy_solution(incumbent_solution)
                print()
                print("New best solution found")
                print(best_solution)
                print(best_objective)

        elif candidate_feasible:
            if rand < 0.8: 
                incumbent_solution = copy_solution(candidate_solution)
            delta_w.append(delta_e)
    if len(delta_w) == 0:
        print("Error, delta_W is empty, likely indicating too small sample size.")
        delta_w.append(2)

    delta_avg = sum(delta_w)/len(delta_w)
    t_0 = (-1 * delta_avg)/(math.log(0.8))
    alpha = (t_f / t_0) ** (1/(iterations - split))
    t = t_0
    
    for i in range(iterations - split):
        rand = random.randint(0,100)
        rand = rand/100

        

        early_stop_counter += 1
        if early_stop_counter > 5000:
            return best_solution
        if (i % 100 == 0):
            print()
            print("Iteration", i + split)
            print("Early stop counter:", early_stop_counter)
            print("Random:", rand)
        #print("incumb")
        #print(incumbent_runner.solution)
        rand_op = random.randint(0,2)
        if rand_op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif rand_op == 1:
            print("op 2")
        else:
            print("op3")
        if not candidate_solution:
            print("No insertion positions found, continuing to next iteration.")
            continue
        candidate_feasible = runner.is_solution_feasible(candidate_solution)
        #print("cand")
        #print(candidate_runner.solution)

        delta_e = candidate_objective - incumbent_objective
        try: 
            p = math.exp(-1*delta_e/t) 
        except:
            print("ERROR: Program crashed at - p = math.exp(-1*delta_e/t)")
            print("alpha", alpha)
            print("delta_e", delta_e)
            print("t", t)
            print("t_0", t_0)
            return "Error"
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
                print()
                print("New best solution found")
                print()
                print(best_solution)
                print(best_objective)
                early_stop_counter = 0
                
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                #print()
                #print("=======================")
                print("Worse solution explored")
                #print(incumbent_solution)
                #print(incumbent_objective)
                #print("Delta E", delta_e)
                #print("=======================")

        t = alpha * t

    return best_solution