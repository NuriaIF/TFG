import csv
import json

from src.game.ai.ai_info.interval import Interval


class DataCollector:
    def __init__(self):
        self.generation_intervals: list[Interval] = []
        self.generation_intervals.append(Interval(0, 0))
        self.top_fitness_per_generation = []

        self.total_fitness_per_car_through_time = {}
        self.fitness_checkpoint_per_car_through_time = {}
        self.fitness_speed_and_still_per_car_through_time = {}
        self.fitness_distance_to_checkpoint_per_car_through_time = {}

    def collect_fitness(self, agent, elapsed_time, evaluate=True, new_generation=False):
        if new_generation:
            self._update_fitness(agent.controlled_entity.entity_ID, elapsed_time + 0.001, 0, 0, 0, 0)
        if evaluate:
            fitness_score = agent.evaluate_fitness()
        else:
            fitness_score = agent.fitness_score
        fitness_from_checkpoints = agent.evaluate_checkpoint_fitness()
        fitness_from_speed_and_still = agent.evaluate_speed_fitness()
        fitness_distance_to_checkpoint = agent.evaluate_distance_to_checkpoint_fitness()

        self._update_fitness(agent.controlled_entity.entity_ID, elapsed_time, fitness_score,
                             fitness_from_checkpoints, fitness_from_speed_and_still, fitness_distance_to_checkpoint)

    def change_generation(self, elapsed_time, agents, current_generation):
        for agent in agents:
            self.collect_fitness(agent, elapsed_time, evaluate=False)
            self.collect_fitness(agent, elapsed_time, evaluate=False, new_generation=True)
        self.generation_intervals[-1].close(elapsed_time)
        self.generation_intervals.append(Interval(elapsed_time, current_generation))

    def save_data(self, elapsed_time):
        self._save_data_for_graphics()
        self._save_generation_intervals(elapsed_time)

    def _update_fitness(self, car_id, elapsed_time, fitness_score, fitness_from_checkpoints,
                        fitness_from_speed_and_still, fitness_distance_to_checkpoint):
        self._update_total_fitness(car_id, elapsed_time, fitness_score)
        self._update_checkpoint_fitness(car_id, elapsed_time, fitness_from_checkpoints)
        self._update_fitness_speed_and_still(car_id, elapsed_time, fitness_from_speed_and_still)
        self._update_distance_to_checkpoint(car_id, elapsed_time, fitness_distance_to_checkpoint)

    def _save_fitness_data(self, fitness_data_list, filename='fitness_data.csv'):
        # Ordenar la lista de datos por fitness_score en orden descendente
        sorted_fitness_data = sorted(fitness_data_list, key=lambda x: x['fitness_score'], reverse=True)

        # Guardar los datos en un fichero CSV
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Fitness Score', 'Car Position'])

            for data in sorted_fitness_data:
                writer.writerow([data['fitness_score'], data['tile']])

    def _update_total_fitness(self, car_id, elapsed_time, fitness):
        elapsed_time = round(elapsed_time, 3)
        if car_id not in self.total_fitness_per_car_through_time:
            self.total_fitness_per_car_through_time[car_id] = {}
        self.total_fitness_per_car_through_time[car_id][elapsed_time] = fitness

    # def _update_tile_fitness(self, car_id, elapsed_time, fitness):
    #     elapsed_time = round(elapsed_time, 3)
    #     if car_id not in self.fitness_tile_per_car_through_time:
    #         self.fitness_tile_per_car_through_time[car_id] = {}
    #     self.fitness_tile_per_car_through_time[car_id][elapsed_time] = fitness

    def _update_checkpoint_fitness(self, car_id, elapsed_time, fitness):
        elapsed_time = round(elapsed_time, 3)
        if car_id not in self.fitness_checkpoint_per_car_through_time:
            self.fitness_checkpoint_per_car_through_time[car_id] = {}
        self.fitness_checkpoint_per_car_through_time[car_id][elapsed_time] = fitness

    def _update_fitness_speed_and_still(self, car_id, elapsed_time, fitness):
        elapsed_time = round(elapsed_time, 3)
        if car_id not in self.fitness_speed_and_still_per_car_through_time:
            self.fitness_speed_and_still_per_car_through_time[car_id] = {}
        self.fitness_speed_and_still_per_car_through_time[car_id][elapsed_time] = fitness

    def _update_distance_to_checkpoint(self, car_id, elapsed_time, fitness):
        elapsed_time = round(elapsed_time, 3)
        if car_id not in self.fitness_distance_to_checkpoint_per_car_through_time:
            self.fitness_distance_to_checkpoint_per_car_through_time[car_id] = {}
        self.fitness_distance_to_checkpoint_per_car_through_time[car_id][elapsed_time] = fitness

    # def _update_angle_to_checkpoint(self, car_id, elapsed_time, fitness):
    #     elapsed_time = round(elapsed_time, 3)
    #     if car_id not in self.fitness_angle_to_checkpoint_per_car_through_time:
    #         self.fitness_angle_to_checkpoint_per_car_through_time[car_id] = {}
    #     self.fitness_angle_to_checkpoint_per_car_through_time[car_id][elapsed_time] = fitness

    # def _update_collision_fitness(self, car_id, elapsed_time, fitness):
    #     elapsed_time = round(elapsed_time, 3)
    #     if car_id not in self.fitness_collision_per_car_through_time:
    #         self.fitness_collision_per_car_through_time[car_id] = {}
    #     self.fitness_collision_per_car_through_time[car_id][elapsed_time] = fitness
    #
    # def _update_tile_per_car_through_time(self, cars, elapsed_time):
    #     for car in cars:
    #         car.car_knowledge.tile_intervals[-1].close(elapsed_time)
    #         if car.entity_ID not in self.tiles_per_elapsed_time_car:
    #             self.tiles_per_elapsed_time_car[car.entity_ID] = []
    #         for interval in car.car_knowledge.tile_intervals:
    #             self.tiles_per_elapsed_time_car[car.entity_ID].append(interval)

    # Guardar fitness total en un archivo JSON
    def _save_fitness_scores(self, filename='total_fitness_scores.json'):
        with open(filename, 'w') as file:
            json.dump(self.total_fitness_per_car_through_time, file, indent=4)

    # Guardar fitness por tipo de tile en un archivo JSON
    # def _save_tile_fitness_scores(self, filename='tile_fitness_scores.json'):
    #     with open(filename, 'w') as file:
    #         json.dump(self.fitness_tile_per_car_through_time, file, indent=4)

    def _save_checkpoint_fitness_scores(self, filename='checkpoint_fitness_scores.json'):
        with open(filename, 'w') as file:
            json.dump(self.fitness_checkpoint_per_car_through_time, file, indent=4)

    def save_speed_fitness_scores(self, filename='speed_fitness_scores.json'):
        with open(filename, 'w') as file:
            json.dump(self.fitness_speed_and_still_per_car_through_time, file, indent=4)

    def _save_fitness_distance_to_checkpoint(self, filename='distance_to_checkpoint_fitness_scores.json'):
        with open(filename, 'w') as file:
            json.dump(self.fitness_distance_to_checkpoint_per_car_through_time, file, indent=4)

    # def _save_fitness_angle_to_checkpoint(self, filename='angle_to_checkpoint_fitness_scores.json'):
    #     with open(filename, 'w') as file:
    #         json.dump(self.fitness_angle_to_checkpoint_per_car_through_time, file, indent=4)
    #
    # def _save_fitness_collision(self, filename='collision_fitness_scores.json'):
    #     with open(filename, 'w') as file:
    #         json.dump(self.fitness_collision_per_car_through_time, file, indent=4)

    # def _save_tiles_intervals_per_car(self, cars, elapsed_time, filename='tiles_intervals_per_car.json'):
    #     elapsed_time = round(elapsed_time, 3)
    #     self._update_tile_per_car_through_time(cars, elapsed_time)
    #     intervals_data = {}
    #     for car_id, intervals in self.tiles_per_elapsed_time_car.items():
    #         intervals_data[str(car_id)] = [{'start': interval.start, 'end': interval.end, 'value': interval.value.value}
    #                                        for interval in intervals]
    #
    #     with open(filename, 'w') as file:
    #         json.dump(intervals_data, file, indent=4)

    def _save_generation_intervals(self, elapsed_time, filename='generation_intervals.json'):
        elapsed_time = round(elapsed_time, 3)
        self.generation_intervals[-1].close(elapsed_time)
        intervals_data = [{'start': round(interval.start, 3), 'end': round(interval.end, 3)} for interval in
                          self.generation_intervals]
        with open(filename, 'w') as file:
            json.dump(intervals_data, file, indent=4)

    def _save_data_for_graphics(self):
        self._save_fitness_scores()
        # self._save_tile_fitness_scores()
        self._save_checkpoint_fitness_scores()
        self.save_speed_fitness_scores()
        self._save_fitness_distance_to_checkpoint()
        self.save_top_fitness()
        # self._save_fitness_angle_to_checkpoint()
        # self._save_fitness_collision()

    def add_top_fitness(self, top_fitness):
        self.top_fitness_per_generation.append(top_fitness)

    def save_top_fitness(self):
        with open('top_fitness.json', 'w') as f:
            json.dump(self.top_fitness_per_generation, f)
