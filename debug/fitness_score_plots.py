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
    # plt.figure(figsize=(12, 6))
    for car_id, fitness_data in fitness_scores.items():
        frames = list(map(float, fitness_data.keys()))
        fitness_values = list(map(float, fitness_data.values()))
        if int(car_id) - 8820 not in cars:
            continue
        plt.plot(frames, fitness_values, label=f'{str} of car {int(car_id)-8820}')

    plt.xlabel('Time')
    plt.ylabel('Fitness Score')
    plt.title('Fitness Score over time by '+str)
    # plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    # plt.show()


# Función para obtener el color según el tipo de tile
def get_color(tile_value):
    tile_colors = {
        1: 'black',  # TRACK
        2: 'red',    # CROSSWALK
        3: 'gray',   # SIDEWALK
        4: 'green',  # GRASS
        5: 'forestgreen',  # FOREST
        6: 'blue'    # SEA
    }
    return tile_colors.get(tile_value, 'black')

def plot_fitness_with_tile_colors(fitness_scores, tiles_intervals_per_car, generation_intervals, cars):
    plt.figure(figsize=(12, 6))
    for car_id, fitness_data in fitness_scores.items():
        frames = list(map(float, fitness_data.keys()))
        fitness_values = list(map(float, fitness_data.values()))
        if int(car_id) - 8820 not in cars:
            continue
        for interval in tiles_intervals_per_car[car_id]:
            start_frame = interval['start']
            end_frame = interval['end']
            tile_value = interval['value']
            color = get_color(tile_value)

            interval_frames = [frame for frame in frames if start_frame <= frame <= end_frame]
            interval_fitness_values = [fitness_data[str(frame)] for frame in interval_frames]

            if interval_frames:
                plt.plot(interval_frames, interval_fitness_values, color=color,
                         label=f'Car {int(car_id)-8820}' if start_frame == frames[0] else "")
        # plt.plot(frames, fitness_values, label=f'Car {int(car_id)-8820}')

    for i, interval in enumerate(generation_intervals):
        plt.axvline(x=interval['end'], color='r', linestyle='--')

    plt.axvline(x=generation_intervals[0]['end'], color='r', linestyle='--',
                label='Generation Change')  # Solo se añade una vez a la leyenda

    plt.xlabel('Frames')
    plt.ylabel('Fitness Score')
    plt.title('Fitness Score over Frames with Generation Changes')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    plt.show()

def plot_top_fitness_per_gen(top_fitness_per_gen):
    x_values = list(range(1, len(top_fitness_per_gen) + 1))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(x_values, top_fitness_per_gen, marker='o')
    plt.title('Data Plot')
    plt.xlabel('X values')
    plt.ylabel('Y values')
    plt.grid(True)
    plt.show()


# Cargar datos
fitness_scores = load_json('../total_fitness_scores.json')
generation_intervals = load_json('../generation_intervals.json')
tiles_intervals_per_car = load_json('../tiles_intervals_per_car.json')

tile_fitness_scores = load_json('../tile_fitness_scores.json')
checkpoint_fitness_scores = load_json('../checkpoint_fitness_scores.json')
speed_fitness_scores = load_json('../speed_fitness_scores.json')
distance_to_checkpoint_fitness_scores = load_json('../distance_to_checkpoint_fitness_scores.json')
angle_to_checkpoint_fitness_scores = load_json('../angle_to_checkpoint_fitness_scores.json')
collision_fitness_scores = load_json('../collision_fitness_scores.json')
top_fitness_per_gen = load_json('../top_fitness.json')

# cars = [int(car) - 8820 for car in list(fitness_scores.keys())]
cars = [0]
start_time = [interval['start'] for interval in generation_intervals][-4]
end_time = [interval['end'] for interval in generation_intervals][-1]

# Plotear gráficos
if False:
    plt.figure(figsize=(12, 6))
    plot_fitness_and_generations(fitness_scores, generation_intervals, cars, "total")
    # plot_fitness_with_tile_colors(tile_fitness_scores, tiles_intervals_per_car, generation_intervals, cars)

    # plot_fitness_and_generations(tile_fitness_scores, generation_intervals, cars, "tile type")
    plot_fitness_and_generations(checkpoint_fitness_scores, generation_intervals, cars, "checkpoints")
    plot_fitness_and_generations(speed_fitness_scores, generation_intervals, cars, "speed and still")
    plot_fitness_and_generations(distance_to_checkpoint_fitness_scores, generation_intervals, cars, "distance to checkpoint")
    # plot_fitness_and_generations(angle_to_checkpoint_fitness_scores, generation_intervals, cars, "angle to checkpoint")
    # plot_fitness_and_generations(collision_fitness_scores, generation_intervals, cars, "collisions")

plot_top_fitness_per_gen(top_fitness_per_gen)

# # plt.ylim(bottom=-400)
# plt.xlim(left=start_time, right=end_time)
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
# plt.show()
