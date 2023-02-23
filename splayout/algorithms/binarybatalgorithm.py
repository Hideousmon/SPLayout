#####################################################################################################
## Reference: Mirjalili, S., Mirjalili, S.M. & Yang, XS. Binary bat algorithm. Neural Comput &
##            Applic 25, 663–681 (2014). https://doi.org/10.1007/s00521-013-1525-5
#####################################################################################################
import numpy as np
import math

class BinaryBatAlgorithm:
    """
    Binary Bat Algorithm.

    Parameters
    ----------
    noS : Int
        Number of solutions.
    loS : Int
        Length of a single solution.
    cost_function : func
        Cost function for evaluating a single solution, input: Array, size (loS,), output: Float, lower means better .
    max_iteration : Int
        Maximum of iterations (default: 500).
    callback_function : func
        Self-defined callback function that will be called after every iteration (default: None).
    loudness : Float
        Loudness in Binary Bat Algorithm (default: 0.25).
    pulse_rate : Float
        Pulse rate in Binary Bat Algorithm (default: 0.1).
    """
    def __init__(self, noS , loS, cost_function , max_iteration = 500,callback_function=None ,loudness = 0.25, pulse_rate = 0.1):
        self.max_iteration = max_iteration
        self.noS = noS
        self.loS = loS
        self.loudness = loudness
        self.pulse_rate = pulse_rate
        self.cost_function = cost_function
        ## some default parameters
        self.__Qmin = 0
        self.__Qmax = 2
        self.__N_iter = 0
        ## initial arrays
        self.__Q = np.zeros((noS,1)) # Frequency
        self.__v = np.zeros((noS,loS)) # Velocities
        self.__Sol = np.random.randint(0,2,size=(noS,loS)) # Initialize the solutions
        self.cg_curve = np.zeros((max_iteration))
        self.__cost = np.zeros((noS,1)) ## the cost of the population, the lower , the better (1 - FoM)
        self.__engine_flag = 0
        self.__iter = 0
        self.best_solution = np.zeros((1,loS))
        self.min_cost = math.inf
        self.__min_position = math.inf
        self.engine_init()
        if (callback_function == None):
            def call_back():
                pass
            self.call_back = call_back
        else:
            self.call_back = callback_function

    def engine_init(self):
        """
        Initialize the Binary Bat Algorithm, evaluate the first iteration.
        """
        for i in range(0, self.noS):
            self.__cost[i] = self.cost_function(self.__Sol[i, :])
        self.min_cost = np.min(self.__cost, axis=0)[0]
        self.__min_position = np.argmin(self.__cost, axis=0)[0]
        self.best_solution = self.__Sol[self.__min_position, :].copy()

        ## Initialize the iteration
        self.__iter = 0
        self.__engine_flag = 1

    def run(self):
        """
        Run the engine.
        """
        if(self.__engine_flag == 0):
            raise Exception("Engine has not been initialized, run: \"obj.engine_init()\" first")
        while (self.__iter < self.max_iteration):
            self.cg_curve[self.__iter] = self.min_cost
            self.__iter += 1
            for i in range(0,self.noS):
                ## create a temporal solution
                temp_solution = self.__Sol[i,:]
                for j in range(0,self.loS):
                    self.__Q[i] = self.__Qmin + (self.__Qmin - self.__Qmax)*np.random.rand() # Equation 3
                    self.__v[i,j] = self.__v[i,j] + (temp_solution[j] - self.best_solution[j]) * self.__Q[i] # Equation 1

                    V_shaped_transfer_function = abs((2/math.pi)*math.atan((math.pi/2)*self.__v[i,j]))

                    if np.random.rand() < V_shaped_transfer_function :
                        temp_solution[j] = (temp_solution[j] + 1 ) %2

                    if np.random.rand() > self.pulse_rate:
                        temp_solution[j] = self.best_solution[j].copy()

                ## Calculate the cost
                new_cost =  self.cost_function(temp_solution)
                if (new_cost <= self.__cost[i]) and (np.random.rand() < self.loudness):
                    self.__Sol[i,:] = temp_solution
                    self.__cost[i] = new_cost

                # Ppdate the current best
                if new_cost <= self.min_cost:
                    self.best_solution = temp_solution.copy()
                    self.min_cost = new_cost

            ## Call back function
            self.call_back()

        self.__engine_flag = 0

    def get_iteration_number(self):
        """
        Get the temporal iteration number.

        Returns
        -------
        out : Int
            Iteration number.
        """
        return self.__iter

    def get_min_cost(self):
        """
        Get the temporal minimum of cost.

        Returns
        -------
        out : Float
            Minimum of cost.
        """
        return self.min_cost

    def get_best_solution(self):
        """
        Get the temporal best solution.

        Returns
        -------
        out : Array
            Best solution.
        """
        return self.best_solution

    def get_total_solutions(self):
        """
        Get the temporal total solutions.

        Returns
        -------
        out : Array
            All the solutions, size: (noS,loS).
        """
        return self.__Sol

    def get_total_cost(self):
        """
        Get the temporal cost for all the solutions.

        Returns
        -------
        out : Array
            cost, size: (noS,1).
        """
        return self.__cost







