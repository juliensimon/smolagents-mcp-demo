import csv
import json
import os
import sys
from collections import defaultdict


def process_data_file(filename):
    data = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
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
    return sorted(data, key=lambda x: x[column] if len(x) > column else 0)


def export_to_json(data, filename):
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


if __name__ == "__main__":
    main()
