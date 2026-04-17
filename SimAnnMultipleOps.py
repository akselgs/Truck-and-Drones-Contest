import copy
from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution
from TruckSectionReinsert import truck_section_reinsert
from FlattenSection import flatten_section

def sim_ann_multiple_ops(runner, iterations):
    split = iterations // 100
    rand = random.randint(0,100)
    rand = rand/100
    delta_w = []
    t_f = 0.1
    op_1_threshold = 30
    op_2_threshold = 30

    scores = [1.0, 1.0, 1.0]  # one per operator
    weights = [1.0, 1.0, 1.0]
    new_best_reward = 3
    improvement_reward = 2
    sa_accept_reward = 1
    decay = 0.5
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

        op = random.choices([0, 1, 2], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)

        if not candidate_solution:
            if w % 100 == 0: 
                print("No insertion positions found, continuing to next iteration from calibration-split.")
            continue
        candidate_feasible = runner.is_solution_feasible(candidate_solution)

        delta_e = candidate_objective - incumbent_objective
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            scores[op] += improvement_reward
            if incumbent_objective < best_objective:
                best_solution =copy_solution(incumbent_solution)
                print()
                print("New best solution found")
                print(best_solution)
                print(best_objective)
                scores[op] += new_best_reward

        elif candidate_feasible:
            if rand < 0.8: 
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                scores[op] += sa_accept_reward
            delta_w.append(delta_e)
        if w % 100 == 0:
            weights[op] = (1 - decay) * weights[op] + decay * scores[op]
            scores = [1.0, 1.0, 1.0]  # reset scores    
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
        if early_stop_counter > 10000:
            return best_solution
        if (i % 500 == 0):
            print()
            print("Iteration", i + split)
            print("Early stop counter:", early_stop_counter)
            print("Weights")
            print(weights)
        #print("incumb")
        #print(incumbent_runner.solution)
        op = random.choices([0, 1, 2], weights=weights)[0]
        #rand_op = 1
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)

        if not candidate_solution:
            if i % 100 == 0: 
                print("No insertion positions found, continuing to next iteration from calibration-split.")
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
            scores[op] += improvement_reward
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
                print()
                print("New best solution found, operation:", op)
                print()
                print(best_solution)
                print(best_objective)
                early_stop_counter = 0
                scores[op] += new_best_reward
                
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                #print()
                #print("=======================")
                if i % 100 == 0:
                    print("Worse solution explored, operation:", op)
                #print(incumbent_solution)
                #print(incumbent_objective)
                #print("Delta E", delta_e)
                #print("=======================")
                scores[op] += sa_accept_reward
        t = alpha * t

        if i%100 == 0:
            weights[op] = (1 - decay) * weights[op] + decay * scores[op]
            scores = [1.0, 1.0, 1.0]  # reset scores
    
    print("final weights:")
    print(weights)


    return best_solution