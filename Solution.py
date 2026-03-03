import copy

class Solution():
    def __init__(
        self,
        truck_route: list,
        drone_1: list,
        drone_2: list,
        drone_1_send: list,
        drone_2_send: list,
        drone_1_receive: list,
        drone_2_receive: list
    ):
        self.truck_route = truck_route
        self.drone_1 = drone_1
        self.drone_2 = drone_2
        self.drone_1_send = drone_1_send
        self.drone_2_send = drone_2_send
        self.drone_1_receive = drone_1_receive
        self.drone_2_receive = drone_2_receive
    

    def copy(self):
        return Solution(
            truck_route=copy.deepcopy(self.truck_route),
            drone_1=copy.deepcopy(self.drone_1),
            drone_2=copy.deepcopy(self.drone_2),
            drone_1_send=copy.deepcopy(self.drone_1_send),
            drone_2_send=copy.deepcopy(self.drone_2_send),
            drone_1_receive=copy.deepcopy(self.drone_1_receive),
            drone_2_receive=copy.deepcopy(self.drone_2_receive),
        )
    
        
    def to_solution_string(self):
        product_string = ""
        for nodes in self.truck_route:
            product_string = product_string + str(nodes) + ","
        product_string = product_string + "|"

        for nodes in self.drone_1:
            product_string = product_string + str(nodes) + ","
        product_string = product_string + "-1,"

        for nodes in self.drone_2:
            product_string = product_string + str(nodes) + ","
        product_string = product_string + "|"

        for i in self.drone_1_send:
            product_string = product_string + str(i) + ","
        product_string = product_string + "-1,"

        for i in self.drone_2_send:
            product_string = product_string + str(i) + ","
        product_string = product_string + "|"


        for i in self.drone_1_receive:
            product_string = product_string + str(i) + ","
        product_string = product_string + "-1,"

        for i in self.drone_2_receive:
            product_string = product_string + str(i) + ","

        return product_string

    
    
