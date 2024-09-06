import numpy as np
import random
import sys
import warnings
import random
import copy
import pandas as pd
import time
from datetime import datetime
from Tasks.GeneticAlgorithm.Tasks_combination import Tasks_combination
from Tasks.GeneticAlgorithm.Crossover_heuristics import crossing_by_cut_off_point

import warnings
warnings.filterwarnings('ignore')

class Population:
    """
    Esta clase crea una población de n individuos(tareas_combination).

    Parameters
    ----------
    n_individuos :`int`
        número de individuos de la población.

    verbose : `bool`, optional
        mostrar información del proceso por pantalla. (default ``False``)

    Attributes
    ----------
    individuos : `list`
        lista con todos los individuos de la población en su estado actual.
    
    n_individuos :`int`
        número de individuos de la población.

    n_variables : `int`
        número de variables que definen a cada individuo.

    mejor_individuo : `object individuo`
        mejor individuo de la población en su estado actual.

    mejor_fitness : `float`
        fitness del mejor individuo de la población en su estado actual.

    mejor_function_value : `float`
        valor de la función objetivo del mejor individuo de la población en su
        estado actual.

    mejor_individuo_variables : `numpy.ndarray`
        valor de las variables del mejor individuo de la población en su estado
        actual.

    historico_individuos : `list`
        lista con la información de todos los individuos en cada una de las 
        generaciones que ha tenido la población.

    historico_mejor_individuo_variables : `list`
        lista con valor de las variables del mejor individuo en cada una de las 
        generaciones que ha tenido la población.

    historico_mejor_fitness : `list`
        lista con el mejor fitness en cada una de las generaciones que ha tenido
        la población.

    historico_mejor_function_value : `list`
        lista con valor de la función objetivo del mejor individuo en cada una
        de las generaciones que ha tenido la población.

    diferencia_abs : `list`
        diferencia absoluta entre el mejor fitness de generaciones consecutivas.

    resultados_df : `pandas.core.frame.DataFrame`
        dataframe con la información del mejor fitness y valor de las variables
        encontrado en cada generación, así como la diferencia respecto a la 
        generación anterior.

    fitness_optimo : `float`
        mejor fitness encontrado tras el proceso de optimización.

    function_value_optimo : `float`
        valor de la función objetivo encontrado tras el proceso de optimización.

    variable_values_optimo : `numpy.narray`
        valor de las variables con el que se ha conseguido el mejor fitness tras
        el proceso de optimización.

    optimizado : `bool`
        si la población ha sido optimizada.

    iter_optimizacion : `int`
        número de iteraciones de optimización (generaciones).



    """

    def __init__(self, n_individuals, tasks, verbose=False):

        # Number of individuals in the population
        self.n_individuals = n_individuals
        # Number of variables for each individual
        self.n_variables = len(tasks)
        # Tasks to combine for the individuals
        self.tasks = tasks
        # List of the individuals in the population
        self.individuals = []
        # Flag to know if the population has been optimized
        self.optimized = False
        # Number of optimization iterations carried out
        self.optimization_iter = None
        # Best individual in the population
        self.best_individual = None
        # Fitness of the best individual in the population (the one with the highest fitness)
        self.best_fitness = None
        # Objective function value of the best individual in the population
        self.best_function_value = None
        # Variable values of the best individual in the population
        self.best_variable_values = None
        # Information of all the individuals in the population at each generation
        self.individuals_history = []
        # Variable values of the best individual in each generation
        self.best_variable_values_history = []
        # Fitness of the best individual in each generation
        self.best_fitness_history = []
        # Objective function value of the best individual in each generation
        self.best_function_value_history = []
        # Absolute difference between the best fitness of consecutive generations
        self.absolute_difference = []
        # DataFrame with the information of the best fitness and variable values found
        # in each generation, as well as the difference from the previous generation.
        self.results_df = None
        # Fitness of the best individual across all generations
        self.optimal_fitness = None
        # Variable values of the best individual across all generations
        self.optimal_variable_values = None
        # Objective function value of the best individual across all generations
        self.optimal_function_value = None

        # INDIVIDUALS OF THE POPULATION ARE CREATED AND STORED
        # ----------------------------------------------------------------------
        for i in np.arange(n_individuals):
            individual_i = Tasks_combination(
                            n_variables = self.n_variables,
                            tasks = tasks,
                            verbose = verbose
                        )
            self.individuals.append(individual_i)

        # PROCESS INFORMATION (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("----------------")
            print("Population created")
            print("----------------")
            print("Number of individuals: " + str(self.n_individuals))


    def __repr__(self):
        text = "============================" \
            + "\n" \
            + "         Population" \
            + "\n" \
            + "============================" \
            + "\n" \
            + "Number of individuals: " + str(self.n_individuals) \
            + "\n" \
            + "Optimized: " + str(self.optimized) \
            + "\n" \
            + "Optimization iterations (generations): " \
                    + str(self.optimization_iter) \
            + "\n" \
            + "\n" \
            + "Best individual information:" \
            + "\n" \
            + "----------------------------" \
            + "\n" \
            + "Variable values: " + str(self.best_variable_values) \
            + "\n" \
            + "Fitness: " + str(self.best_fitness) \
            + "\n" \
            + "\n" \
            + "Results after optimization:" \
            + "\n" \
            + "--------------------------" \
            + "\n" \
            + "Optimal variable values: " + str(self.optimal_variable_values) \
            + "\n" \
            + "Optimal objective function value: " + str(self.optimal_function_value) \
            + "\n" \
            + "Optimal fitness: " + str(self.optimal_fitness)
            
        return text


    def show_individuals(self, n=None):
        """
        This method displays the information of the first n individuals 
        in the population.

        Parameters
        ----------
        n : `int`
            Number of individuals to display. If not specified 
            (default is ``None``), all are displayed. If the value is greater
            than `self.n_individuals`, all are displayed.
        """

        if n is None or n > self.n_individuals:
            n = self.n_individuals
        
        for i in np.arange(n):
            print(self.individuals[i])
        return None


    def evaluate_population(self, objective_function, optimization, verbose=False):
        """
        This method calculates the fitness of all individuals in the population,
        updates their values, and identifies the best one.

        Parameters
        ----------
        objective_function : `function`
            The function to be optimized.

        optimization : {"maximize" or "ze"}
            Whether to maximize or minimize the function.

        verbose : `bool`, optional
            Display process information on the screen. (default is ``False``)
        """

        # EVALUATE EACH INDIVIDUAL IN THE POPULATION
        # ----------------------------------------------------------------------
        # BEST INDIVIDUAL IN THE POPULATION
        # ----------------------------------------------------------------------
        # The best individual in the entire population is identified, 
        # the one with the highest fitness.
        # Initially, select the first individual as the best.
        self.best_individual = copy.deepcopy(self.individuals[0])
        if optimization == "maximize" : self.best_individual.fitness = - sys.maxsize - 1
        else : self.best_individual.fitness = sys.maxsize
        for i in np.arange(self.n_individuals):
            self.individuals[i].calculate_fitness(
                objective_function = objective_function,
                optimization       = optimization,
                verbose            = verbose
            )
            if self.individuals[i].fitness > self.best_individual.fitness:
                self.best_individual = copy.deepcopy(self.individuals[i])
            

        # Extract the information of the best individual in the population.
        self.best_fitness = self.best_individual.fitness
        self.best_variable_values = self.best_individual.variable_values
        self.best_function_value = self.best_individual.function_value
        
        # PROCESS INFORMATION (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("------------------")
            print("Population evaluated")
            print("------------------")
            print("Best fitness found: " + str(self.best_fitness))
            print("Objective function value: " + str(self.best_function_value))
            print("Best variable values found: " + str(self.best_variable_values))
            print("")

    def crossover_individuals(self, parent_1, parent_2, verbose=False, method="smart_cut"):
        """
        This method generates a new individual from two parent individuals
        using the uniform crossover method.

        Parameters
        ----------
        parent_1 : `int`
            Index of the individual in the population to be used as
            parent 1 for crossover.

        parent_2 : `int`
            Index of the individual in the population to be used as
            parent 2 for crossover.
        
        verbose : `bool`, optional
            Display process information on the screen. (default ``False``)

        Raises
        ------
        Exception
            If the indices parent_1 or parent_2 are not valid indices.

        Returns
        ------
        offspring : `Individual`
            New individual generated by crossover of two parents.

        
        Notes
        -----
        The goal of crossover is to generate, from existing individuals 
        (parents), new individuals (offspring) that combine the characteristics 
        of the parents. This is one of the points in the algorithm where various 
        strategies can be applied. Three of the most common are:

        - Single-point crossover: A position is randomly selected as the 
        crossover point. Each parent individual is split into two parts and 
        the halves are swapped. As a result of this process, two new individuals 
        are generated from each crossover.

        - Multi-point crossover: Multiple positions are randomly selected 
        as crossover points. Each parent individual is split at the crossover 
        points, and the parts are swapped. As a result of this process, two 
        new individuals are generated from each crossover.

        - Uniform crossover: The value of each position in the new individual 
        is taken from one of the two parents. Generally, the probability that 
        the value comes from each parent is the same, although it could be, 
        for example, conditioned on the fitness of each parent. Unlike the 
        previous strategies, this method generates only one offspring per crossover.

        """

        # INITIAL CHECKS: EXCEPTIONS AND WARNINGS
        # ----------------------------------------------------------------------
        if parent_1 not in np.arange(self.n_individuals):
            raise Exception(
                "The index of parent_1 must be a value between 0 and " +
                "the number of individuals in the population."
            )
        if parent_2 not in np.arange(self.n_individuals):
            raise Exception(
                "The index of parent_2 must be a value between 0 and " +
                "the number of individuals in the population."
            )

        # CREATION OF THE OFFSPRING
        # ----------------------------------------------------------------------
        # Extract the parents according to the specified indices.
        parent_1 = self.individuals[parent_1]
        parent_2 = self.individuals[parent_2]
        
        # Clone one of the parents to use as a template for the new individual.
        offspring = copy.deepcopy(parent_1)
        offspring.variable_values = np.repeat(None, offspring.n_variables)
        offspring.fitness = None

        # # Randomly select the positions inherited from parent_1 and parent_2.
        # inheritance_parent_1 = np.random.choice(
        #                         a       = [True, False],
        #                         size    = offspring.n_variables,
        #                         p       = [0.5, 0.5],
        #                         replace = True
        #                     )

        # # Transfer the values to the new individual.
        # for index, value in enumerate(inheritance_parent_1):
        #     if value:
        #         offspring.variable_values[index] = parent_1.variable_values[index]
        #     else :
        #         offspring.variable_values[index] = parent_2.variable_values[index]

        offspring.variable_values = crossing_by_cut_off_point(parent_1.variable_values, parent_2.variable_values, mode="inteligente")

        # Create a deepcopy to make the new individual independent of the parents.
        # This prevents issues if the offspring is later mutated.
        offspring = copy.deepcopy(offspring)

        # PROCESS INFORMATION (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("------------------------------------")
            print("Crossover completed: offspring created")
            print("------------------------------------")
            print("Variable values: " + str(offspring.variable_values))
            print("")
        return offspring

    def select_individual(self, n, return_indices=True,
                        selection_method="tournament", verbose=False):
        """
        This method selects the indices of n individuals from a population,
        where the probability of selection is related to the fitness of each 
        individual. If the argument `return_indices=False`, instead of the 
        indices, a copy of the selected individuals is returned.

        Parameters
        ----------
        n : `int`
            Number of individuals to be selected from the population.

        return_indices : `bool`, optional
            When True, the indices of the selected individuals are returned.
            When False, a list containing copies of the selected individuals is returned. 
            (default ``True``)

        selection_method : {"roulette", "rank", "tournament"}
            Selection method, see notes for more information. (default `tournament`)

        verbose : `bool`, optional
            Display process information on the screen. (default ``False``)
        
        Raises
        ------
        Exception
            If the `selection_method` argument is not 'roulette', 'rank', or 'tournament'.

        Returns
        -------
        indices : `numpy.ndarray`
            Indices of the selected individuals (if `return_indices=True`).

        individuals : `list`
            List of selected individuals (if `return_indices=False`).

        
        Notes
        -----
        The way individuals are selected for crossover differs across various 
        implementations of genetic algorithms. Generally, all methods tend to 
        favor the selection of individuals with higher fitness. Some of the most 
        common strategies are:

        - Roulette method: The probability that an individual is selected 
        is proportional to its relative fitness, i.e., its fitness divided 
        by the sum of the fitness of all individuals in the population. 
        If an individual's fitness is twice that of another, its probability 
        of being selected is also twice as high. This method has issues if 
        the fitness of a few individuals is much higher (by several orders 
        of magnitude) than the rest, as they will be repeatedly selected, and 
        most of the next generation's individuals will be "children" of the 
        same "parents" (low variation).

        - Rank method: The probability of selection of an individual is inversely 
        proportional to its position after sorting all individuals from highest 
        to lowest fitness. This method is less aggressive than the roulette method 
        when the difference between the highest fitness is several orders of 
        magnitude greater than the rest.

        - Tournament selection: Two pairs of individuals are randomly selected 
        from the population (all with the same probability). The one with the 
        higher fitness is selected from each pair. Finally, the two finalists 
        are compared, and the one with the higher fitness is selected. This 
        method tends to generate a more balanced selection probability distribution 
        than the previous two methods.

        - Truncated selection: Random selections of individuals are made, 
        having first discarded the n individuals with the lowest fitness 
        from the population.

        """

        # INITIAL CHECKS: EXCEPTIONS AND WARNINGS
        # ----------------------------------------------------------------------
        if selection_method not in ["roulette", "rank", "tournament"]:
            raise Exception(
                "The selection method must be 'roulette', 'rank', or 'tournament'"
            )

        # INDIVIDUAL SELECTION
        # ----------------------------------------------------------------------
        # Create an array with the fitness of each individual in the population.
        fitness_array = np.repeat(None, self.n_individuals)
        for i in np.arange(self.n_individuals):
            fitness_array[i] = copy.copy(self.individuals[i].fitness)
        
        # Calculate the selection probability of each individual based on fitness.
        if selection_method == "roulette":
            selection_probability = fitness_array / np.sum(fitness_array)
            selected_indices = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = n,
                                p       = list(selection_probability),
                                replace = True
                            )
        elif selection_method == "rank":
            # The probability with this method is inversely proportional to the 
            # position after sorting individuals from lowest to highest fitness.
            order = np.flip(np.argsort(a=fitness_array) + 1)
            ranks = np.argsort(order) + 1
            selection_probability = 1 / ranks
            selection_probability = selection_probability / np.sum(selection_probability)
            selected_indices = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = n,
                                p       = list(selection_probability),
                                replace = True
                            )
        elif selection_method == "tournament":
            selected_indices = np.repeat(None, n)
            for i in np.arange(n):
                # Randomly select two pairs of individuals.
                candidates_a = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = 2,
                                replace = False
                            )
                candidates_b = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = 2,
                                replace = False
                            )
                # Select the one with the higher fitness from each pair.
                if fitness_array[candidates_a[0]] > fitness_array[candidates_a[1]]:
                    winner_a = candidates_a[0]
                else:
                    winner_a = candidates_a[1]

                if fitness_array[candidates_b[0]] > fitness_array[candidates_b[1]]:
                    winner_b = candidates_b[0]
                else:
                    winner_b = candidates_b[1]

                # Compare the two winners from each pair.
                if fitness_array[winner_a] > fitness_array[winner_b]:
                    final_index = winner_a
                else:
                    final_index = winner_b
                
                selected_indices[i] = final_index

        # PROCESS INFORMATION (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("----------------------")
            print("Individual selected")
            print("----------------------")
            print("Selection method: " + selection_method)
            print("")

        if return_indices:
            return selected_indices
        else:
            if n == 1:
                return copy.deepcopy(self.individuals[int(selected_indices)])
            if n > 1:
                return [
                    copy.deepcopy(self.individuals[i]) for i in selected_indices
                ]

    def create_new_generation(self, selection_method="tournament",
                            elitism=0.1, mutation_prob=0.01,
                            distribution="uniform",
                            mean_distribution=1, sd_distribution=1,
                            min_distribution=-1, max_distribution=1,
                            verbose=False, verbose_selection=False,
                            verbose_crossover=False, verbose_mutation=False):
        """
        This method evolves the population to a new generation.

        Parameters
        ----------
        selection_method : {"roulette", "rank", "tournament"}
            Selection method, see notes for more information. (default `tournament`)

        elitism : `float`, optional
            Percentage of the best individuals in the current population that are 
            directly passed to the next generation. This ensures that the next 
            generation is never worse. (default `0.1`)

        mutation_prob : `float`, optional
            Probability that each position in the individual will mutate.
            (default 0.01)

        distribution : {"normal", "uniform", "random"}, optional
            Distribution from which to obtain the mutation factor.
            (default "uniform")

        mean_distribution : `float`, optional
            Mean of the distribution if `distribution = "normal"` is selected.
            (default 1)

        sd_distribution : `float`, optional
            Standard deviation of the distribution if `distribution = "normal"`
            is selected. (default 1)

        min_distribution : `float`, optional
            Minimum of the distribution if `distribution = "uniform"` is selected.
            (default -1)

        max_distribution : `float`, optional
            Maximum of the distribution if `distribution = "uniform"` is selected.
            (default +1)

        verbose : `bool`, optional
            Display process information on the screen. (default ``False``)
        
        verbose_selection : `bool`, optional
            Display information about each selection on the screen.
            (default ``False``)

        verbose_crossover : `bool`, optional
            Display information about each crossover on the screen.
            (default ``False``)

        verbose_mutation : `bool`, optional
            Display information about each mutation on the screen.
            (default ``False``)

        """

        # List to store the individuals of the new generation.
        new_individuals = []

        # ELITISM
        # ----------------------------------------------------------------------
        if elitism > 0:
            # Number of individuals that are directly passed to the next generation.
            n_elitism = int(np.ceil(self.n_individuals * elitism))

            # Identify the n_elitism individuals with the highest fitness (elite).
            fitness_array = np.repeat(None, self.n_individuals)
            for i in np.arange(self.n_individuals):
                fitness_array[i] = copy.copy(self.individuals[i].fitness)
            rank = np.flip(np.argsort(fitness_array))
            elite = [copy.deepcopy(self.individuals[i]) for i in rank[:n_elitism]]
            # Add elite individuals to the list of new individuals.
            new_individuals = new_individuals + elite
        else:
            n_elitism = 0
            
        # CREATION OF NEW INDIVIDUALS THROUGH CROSSOVER
        # ----------------------------------------------------------------------
        for i in np.arange(self.n_individuals - n_elitism):
            # Select parents
            parent_indices = self.select_individual(
                                n                = 2,
                                return_indices   = True,
                                selection_method = selection_method,
                                verbose          = verbose_selection
                            )
            # Crossover parents to obtain offspring
            offspring = self.crossover_individuals(
                            parent_1 = parent_indices[0],
                            parent_2 = parent_indices[1],
                            verbose  = verbose_crossover
                        )
            # Mutate the offspring
            offspring.mutate(
                mutation_prob     = mutation_prob,
                distribution      = distribution,
                min_distribution  = min_distribution,
                max_distribution  = max_distribution,
                verbose           = verbose_mutation
            )
            # Add offspring to the list of new individuals. 
            new_individuals = new_individuals + [offspring]

        # UPDATE POPULATION INFORMATION
        # ----------------------------------------------------------------------
        self.individuals = copy.deepcopy(new_individuals)
        self.best_individual = None
        self.best_fitness = None
        self.best_variable_values = None
        self.best_function_value = None
        
        # PROCESS INFORMATION (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("-----------------------")
            print("New generation created")
            print("-----------------------")
            print("Selection method: " + selection_method)
            print("Elitism: " + str(elitism))
            print("Number of elite individuals: " + str(n_elitism))
            print("Number of new individuals: " + str(self.n_individuals - n_elitism))
            print("")

    def optimize(self, objective_function, optimization, n_generations=50,
                selection_method="tournament", elitism=0.1, mutation_prob=0.01,
                distribution="uniform", mean_distribution=1,
                sd_distribution=1, min_distribution=-1, max_distribution=1,
                early_stopping=False, stopping_rounds=None,
                stopping_tolerance=None, verbose=False,
                verbose_new_generation=False,
                verbose_selection=False, verbose_crossover=False,
                verbose_mutation=False, verbose_evaluation=False):
        """
        This method performs the optimization process for a population.

        Parameters
        ----------
        objective_function : `function`
            The function to be optimized.

        optimization : {"maximize" or "minimize"}
            Whether to maximize or minimize the function.

        n_generations : `int`, optional
            Number of optimization generations. (default ``50``)

        selection_method : {"roulette", "rank", "tournament"}
            Selection method, see notes for more information. (default `tournament`)

        elitism : `float`, optional
            Percentage of the best individuals in the current population that are
            directly passed to the next generation. This ensures that the next 
            generation is never worse. (default `0.1`)

        mutation_prob : `float`, optional
            Probability that each position in the individual will mutate.
            (default 0.01)

        distribution : {"normal", "uniform", "random"}, optional
            Distribution from which to obtain the mutation factor.
            (default "uniform")

        mean_distribution : `float`, optional
            Mean of the distribution if `distribution = "normal"` is selected.
            (default 1)

        sd_distribution : `float`, optional
            Standard deviation of the distribution if `distribution = "normal"`
            is selected. (default 1)

        min_distribution : `float`, optional
            Minimum of the distribution if `distribution = "uniform"` is selected.
            (default -1)

        max_distribution : `float`, optional
            Maximum of the distribution if `distribution = "uniform"` is selected.
            (default +1)
        
        early_stopping : `bool`, optional
            If during the last `stopping_rounds` generations the absolute difference
            between the best individuals is not greater than the value of 
            `stopping_tolerance`, the algorithm stops and no new generations are 
            created. (default ``False``)

        stopping_rounds : `int`, optional
            Number of consecutive generations without minimal improvement needed to
            trigger early stopping. (default ``None``)

        stopping_tolerance : `float` or `int`, optional
            Minimum difference value between consecutive generations to consider 
            a change. (default ``None``)

        verbose : `bool`, optional
            Display process information on the screen. (default ``False``)
        
        verbose_new_generation : `bool`, optional
            Display information for each new generation on the screen.
            (default ``False``)

        verbose_selection : `bool`, optional
            Display information for each selection on the screen.
            (default ``False``)

        verbose_crossover : `bool`, optional
            Display information for each crossover on the screen.
            (default ``False``)

        verbose_mutation : `bool`, optional
            Display information for each mutation on the screen.
            (default ``False``)
        
        Raises
        ------
        Exception
            If `early_stopping = True` and the arguments `stopping_rounds` or 
            `stopping_tolerance` are ``None``.

        Exception
            If the `selection_method` argument is not 'roulette', 'rank', or 'tournament'.

        Exception
            If the `optimization` argument is not 'maximize' or 'minimize'.
        """

        # INITIAL CHECKS: EXCEPTIONS AND WARNINGS
        # ----------------------------------------------------------------------
        # If early stopping is enabled, the stopping_rounds and stopping_tolerance
        # arguments must be specified.
        if early_stopping and (stopping_rounds is None or stopping_tolerance is None):
            raise Exception(
                "To enable early stopping, a value for stopping_rounds and " \
                + "stopping_tolerance must be provided."
            )

        # ITERATIONS (GENERATIONS)
        # ----------------------------------------------------------------------
        start = time.time()

        for i in np.arange(n_generations):
            if verbose:
                print("-------------")
                print("Generation: " + str(i))
                print("-------------")
            
            # EVALUATE POPULATION INDIVIDUALS
            # ------------------------------------------------------------------
            self.evaluate_population(
                objective_function = objective_function,
                optimization       = optimization,
                verbose            = verbose_evaluation
            )

            # STORE GENERATION INFORMATION IN HISTORY
            # ------------------------------------------------------------------
            self.individuals_history.append(copy.deepcopy(self.individuals))
            self.best_fitness_history.append(copy.deepcopy(self.best_fitness))
            self.best_variable_values_history.append(
                copy.deepcopy(self.best_variable_values)
            )
            self.best_function_value_history.append(
                copy.deepcopy(self.best_function_value)
            )

            # CALCULATE THE ABSOLUTE DIFFERENCE COMPARED TO THE PREVIOUS GENERATION
            # ------------------------------------------------------------------
            # The difference can only be calculated starting from the second generation.
            if i == 0:
                self.absolute_difference.append(None)
            else:
                difference = abs(self.best_fitness_history[i] \
                                - self.best_fitness_history[i - 1])
                self.absolute_difference.append(difference)

            # STOPPING CRITERION
            # ------------------------------------------------------------------
            # If during the last n generations, the absolute difference between 
            # the best individuals is not greater than the stopping_tolerance value, 
            # the algorithm stops and no new generations are created.
            if early_stopping and i > stopping_rounds:
                last_n = np.array(self.absolute_difference[-stopping_rounds:])
                if all(last_n < stopping_tolerance):
                    print("Algorithm stopped at generation " 
                        + str(i) \
                        + " due to lack of minimum absolute change of " \
                        + str(stopping_tolerance) \
                        + " during " \
                        + str(stopping_rounds) \
                        + " consecutive generations.")
                    break
            
            # CREATE A NEW GENERATION
            # ------------------------------------------------------------------         
            self.create_new_generation(
                selection_method   = selection_method,
                elitism            = elitism,
                mutation_prob      = mutation_prob,
                distribution       = distribution,
                verbose            = verbose_new_generation,
                verbose_selection  = verbose_selection,
                verbose_crossover  = verbose_crossover,
                verbose_mutation   = verbose_mutation
            )

        end = time.time()
        self.optimized = True
        self.optimization_iter = i
        
        # IDENTIFY THE BEST INDIVIDUAL OF THE ENTIRE PROCESS
        # ----------------------------------------------------------------------
        optimal_index  = np.argmax(np.array(self.best_fitness_history))
        self.optimal_fitness  = self.best_fitness_history[optimal_index]
        self.optimal_function_value = self.best_function_value_history[optimal_index]
        self.optimal_variable_values = self.best_variable_values_history[optimal_index]
        
        # CREATE A DATAFRAME WITH THE RESULTS
        # ----------------------------------------------------------------------
        self.results_df = pd.DataFrame(
            {
            "best_fitness"         : self.best_fitness_history,
            "best_function_value"  : self.best_fitness_history,
            "best_variable_values" : self.best_variable_values_history,
            "absolute_difference"  : self.absolute_difference
            }
        )
        self.results_df["generation"] = self.results_df.index
        
        print("-------------------------------------------")
        print("Optimization completed " \
            + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("-------------------------------------------")
        print("Optimization duration: " + str(end - start))
        print("Number of generations: " + str(self.optimization_iter))
        print("Optimal variable values: " + str(self.optimal_variable_values))
        print("Objective function value: " + str(self.optimal_function_value))
        print("")
