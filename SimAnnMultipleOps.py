import copy
from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution
from TruckSectionReinsert import truck_section_reinsert
from FlattenSection import flatten_section

def sim_ann_multiple_ops(runner, iterations):
    # Calibration split:
    split = iterations // 100
    delta_w = []
    t_f = 0.1

    ###Weights of operator. Should match nr of operators
    # scores = [1.0, 1.0, 1.0] #Scores if we want adjustable adaptive weights
    weights = [3.0, 1.0, 2.0]

    ###Rewards for updating scores
    # new_best_reward = 3
    # improvement_reward = 2
    # sa_accept_reward = 1
    # decay = 0.5


    #--Start
    result = runner.run()

    if result["feasible"]:
        best_solution = copy_solution(runner.solution)
        best_objective = result["objective"]
        incumbent_solution = copy_solution(runner.solution)
        incumbent_objective = result["objective"]
        early_stop_counter = 0
    else:
        print("ERROR- Initial result is not feasible")


    #-- Calibrate temperature
    for w in range(split):
        rand = random.randint(0,100)
        rand = rand/100
        
        if (w % 250 == 0):
            print()
            print("Iteration", w)


        op = random.choices([0, 1, 2], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)

        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)



        candidate_feasible = runner.is_solution_feasible(candidate_solution)

        delta_e = candidate_objective - incumbent_objective
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            # scores[op] += improvement_reward
            
            if incumbent_objective < best_objective:
                best_solution =copy_solution(incumbent_solution)
                print()
                print("New best solution found")
                print(best_solution)
                print(best_objective)
                # scores[op] += new_best_reward

        elif candidate_feasible:
            if rand < 0.8: 
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                # scores[op] += sa_accept_reward
            delta_w.append(delta_e)

        ###Update weights based on scores. Reset sometimes..
        # weights[op] = (1 - decay) * weights[op] + decay * scores[op]
        # if w % 100 == 0:
        #     scores = [1.0, 1.0, 1.0]

    if len(delta_w) == 0:
        print("Error, delta_W is empty, likely indicating too small sample size.")


    delta_avg = sum(delta_w)/len(delta_w)
    t_0 = (-1 * delta_avg)/(math.log(0.8))
    alpha = (t_f / t_0) ** (1/(iterations - split))
    t = t_0
    
    # Main iteration loop:
    for i in range(iterations - split):
        rand = random.randint(0,100)
        rand = rand/100

        if (i % 500 == 0):
            print()
            print("Iteration", i + split)
            print("Weights")
            print(weights)

        op = random.choices([0, 1, 2], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)

        #If no insertions are found using one-reinsert, it will return none.
        if not candidate_solution:
            if i % 100 == 0: 
                print("No insertion positions found, continuing to next iteration from calibration-split.")
            continue

        #Check feasibility
        candidate_feasible = runner.is_solution_feasible(candidate_solution)

        delta_e = candidate_objective - incumbent_objective

        if delta_e < 0:
            p = 1
        else:
        #This sometimes fails, we include some print statement for debugging in case it does.
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
            # scores[op] += improvement_reward
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
                print()
                print("New best solution found, operation:", op)
                print()
                print(best_solution)
                print(best_objective)
                # scores[op] += new_best_reward
                
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                # scores[op] += sa_accept_reward
        t = alpha * t

        # weights[op] = (1 - decay) * weights[op] + decay * scores[op]
        # if i%100 == 0:
        #     scores = [1.0, 1.0, 1.0]
    
    print("final weights:")
    print(weights)


    return best_solution