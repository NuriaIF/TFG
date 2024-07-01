import csv


def load_data_from_csv(filename):
    data = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        for row in reader:
            normalized_velocity = float(row[0])
            normalized_relative_position_x = float(row[1])
            normalized_relative_position_y = float(row[2])
            fov_tiles = [float(val) for val in row[3:-6]]
            actions = [float(val) for val in row[-6:]]
            inputs = [normalized_velocity,
                      normalized_relative_position_x, normalized_relative_position_y]
            inputs.extend(fov_tiles)
            data.append([inputs, actions])
    return data


def prepare_data_for_training(data):
    inputs = []
    labels = []
    for d in data:
        input_data = d[0]  # Primer elemento es la lista de características de entrada
        actions = d[1]     # Segundo elemento es la lista de acciones
        inputs.append(input_data)
        labels.append(actions)
    return inputs, labels
