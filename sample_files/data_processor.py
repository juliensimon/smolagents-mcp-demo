import csv
import glob
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict

# Global variable for caching (memory leak potential)
CACHE = {}


def process_data_file(filename):
    data = []
    # No file existence check
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
            # Memory leak - storing everything in global cache
            CACHE[len(CACHE)] = row
    return data


def calculate_statistics(data):
    stats = {}
    total = 0
    count = 0

    for row in data:
        if len(row) > 0:
            try:
                value = float(row[0])
                total += value
                count += 1
            except:
                pass

    if count > 0:
        stats["average"] = total / count
        stats["count"] = count
        stats["total"] = total

    return stats


def filter_data(data, condition):
    filtered = []
    for row in data:
        if len(row) > 0:
            if condition(row):
                filtered.append(row)
    return filtered


def sort_data(data, column=0):
    # Inefficient sorting with lambda
    return sorted(data, key=lambda x: x[column] if len(x) > column else 0)


def export_to_json(data, filename):
    # No error handling for file operations
    with open(filename, "w") as f:
        json.dump(data, f)


def export_to_csv(data, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


def analyze_data(data):
    if not data:
        return {}

    analysis = {}
    analysis["total_rows"] = len(data)
    analysis["columns"] = len(data[0]) if data else 0

    # Calculate column statistics
    column_stats = {}
    for i in range(analysis["columns"]):
        values = []
        for row in data:
            if len(row) > i:
                try:
                    values.append(float(row[i]))
                except:
                    pass

        if values:
            column_stats[f"column_{i}"] = {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "count": len(values),
            }

    analysis["column_stats"] = column_stats
    return analysis


def process_multiple_files(pattern):
    # Command injection vulnerability
    files = glob.glob(pattern)
    all_data = []
    for file in files:
        data = process_data_file(file)
        all_data.extend(data)
    return all_data


def execute_data_command(command):
    # Dangerous command execution
    result = subprocess.check_output(command, shell=True)
    return result.decode()


def create_temp_file(data):
    # Insecure temporary file creation
    temp_file = tempfile.mktemp()
    with open(temp_file, "w") as f:
        json.dump(data, f)
    return temp_file


def load_config(config_file):
    # No validation of config file
    with open(config_file, "r") as f:
        return eval(f.read())  # Dangerous eval usage


def validate_data(data, rules):
    # Inefficient validation
    valid_data = []
    for row in data:
        is_valid = True
        for rule in rules:
            if not rule(row):
                is_valid = False
                break
        if is_valid:
            valid_data.append(row)
    return valid_data


def merge_datasets(datasets):
    # Memory inefficient merging
    merged = []
    for dataset in datasets:
        merged.extend(dataset)
    return merged


def calculate_correlation(data1, data2):
    # No input validation
    if len(data1) != len(data2):
        return None

    n = len(data1)
    sum_x = sum(data1)
    sum_y = sum(data2)
    sum_xy = sum(x * y for x, y in zip(data1, data2))
    sum_x2 = sum(x * x for x in data1)
    sum_y2 = sum(y * y for y in data2)

    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5

    if denominator == 0:
        return 0

    return numerator / denominator


def main():
    if len(sys.argv) < 2:
        print("Usage: python data_processor.py <input_file>")
        return

    input_file = sys.argv[1]

    # Process data
    data = process_data_file(input_file)

    # Calculate basic statistics
    stats = calculate_statistics(data)
    print(f"Statistics: {stats}")

    # Filter data (example: values greater than 100)
    filtered = filter_data(data, lambda x: len(x) > 0 and float(x[0]) > 100)
    print(f"Filtered rows: {len(filtered)}")

    # Sort data
    sorted_data = sort_data(data)

    # Export results
    export_to_json(stats, "output_stats.json")
    export_to_csv(sorted_data, "output_sorted.csv")

    # Analyze data
    analysis = analyze_data(data)
    print(f"Analysis: {analysis}")

    # Process multiple files (vulnerable)
    all_files_data = process_multiple_files("*.csv")
    print(f"Total data from all files: {len(all_files_data)}")

    # Create temp file (vulnerable)
    temp_file = create_temp_file(data)
    print(f"Created temp file: {temp_file}")


if __name__ == "__main__":
    main()
