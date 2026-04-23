import copy
from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution
from TruckSectionReinsert import truck_section_reinsert
from FlattenSection import flatten_section

def adaptive_sa(runner, iterations):
    # Calibration split:
    split = iterations // 100
    delta_w = []
    t_f = 0.1

    ###Weights of operator. Should match nr of operators
    weights = [1.0, 1.0, 1.0]
    k = iterations//100
    print("Weights are updated every", k , "iterations")

    # Long term scores (updated every k iterations)
    scores = [1.0, 1.0, 1.0] 

    # Short term rewards and how often the operator was chosen (updated every iteration)
    rewards = [0, 0, 0]
    counts = [0, 0 ,0]

    ###Rewards for updating scores
    new_best_reward = 3
    improvement_reward = 2
    sa_accept_reward = 1
    decay = 0.5

    redundant_operators = 0
    #--Start
    result = runner.run()

    #Initial check that initial solution is feasible
    if result["feasible"]:
        best_solution = copy_solution(runner.solution)
        best_objective = result["objective"]
        incumbent_solution = copy_solution(runner.solution)
        incumbent_objective = result["objective"]
    else:
        print("ERROR- Initial result is not feasible")


    #-- Calibrate temperature
    for w in range(split):

        #Random number to pass SA-threshold
        rand = random.randint(0,100)
        rand = rand/100
        
        #Progress update
        if (w % 100 == 0):
            print()
            print("Tuning: Iteration", w)


        #Operation choice
        op = random.choices([0, 1, 2], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)


        # Check feasibility and delta_e
        candidate_feasible = runner.is_solution_feasible(candidate_solution)
        delta_e = candidate_objective - incumbent_objective

        #Update accordingly
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)

        elif candidate_feasible:
            if rand < 0.8: 
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
            delta_w.append(delta_e)


    #Now, we can update initial temperatures and cooling based on the tuning.
    if len(delta_w) == 0:
        print("Error, delta_W is empty, likely indicating too small sample size.")
    delta_avg = sum(delta_w)/len(delta_w)
    t_0 = (-1 * delta_avg)/(math.log(0.8))
    alpha = (t_f / t_0) ** (1/(iterations - split))
    t = t_0
    print()
    print("Improvements during tuning: ", delta_w)
    print("Average improvement:", delta_avg)
    print(iterations, split)
    print("Alpha:", alpha)
    print("Initial temperature and final temperature:", t_0, t_f)
    
    # Main iteration loop:
    for i in range(split, iterations):
        rand = random.randint(0,100)
        rand = rand/100

        #Progress
        if ((i) % 100 == 0):
            print()
            print("Iteration:", i , "| Best objective:", best_objective, "| Weights:", weights)


        #Operation choice
        op = random.choices([0, 1, 2], weights=weights)[0]
        counts[op] += 1
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)

        #If no insertions are found using one-reinsert, it will return none.
        if not candidate_solution:
            redundant_operators += 1
            continue

        #Double check feasibility
        candidate_feasible = runner.is_solution_feasible(candidate_solution)
        delta_e = candidate_objective - incumbent_objective

        #We always accept negative delte_e so we set p to 1 in these cases (saves computation and prevents p from exploding) 
        if delta_e < 0:
            p = 1.0
        else:
            p = math.exp(-1*delta_e/t) 
        
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            rewards[op] += (improvement_reward * (1 - (t/t_0)))
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
                rewards[op] += new_best_reward
                
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                rewards[op] += (sa_accept_reward * (t/t_0))
        t = alpha * t

        # Update weights every k iterations
        if i % k == 0:
            scores_sum = 0
            print("Rewards and Counts this split:", rewards, " | " , counts)
            for c in range(3):
                if counts[c] > 0:
                    avg_reward = rewards[c]/counts[c]
                    scores[c] = (1-decay) * scores[c] + decay * avg_reward
                    scores[c] = max(scores[c],1)
                    scores_sum += scores[c]
                else:
                    scores[c] = (1-decay) * scores[c]
                    scores[c] = max(scores[c],1)
                    scores_sum += scores[c]
                    
            scores_sum /= len(scores)
            rewards = [0,0,0]
            counts = [0,0,0]

            eps = 1e-8
            # w_i = exp(S_i / τ) / Σ exp(S_j / τ)
            weights = [(s + eps) / (scores_sum + eps * len(scores)) for s in scores]
            print("Scores and Weights next split:", scores, " | " , weights)


    return best_solution