print("Testing sensor logic...")

test_distances = [1.5, 3.0, 0.8, 5.0, 1.9]
occupied_threshold = 2.0

for distance in test_distances:
    is_occupied = distance < occupied_threshold
    status = "PRESENT" if is_occupied else "EMPTY"
    print(f"Distance: {distance}cm -> {status}")

print("Sensor logic test complete")