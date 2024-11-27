import matplotlib.pyplot as plt
import os

# Parameters for weight decay
initial_weight = 5.0  # Starting weight
decay_factor = 0.9  # Decay applied each cycle
decay_cycles = 12  # Simulate 12 decay cycles (e.g., 12 months)

# Apply decay across cycles and track weight over time
weights = [initial_weight]
for cycle in range(1, decay_cycles + 1):
    new_weight = weights[-1] * decay_factor
    weights.append(new_weight)

# Plotting the decay
plt.figure(figsize=(10, 6))
plt.plot(range(decay_cycles + 1), weights, marker='o', color='b', label='Weight Over Time')
plt.title("Weight Decay Visualization")
plt.xlabel("Decay Cycles (e.g., Months)")
plt.ylabel("Weight")
plt.ylim(0, initial_weight + 1)
plt.grid(True)
plt.legend()

# Ensure the directory exists
output_dir = "./diagrams"
os.makedirs(output_dir, exist_ok=True)

# Save the figure
plt.savefig(os.path.join(output_dir, "weight_decay.png"))
plt.show()
