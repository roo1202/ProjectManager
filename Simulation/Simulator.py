import multiprocessing

class Simulator():
    '''
    Clase de un Simulador por pasos de tiempo
    '''
    def __init__(self, class_environment) -> None:
        self.class_enviroment = class_environment

    def StartSimulation(self, stop_steps, *args, **kvargs):
        '''
        Función que comienza la simulación y genera un conjunto de salidas
        que son las variables observables.
        '''
        environment = self.class_enviroment(*args, **kvargs)
        step = 0
        while step < stop_steps and not environment.end():
            environment.next_step()
            step += 1

        return environment

    def StartManySimulations(self, count_simulations, stop_steps, *args, **kvargs):
        simulations = []
        for _ in range(count_simulations):
            output = self.StartSimulation(stop_steps, *args, **kvargs)
            simulations.append(output)
        return simulations

    def ThreadSimulations(self, conn, count_simulations, stop_steps, *args, **kvargs):
        results = self.StartManySimulations(count_simulations, stop_steps, *args, **kvargs)
        conn.send(results)

    def StartManySimulationsThreading(self, total_simulations, stop_steps, *args, **kvargs):
        simulations_per_thread = total_simulations // 4  # Dividimos las simulaciones en 4 procesos
        remaining_simulations = total_simulations % 4     # Simulaciones restantes

        simulations1 = []
        simulations2 = []
        simulations3 = []
        simulations4 = []

        parent_conn1, child_conn1 = multiprocessing.Pipe()
        thread1 = multiprocessing.Process(
            target=self.ThreadSimulations,
            args=(child_conn1, simulations_per_thread + (1 if remaining_simulations > 0 else 0), stop_steps, *args),
            kwargs=kvargs, daemon=True)

        parent_conn2, child_conn2 = multiprocessing.Pipe()
        thread2 = multiprocessing.Process(
            target=self.ThreadSimulations,
            args=(child_conn2, simulations_per_thread + (1 if remaining_simulations > 1 else 0), stop_steps, *args),
            kwargs=kvargs, daemon=True)

        parent_conn3, child_conn3 = multiprocessing.Pipe()
        thread3 = multiprocessing.Process(
            target=self.ThreadSimulations,
            args=(child_conn3, simulations_per_thread + (1 if remaining_simulations > 2 else 0), stop_steps, *args),
            kwargs=kvargs, daemon=True)

        parent_conn4, child_conn4 = multiprocessing.Pipe()
        thread4 = multiprocessing.Process(
            target=self.ThreadSimulations,
            args=(child_conn4, simulations_per_thread, stop_steps, *args),
            kwargs=kvargs, daemon=True)

        # Iniciar procesos
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()

        # Recibir resultados
        simulations1 = parent_conn1.recv()
        simulations2 = parent_conn2.recv()
        simulations3 = parent_conn3.recv()
        simulations4 = parent_conn4.recv()

        # Esperar a que los hilos terminen
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()

        # Devolver la lista combinada de todas las simulaciones
        return simulations1 + simulations2 + simulations3 + simulations4
