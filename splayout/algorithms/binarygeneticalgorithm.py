##########################################################################
## Reference: (1)Houck, Christopher & Joines, Jeffrey & Kay, Michael. (1998).
## A Genetic Algorithm for Function Optimization: A MATLAB implementation.
## NCSUIE-TR-95-09. North Carolina State University, Raleigh, NC, USA. 22.
## (2) https://github.com/bigzhao/Binary-Genetic-Algorithm/
##########################################################################
import numpy as np
import math

class BinaryGeneticAlgorithm:
    """
    Binary Genetic Algorithm.
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
    p_crossover : Float
        Probability of crossover (default: 0.8).
    p_mutation : Float
        Probability of mutation (default: 0.2).
    """
    def __init__(self, noS , loS, cost_function , max_iteration = 500,callback_function=None ,p_crossover = 0.9, p_mutation = 0.005):
        self.max_iteration = max_iteration
        self.loS = loS
        self.p_crossover = p_crossover
        self.p_mutation = p_mutation
        self.cost_function = cost_function
        self.__Sol = np.random.randint(0,2,size=(noS,loS)) # Initialize the solutions
        self.cg_curve = np.zeros((max_iteration))
        self.__cost = np.zeros(noS) ## the cost of the population, the lower , the better (1 - FoM)
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
        Initialize the Binary Genetic Algorithm, evaluate the first iteration.
        """
        for i in range(0, self.__Sol.shape[0]):
            self.__cost[i] = self.cost_function(self.__Sol[i, :])
        self.min_cost = np.min(self.__cost, axis=0)
        self.__min_position = np.argmin(self.__cost, axis=0)
        self.best_solution = self.__Sol[self.__min_position, :].copy()

        ## Initialize the iteration
        self.__iter = 0
        self.__engine_flag = 1

    def rws(self):
        '''
        reference: https://github.com/bigzhao/Binary-Genetic-Algorithm/
        '''
        temp_cost = - self.__cost - (-self.__cost).min()
        sid = np.random.choice(np.arange(len(temp_cost)), size=2, replace=True,
               p=temp_cost/temp_cost.sum())
        return sid

    @staticmethod
    def crossover(sol_0, sol_1):
        assert (len(sol_0) == len(sol_1))
        point = np.random.randint(len(sol_0))
        new_sol_0 = np.hstack((sol_0[:point], sol_1[point:]))
        new_sol_1 = np.hstack((sol_1[:point], sol_0[point:]))

        return new_sol_0, new_sol_1

    @staticmethod
    def mutation(sol):
        point = np.random.randint(len(sol))
        sol[point] = 1 - sol[point]
        return sol

    def evaluate(self):
        for i in range(0, self.__Sol.shape[0]):
            self.__cost[i] = self.cost_function(self.__Sol[i, :])

        if np.min(self.__cost, axis=0) <= self.min_cost:
            self.min_cost = np.min(self.__cost, axis=0)
            self.__min_position = np.argmin(self.__cost, axis=0)
            self.best_solution = self.__Sol[self.__min_position, :].copy()

    def run(self):
        """
        Run the engine.
        """
        if(self.__engine_flag == 0):
            raise Exception("Engine has not been initialized, run: \"obj.engine_init()\" first")
        while (self.__iter < self.max_iteration):
            self.cg_curve[self.__iter] = self.min_cost
            self.__iter += 1

            ## get a new iteration
            temp_Sol = self.__Sol.copy()
            self.__Sol = []

            for i in range(0,int(temp_Sol.shape[0]/2)):
                id_0, id_1 = self.rws()
                sol_0, sol_1 = temp_Sol[id_0,:].copy(), temp_Sol[id_1,:].copy()
                if np.random.rand() < self.p_crossover:
                    sol_0, sol_1 = self.crossover(sol_0, sol_1)

                if np.random.rand() < self.p_mutation:
                    sol_0 = self.mutation(sol_0)
                    sol_1 = self.mutation(sol_1)

                self.__Sol.append(sol_0)
                self.__Sol.append(sol_1)

            self.__Sol = np.array(self.__Sol)
            self.evaluate()

            worst_index = np.argsort(self.__cost)[-1]
            self.__Sol[worst_index, :] = self.best_solution
            self.__cost[worst_index] = self.__min_position

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