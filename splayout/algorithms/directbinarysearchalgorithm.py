#####################################################################################################
## Reference: Shen, B., Wang, P., Polson, R. et al. An integrated-nanophotonics polarization
##            beamsplitter with 2.4 × 2.4 μm2 footprint. Nature Photon 9, 378–382 (2015).
##            https://doi.org/10.1038/nphoton.2015.80
#####################################################################################################
import numpy as np

class DirectBinarySearchAlgorithm:
    """
    Direct Binary Search Algorithm.

    Parameters
    ----------
    loS : Int
        Length of a single solution.
    cost_function : func
        Cost function for evaluating a single solution, input: Array, size (loS,), output: Float, lower means better.
    max_iteration : Int
        Maximum of iterations (default: 500).
    callback_function : func
        Self-defined callback function that will be called after every solution evaluated (default: None).
    initial_solution : Array
        Initialize the solution, size: (noS,) (default: None, means random).
    """
    def __init__(self,loS,cost_function,max_iteration = 4,callback_function = None,initial_solution = None):
        self.loS = loS
        self.cost_function = cost_function
        self.max_iteration = max_iteration

        if (type(initial_solution) != type(None)):
            self.__Sol = initial_solution
        else:
            self.__Sol = np.random.randint(0, 2, size=(self.loS))

        self.cg_curve = np.zeros((max_iteration*self.loS))
        self.cost = np.zeros(1)
        self.__iter = 0
        self.best_solution = np.zeros(loS)
        self.__undisturbed = np.array(range(0,self.loS))

        if (callback_function == None):
            def call_back():
                pass
            self.call_back = call_back
        else:
            self.call_back = callback_function

        self.__engine_init()

    def __engine_init(self):
        self.cost = self.cost_function(self.__Sol)
        self.best_solution = self.__Sol.copy()
        self.__iter = 0

    def run(self):
        """
        Run the DBS engine.
        """
        while (self.__iter < self.max_iteration):
            self.__undisturbed = np.array(range(0, self.loS))
            for i in range(0,self.loS):
                temp_solution = self.__Sol.copy()
                perturbate_shuffle = np.random.randint(0,self.__undisturbed.size)
                perturbate_position = self.__undisturbed[perturbate_shuffle]
                if (i != self.loS -1):
                    self.__undisturbed = np.delete(self.__undisturbed,perturbate_shuffle)
                temp_solution[perturbate_position] = (temp_solution[perturbate_position] + 1)%2
                new_cost = self.cost_function(temp_solution)
                if (new_cost <= self.cost):
                    self.__Sol = temp_solution
                    self.cost = new_cost
                    self.best_solution = self.__Sol

                self.cg_curve[self.__iter * self.loS + i] = self.cost
                self.call_back()
            self.__iter += 1

    def get_remained_size(self):
        """
        Get the size of undisturbed positions.

        Returns
        -------
        out : Int
           Size of undisturbed positions.
        """
        return len(self.__undisturbed)

    def get_remained(self):
        """
        Get the undisturbed positions.

        Returns
        -------
        out : Array
           Undisturbed positions.
        """
        return self.__undisturbed

    def get_iteration_number(self):
        """
        Get the temporal iteration number.

        Returns
        -------
        out : Int
            Iteration number.
        """
        return self.__iter

    def get_cost(self):
        """
        Get the temporal cost.

        Returns
        -------
        out : Float
            cost.
        """
        return self.cost

    def get_best_solution(self):
        """
        Get the temporal best solution.

        Returns
        -------
        out : Array
            Best solution.
        """
        return self.best_solution






