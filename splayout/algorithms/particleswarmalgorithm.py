################################################################################################
## References: Nezamabadi-pour, Hossein & Rostami-Shahrbabaki, Majid & Farsangi,
## Malihe.(2008).Binary Particle Swarm Optimization: challenges and New Solutions.
## The Journal of Computer Society of Iran (CSI) On Computer Scienceand Engineering (JCSE),.
## 6. 21-32.
################################################################################################
import numpy as np
import math

class ParticleSwarmAlgorithm:
    """
    Particle Swarm Optimization Algorithm.
    Parameters
    ----------
    noS : Int
        Initial Number of solutions.
    loS : Int
        Length of a single solution.
    cost_function : func
        Cost function for evaluating a single solution, input: Array, size (loS,), output: Float, lower means better .
    max_iteration : Int
        Maximum of iterations (default: 500).
    callback_function : func
        Self-defined callback function that will be called after every iteration (default: None).
    v_max : Float or Int
        Maximum of particle velocity (default: 6).
    inertia_weight : Float
        Intertia weight for particles (default: 0.99).
    c_1 : Float or Int
        Learning rate for self-cognition (default: 2).
    c_2 : Float or Int
        Learning rate for social-cognition (default: 2).
    ratio_personal : Float
        Ratio for self-cognition (default: 0.2).
    ratio_global : Float
        Ratio for social-cognition (default: 0.8).
    """
    def __init__(self, param_constrains , noS, cost_function,  max_iteration = 50,callback_function=None , v_max = 0.5, inertia_weight = 1.0, c_1 = 2, c_2 = 2,
                 ratio_personal = 0.2, ratio_global = 0.8, ratio_random = True):
        self.param_constrains = param_constrains
        try:
            self.loS = len(self.param_constrains)
            for item in self.param_constrains:
                if len(item) == 2:
                    pass
                else:
                    raise Exception("The param_constrains should get the format that a list with sub-lists or tuples.")
        except:
            raise Exception("The param_constrains should get the format that a list with sub-lists or tuples.")
        self.max_iteration = max_iteration
        self.noS = noS
        self.v_max = v_max
        self.inertia_weight = inertia_weight
        self.c_1 = c_1
        self.c_2 = c_2
        self.cost_function = cost_function
        self.ratio_personal = ratio_personal
        self.ratio_global = ratio_global
        self.ratio_random = ratio_random
        self.__Sol = np.random.uniform(0,1,size=(self.noS,self.loS)) # Initialize the solutions
        self.__Best_Sol = self.__Sol.copy()
        self.__v = np.zeros((self.noS,self.loS))
        self.cg_curve = np.zeros((max_iteration))
        self.__cost = np.zeros(self.noS)
        self.__engine_flag = 0
        self.__iter = 0
        self.best_solution = np.zeros((1,self.loS))
        self.min_cost = math.inf
        self.engine_init()
        if (callback_function == None):
            def call_back():
                pass
            self.call_back = call_back
        else:
            self.call_back = callback_function

    def __solutions_to_params(self, solution):
        params = np.copy(solution)
        for i, citem in enumerate(self.param_constrains):
            params[i] = params[i]*(citem[1] - citem[0]) + citem[0]
        return params

    def engine_init(self):
        """
        Initialize the Binary Particle Swarm Optimization, evaluate the first iteration.
        """
        for i in range(0, self.__Sol.shape[0]):
            self.__cost[i] = self.cost_function(self.__solutions_to_params(self.__Sol[i, :]))
        self.min_cost = np.min(self.__cost, axis=0)
        __min_position = np.argmin(self.__cost, axis=0)
        self.best_solution = self.__Sol[__min_position, :].copy()

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

            for i in range(0, self.noS):
                if (self.ratio_random):
                    self.__v[i, :] = self.inertia_weight * self.__v[i, :] + self.c_1 * np.random.random() * (
                                self.__Best_Sol[i, :] - self.__Sol[i, :]) + \
                                     self.c_2 * np.random.random() * (self.best_solution - self.__Sol[i, :])
                else:
                    self.__v[i, :] = self.inertia_weight * self.__v[i, :] + self.c_1 * self.ratio_personal * (
                                self.__Best_Sol[i, :] - self.__Sol[i, :]) + \
                                     self.c_2 * self.ratio_global * (self.best_solution - self.__Sol[i, :])

                self.__v[i,:] = np.clip(self.__v[i,:], -self.v_max, self.v_max)

                self.__Sol[i,:] = self.__Sol[i,:] + self.__v[i,:]
                self.__Sol[i, :] = np.clip(self.__v[i,:], 0, 1)

                ## Calculate the cost
                new_cost = self.cost_function(self.__solutions_to_params(self.__Sol[i,:]))
                if (new_cost <= self.__cost[i]) :
                    self.__Best_Sol[i, :] = self.__Sol[i,:].copy()
                    self.__cost[i] = new_cost

                if new_cost <= self.min_cost:
                    self.best_solution = self.__Sol[i,:].copy()
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

    def get_best_params(self):
        """
        Get the temporal best solution.
        Returns
        -------
        out : Array
            Best solution.
        """
        return self.__solutions_to_params(self.best_solution)

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
