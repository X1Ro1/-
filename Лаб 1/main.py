import os
import random
import csv
import statistics
from multiprocessing import Pool

CATEGORIES = 'ABCD'
FILE_COUNT = 5
ROWS_PER_FILE = 10000
DATA_FOLDER = "lab1"

def gen_file(file_num):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    path = f"{DATA_FOLDER}/file_{file_num}.csv"

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Категория", "Значение"])

        for _ in range(ROWS_PER_FILE):
            cat = random.choice(CATEGORIES)
            value = round(random.uniform(-80, 180), 3)
            writer.writerow([cat, value])
    print(f"Создан файл {file_num}")

def read_groups(filepath):
    groups = {c: [] for c in CATEGORIES}

    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # заголовок

        for row in reader:
            if len(row) != 2:
                continue
            cat, val_str = row
            if cat not in groups:
                continue
            try:
                groups[cat].append(float(val_str))
            except ValueError:
                pass
    return groups

def calc_stats(groups):
    stats = {}
    for cat in CATEGORIES:
        values = groups[cat]
        if not values:
            stats[cat] = (0.0, 0.0)
            continue
        median = statistics.median(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        stats[cat] = (round(median, 4), round(stdev, 4))
    return stats

def main():
    print("Генерация файлов")
    file_paths = []
    for i in range(1, FILE_COUNT + 1):
        gen_file(i)
        file_paths.append(f"{DATA_FOLDER}/file_{i}.csv")

    print("\nПараллельная обработка")
    with Pool(FILE_COUNT) as pool:
        results = pool.map(read_groups, file_paths)

    # Все данные вместе
    all_values = {c: [] for c in CATEGORIES}
    for res in results:
        for c in CATEGORIES:
            all_values[c].extend(res[c])

    print("\nОбщая статистика по всем файлам:")
    total_stats = calc_stats(all_values)
    for c in CATEGORIES:
        m, s = total_stats[c]
        print(f"{c} {m:10.4f} {s:10.4f}")

    # Медианы по каждому файлу
    medians_by_cat = {c: [] for c in CATEGORIES}
    for res in results:
        file_stats = calc_stats(res)
        for c in CATEGORIES:
            medians_by_cat[c].append(file_stats[c][0])

    print("\nМедиана и разброс медиан:")
    for c in CATEGORIES:
        med_list = medians_by_cat[c]
        if not med_list:
            print(f"{c} 0.0000 0.0000")
            continue
        med_of_meds = statistics.median(med_list)
        std_of_meds = statistics.stdev(med_list) if len(med_list) > 1 else 0.0
        print(f"{c}{round(med_of_meds, 4):10.4f}{round(std_of_meds, 4):10.4f}")


if __name__ == "__main__":
    main()
