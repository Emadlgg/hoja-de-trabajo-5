import simpy
import random
import csv
import statistics
import matplotlib.pyplot as plt

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

class Programa:
    def __init__(self, env, RAM, cpu, numero_proceso):
        self.env = env
        self.RAM = RAM
        self.cpu = cpu
        self.numero_proceso = numero_proceso
        self.memoria = random.randint(1, 10)  # Define la cantidad de memoria requerida al inicio

    def pedir_memoria(self):
        yield self.RAM.get(self.memoria)  # Utiliza la cantidad de memoria definida al inicio

    def usar_cpu(self):
        yield self.env.timeout(1)

    def pedir_io(self):
        yield self.env.timeout(1)

    def run(self):
        tiempo_inicio = self.env.now
        yield self.env.process(self.pedir_memoria())
        with self.cpu.request() as req:
            yield req
            yield self.env.process(self.usar_cpu())
            while random.randint(1, 21) != 1:
                yield self.env.process(self.pedir_io())
        tiempo_final = self.env.now
        yield self.RAM.put(self.memoria)  # Devuelve la cantidad de memoria utilizada al contenedor
        return tiempo_inicio, tiempo_final

def simular_procesos(env, RAM, cpu, num_procesos):
    tiempos_ejecucion = []
    for i in range(num_procesos):
        numero_proceso = i + 1
        programa = Programa(env, RAM, cpu, numero_proceso)
        tiempo_inicio, tiempo_final = yield env.process(programa.run())
        tiempos_ejecucion.append((tiempo_inicio, tiempo_final))
        yield env.timeout(10)  # Intervalo entre procesos
    return tiempos_ejecucion

def simular(num_procesos, intervalo, procesadores):
    env = simpy.Environment()
    RAM = simpy.Container(env, init=100, capacity=100)
    cpu = simpy.Resource(env, capacity=procesadores)

    tiempos_ejecucion = yield env.process(simular_procesos(env, RAM, cpu, num_procesos))  # Asigna el valor de retorno de simular_procesos a tiempos_ejecucion

    tiempo_promedio = statistics.mean(tiempo_final - tiempo_inicio for tiempo_inicio, tiempo_final in tiempos_ejecucion)
    desviacion_estandar = statistics.stdev(tiempo_final - tiempo_inicio for tiempo_inicio, tiempo_final in tiempos_ejecucion)
    print(f"Tiempo promedio de ejecución: {tiempo_promedio}")
    print(f"Desviación estándar: {desviacion_estandar}")

    # Generar la gráfica
    plot_tiempo_vs_procesos(tiempos_ejecucion)

def plot_tiempo_vs_procesos(tiempos_ejecucion):
    num_procesos = range(1, len(tiempos_ejecucion) + 1)
    tiempo_total = [tiempo_final - tiempo_inicio for tiempo_inicio, tiempo_final in tiempos_ejecucion]
    tiempo_acumulado = [sum(tiempo_total[:i+1]) for i in range(len(tiempo_total))]

    plt.plot(num_procesos, tiempo_acumulado, marker='o')
    plt.title('Tiempo Total de Ejecución por Número de Procesos')
    plt.xlabel('Número de Procesos')
    plt.ylabel('Tiempo Total de Ejecución')
    plt.grid(True)
    plt.show()


num_procesos = [25, 50, 100, 150, 200]
intervalo = [10, 5, 1]
procesadores = [1, 6, 2]


for procesos in num_procesos:
    for interval in intervalo:
        for proc in procesadores:
            print(f"Simulación con {procesos} procesos, intervalo {interval}, procesadores {proc}")
            simular(procesos, interval, proc)
            

