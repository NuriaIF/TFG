import json
import matplotlib.pyplot as plt
import numpy as np

# Cargar los datos desde el archivo JSON
with open('../assets/data_files/results/fitness_scores.json', 'r') as f:
    fitness_scores = json.load(f)

# Convertir los datos a listas para graficar
generations = list(map(int, fitness_scores.keys()))
generations.sort()  # Asegurarse de que las generaciones estén en orden

# Calcular el fitness promedio para cada generación
average_fitness = [sum(fitness_scores[str(gen)]) / len(fitness_scores[str(gen)]) for gen in generations]

# Graficar los datos promedio
plt.figure(figsize=(10, 5))
plt.plot(generations, average_fitness, marker='o')
plt.xlabel('Generación')
plt.ylabel('Fitness Score Promedio')
plt.title('Evolución del Fitness Score a lo largo de las Generaciones')
plt.grid(True)
plt.show()

# Graficar valores individuales de fitness por generación
plt.figure(figsize=(10, 5))
for gen in generations:
    plt.scatter([gen] * len(fitness_scores[str(gen)]), fitness_scores[str(gen)], alpha=0.5)

plt.xlabel('Generación')
plt.ylabel('Fitness Score')
plt.title('Distribución de Fitness Scores a lo largo de las Generaciones')
plt.xticks(np.arange(min(generations), max(generations)+1, 5))
plt.grid(True)
plt.savefig('../doc/plots/2024-06-17_4_v2.png')
plt.show()
