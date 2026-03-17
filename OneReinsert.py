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
# Drone indexing are unchanged *or swapped between drones in case drone swap..
from InitialSolution import create_initial_runner
from main import SolutionRunner, read_data, parse_solution
import random

#Random removal- random insert
def one_reinsert(runner):
    n_nodes = len(runner.solution["part1"]) + len(runner.solution["part2"]) - 3
    print("ONE RE-INSERT")
    print(runner.solution)

    remove_node = random.randint(1,n_nodes)
    remove_node = 5

    if (remove_node in runner.solution["part1"]): #Remove node was originally truck-node:
        remove_node_index = runner.solution["part1"].index(remove_node)
        runner.solution["part1"].remove(remove_node)
        print()
        print("node", remove_node, "was moved from truck at index", remove_node_index)
        print(runner.solution)

        #If this node is a sender or reciever, we reinser into truck path.
        if ((remove_node_index in runner.solution["part3"]) or (remove_node_index in runner.solution["part4"])):
            print("this is a sender or receiver, so must be reinserted to truck, so we don't have to deal with extra node")
            insert_option = 0
        
        else:
            insert_option = random.randint(0,2)
            insert_option = 1


        if insert_option == 0:
            insert_position = random.randint(1, len(runner.solution["part1"])-1)
            runner.solution["part1"].insert(insert_position, remove_node)
            print()
            print("inserted into truck_route, at index", insert_position)
            print(runner.solution)

        
        else:
            splitpoint = runner.solution["part4"].index(-1)

            part2 = [runner.solution["part2"][:splitpoint],runner.solution["part2"][splitpoint+1:]]

            part3 = [runner.solution["part3"][:splitpoint],runner.solution["part3"][splitpoint+1:]]

            part4 = [runner.solution["part4"][:splitpoint],runner.solution["part4"][splitpoint+1:]]

            part3[0] = [x-1 if x > remove_node_index else x for x in part3[0]]
            part3[1] = [x-1 if x > remove_node_index else x for x in part3[1]]
            part4[0] = [x-1 if x > remove_node_index else x for x in part4[0]]
            part4[1] = [x-1 if x > remove_node_index else x for x in part4[1]]

            runner.solution["part3"] = part3[0] + [-1] + part3[1]
            runner.solution["part4"] = part4[0] + [-1] + part4[1]
            print()
            print("to be inserted into drone", insert_option)
            print("shifted indexes larger than the remove node's index: ", remove_node_index)
            print(runner.solution)

            drone_index = insert_option-1

            #Temprorarily add 0 and x to send and receive for comparing lists.
            part3[drone_index].append(len(runner.solution["part1"]))
            part4[drone_index].insert(0,0)

            #Find sender candidates between the sender and receiver positions
            sending_candidates = []
            for i in range(0, len(part3[drone_index])):
                if part4[drone_index][i]-part3[drone_index][i] <= -1:
                    sending_candidates.extend(list(range(part4[drone_index][i],part3[drone_index][i])))

            selected_sender = random.sample(sending_candidates,1)[0]

            #Find receiver candidates (between selected sender and the "next possible sender")")
            insertion_index = -1 #Only an initial value, NOT the same as the -1 used as separator
            for i in range(0, len(part3[drone_index])):
                if selected_sender < part3[drone_index][i]:
                    receiver_candidates = list(range(selected_sender+1,part3[drone_index][i]+1))
                    insertion_index = i
                    print(insertion_index)
                    break

            selected_receiver = random.sample(receiver_candidates,1)[0]


            #Now we can remove the temp additions
            part3[drone_index].pop()
            part4[drone_index].remove(0)

            #And we insert the node we removed into the node's list with the corresponding indexes
            part2[drone_index].insert(insertion_index, remove_node)
            part3[drone_index].insert(insertion_index, selected_sender)
            part4[drone_index].insert(insertion_index, selected_receiver)


            #We update the list.
            runner.solution["part2"] = part2[0] + [-1] + part2[1]
            runner.solution["part3"] = part3[0] + [-1] + part3[1]
            runner.solution["part4"] = part4[0] + [-1] + part4[1]

            if insert_option == 2:
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

    else:
        print("remove node not found in truck route or drone route. ERROR...")
        
    print(remove_node in runner.solution["part2"])


    new_runner = runner
    return new_runner

example_filename = "Data/F_10.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(example_filename)
depot_index = 0
example_runner = SolutionRunner(
    solution=parse_solution("0,5,3,2,6,9,4,7,0,|8,10,1,-1,|2,3,5,-1,|3,4,6,-1,"),
    truck_times=truck_times,
    flight_time_matrix=drone_times,
    flight_range_limit=flight_range,
    depot_index=depot_index,
    max_iterations=10,
    convergence_threshold=1.0,
    n_drones=n_drones,
)
print("Example runner:")
print(example_runner.solution)
print(example_runner.run())
#example_runner = create_initial_runner(example_filename)
new_runner = one_reinsert(example_runner)
print("New runner:")
print(new_runner.solution)
print(new_runner.run())