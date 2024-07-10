import json
import matplotlib.pyplot as plt


# Cargar datos desde archivos JSON
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


# Función para plotear fitness score y líneas verticales para generaciones
def plot_fitness_and_generations(fitness_scores, generation_intervals, cars, str=""):
    if str == "total":
        for i, interval in enumerate(generation_intervals):
            plt.axvline(x=interval['end'], color='r', linestyle='--')

        plt.axvline(x=generation_intervals[0]['end'], color='r', linestyle='--',
                    label='Generation Change')  # Solo se añade una vez a la leyenda
    plt.figure(figsize=(12, 6))
    for car_id, fitness_data in fitness_scores.items():
        frames = list(map(float, fitness_data.keys()))
        fitness_values = list(map(float, fitness_data.values()))
        if int(car_id) - 8820 not in cars:
            continue
        plt.plot(frames, fitness_values, label=f'{str} of car {int(car_id)-8820}')

    plt.xlabel('Time')
    plt.ylabel('Fitness Score')
    plt.title('Fitness Score over time by '+str)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    plt.show()


def plot_top_fitness_per_gen(top_fitness_per_gen):
    x_values = list(range(1, len(top_fitness_per_gen) + 1))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(x_values, top_fitness_per_gen, marker='o')
    plt.title('Top fitness per generation')
    plt.xlabel('Generation')
    plt.ylabel('Fitness score')
    plt.grid(True)
    plt.show()


# Cargar datos
fitness_scores = load_json('../assets/data_files/results/total_fitness_scores.json')
generation_intervals = load_json('../assets/data_files/results/generation_intervals.json')
top_fitness_per_gen = load_json('../assets/data_files/results/top_fitness.json')

# cars = [int(car) - 8820 for car in list(fitness_scores.keys())]
cars = [0, 1, 2, 3, 4]
start_time = [interval['start'] for interval in generation_intervals][-4]
end_time = [interval['end'] for interval in generation_intervals][-1]

# Plotear gráficos
plot_top_fitness_per_gen(top_fitness_per_gen)
# plot_fitness_and_generations(fitness_scores, generation_intervals, cars, "total")

