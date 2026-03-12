#PLAN:
# 1-reinsert
# Choose random node:
#
# 4 scenarios:
# 
# 1- From truck to truck:
# Drones indexing are unchanged
#
# 2- From truck to drone:
# Verify truck is longer than drone
# Drone that is received by moved truck-node should follow the successor
# Drone that is sendt by moved truck-node should follow the predecessor
# These are always valid as we can not move depot nodes.
#
# Find all insertion options. by searching gaps in sendt and received indexing:
# Choose random insertion option, select random send and receive nodes within that window.
#
# 3- From drone to truck:
# New truck route follows the sending node to the drone-node and then to sending node's sucessor.
# 
# 4- From drone to drone:
# Original drone indexes are deleted, and new ones are created at random from insertion options as in scenario 2.
from InitialSolution import create_initial_runner
from main import SolutionRunner
import random

def one_reinsert(runner):
    n_nodes = len(runner.solution["part1"]) + len(runner.solution["part2"]) - 3
    print(n_nodes)

    remove_node = random.randint(1,n_nodes)
    remove_node = 18
    print("removed node:", remove_node)

    if (remove_node in runner.solution["part1"]): #Remove node was originally truck-node:
        print("node", remove_node, "was moved from truck")
        remove_node_index = runner.solution["part1"].index(remove_node)

        runner.solution["part1"].remove(remove_node)
        insert_option = random.randint(1,3)
        print("insert option:",insert_option)
        if insert_option == 1:
            insert_position = random.randint(1, len(runner.solution["part1"])-1)
            runner.solution["part1"].insert(insert_position, remove_node)

        
        else:
            runner.solution["part2"].pop()
            runner.solution["part2"].extend([5,18,23,10,-1,7,91,16,14,15,50])
            runner.solution["part3"].pop()
            runner.solution["part3"].extend([1,3,5,10,-1,0,2,4,6,8,10])
            runner.solution["part4"].pop()
            runner.solution["part4"].extend([3,4,8,11,-1,1,3,5,8,10,11])

            splitpoint = runner.solution["part4"].index(-1)

            part2_1 = runner.solution["part2"][:splitpoint]
            part2_2 = runner.solution["part2"][splitpoint+1:]
            part3_1 = runner.solution["part3"][:splitpoint]
            part3_2 = runner.solution["part3"][splitpoint+1:]
            part4_1 = runner.solution["part4"][:splitpoint]
            part4_2 = runner.solution["part4"][splitpoint+1:]
            print("===")
            print(part3_2)
            
            part3_1 = [x-1 if x == remove_node_index else x for x in part3_1]
            part3_2 = [x+1 if x == remove_node_index else x for x in part3_2]
            part4_1 = [x-1 if x == remove_node_index else x for x in part4_1]
            part4_2 = [x+1 if x == remove_node_index else x for x in part4_2]

            if insert_option == 2:
                #part3_1.append(len(runner.solution["part1"]))
                part3_1.append(13)
                part4_1 = part4_1
                part4_1.insert(0,0)

                sending_candidates = []
                for i in range(0, len(part3_1)):
                    if part4_1[i]-part3_1[i] <= -1:
                        sending_candidates.extend(list(range(part4_1[i],part3_1[i])))

                selected_sender = random.sample(sending_candidates,1)[0]

                insertion_index = -1 #Only an initial value, NOT the same as the -1 used as separator
                for i in range(0, len(part3_1)):
                    if selected_sender < part3_1[i]:
                        receiver_candidates = list(range(selected_sender+1,part3_1[i]+1))
                        insertion_index = i
                        print(insertion_index)
                        break
                    
                selected_receiver = random.sample(receiver_candidates,1)[0]

                part3_1.remove(13)
                part4_1.remove(0)

                part2_1.insert(insertion_index, remove_node)
                part3_1.insert(insertion_index, selected_sender)
                part4_1.insert(insertion_index, selected_receiver)

                runner.solution["part2"] = part2_1 + [-1] + part2_2
                runner.solution["part3"] = part3_1 + [-1] + part3_2
                runner.solution["part4"] = part4_1 + [-1] + part4_2

            if insert_option == 3:
                #part3_1.append(len(runner.solution["part1"]))
                part3_2.append(13)
                part4_2.insert(0,0)

                sending_candidates = []
                for i in range(0, len(part3_2)):
                    if part4_2[i]-part3_2[i] <= -1:
                        sending_candidates.extend(list(range(part4_2[i],part3_2[i])))

                selected_sender = random.sample(sending_candidates,1)[0]

                insertion_index = -1 #Only an initial value, NOT the same as the -1 used as separator
                for i in range(0, len(part3_2)):
                    if selected_sender < part3_2[i]:
                        receiver_candidates = list(range(selected_sender+1,part3_2[i]+1))
                        insertion_index = i
                        print(insertion_index)
                        break
                    
                selected_receiver = random.sample(receiver_candidates,1)[0]

                part3_2.remove(13)
                part4_2.remove(0)

                part2_2.insert(insertion_index, remove_node)
                part3_2.insert(insertion_index, selected_sender)
                part4_2.insert(insertion_index, selected_receiver)

                runner.solution["part2"] = part2_1 + [-1] + part2_2
                runner.solution["part3"] = part3_1 + [-1] + part3_2
                runner.solution["part4"] = part4_1 + [-1] + part4_2

    elif (remove_node in runner.solution["part2"]): #Remove node was origianlly drone-node.
        print("wtf..")
        
    print(remove_node in runner.solution["part2"])


    new_runner = runner
    return new_runner

example_filename = "Truck_Drone_Contest_new.txt"
example_runner = create_initial_runner(example_filename)
new_runner = one_reinsert(example_runner)
print(new_runner.solution)
print(new_runner.run())