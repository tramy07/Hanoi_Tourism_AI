
"""Thuc nghiem so sanh Greedy, A* va vet can cho bai toan tham quan Ha Noi.

Tat ca thoi gian deu tinh bang PHUT.

Dinh nghia "so trang thai duyet" (cot states):
- Greedy : so lan goi try_visit de kiem tra mot diem ung vien.
- A*     : so phuong an (trang thai) da duoc lay ra khoi hang doi va mo rong.
- Vet can: so hoan vi da danh gia bang evaluate (7! = 5040).
Chay file nay bang: python experiments.py
Hoac import cac ham trong notebook.ipynb.
"""

from copy import deepcopy
from pathlib import Path
import csv
import random
import time

from common import try_visit
from greedy import greedy_search
from astar import astar_search
from brute import brute_force_search

OUTPUT_DIR = Path(__file__).resolve().parent / "results"
START_POINT = 0
TIME_REPEATS = 100
RANDOM_DATASETS = 300
RANDOM_SEED = 42

# Gio mo/dong cua va thoi gian tham quan deu tinh bang phut sau nua dem.
# 0: Hoan Kiem Lake la diem xuat phat, khong tinh la diem tham quan.
BASE_PLACES = {
    0: {"name": "Hoan Kiem Lake", "open": 0, "close": 1440, "visit_time": 0},
    1: {"name": "Dong Xuan Market", "open": 8 * 60, "close": 18 * 60, "visit_time": 60},
    2: {"name": "Tran Quoc Pagoda", "open": 7 * 60 + 30, "close": 11 * 60, "visit_time": 30},
    3: {"name": "St. Joseph's Cathedral", "open": 8 * 60, "close": 11 * 60, "visit_time": 60},
    4: {"name": "Temple of Literature", "open": 8 * 60, "close": 17 * 60, "visit_time": 90},
    5: {"name": "Imperial Citadel of Thang Long", "open": 8 * 60, "close": 17 * 60, "visit_time": 120},
    6: {"name": "Ho Chi Minh Mausoleum", "open": 7 * 60 + 30, "close": 11 * 60, "visit_time": 75},
    7: {"name": "Tay Ho Temple", "open": 5 * 60, "close": 18 * 60, "visit_time": 45},
}

# Ma tran thoi gian di chuyen (phut), doi xung theo bang trong file IDEA.
BASE_MATRIX = [
    [0, 8, 15, 4, 11, 10, 12, 29],
    [8, 0, 11, 8, 12, 10, 13, 21],
    [15, 11, 0, 17, 12, 7, 6, 20],
    [4, 8, 17, 0, 10, 8, 11, 27],
    [11, 12, 12, 10, 0, 7, 6, 26],
    [10, 10, 7, 8, 7, 0, 5, 22],
    [12, 13, 6, 11, 6, 5, 0, 23],
    [29, 21, 20, 27, 26, 22, 23, 0],
]

ALGORITHMS = ("Greedy", "A*", "Vet can")


def format_time(minutes):
    """Doi so phut thanh chuoi HH:MM; chap nhan ca thoi gian lon hon 24h."""
    if minutes is None:
        return ""
    minutes = int(round(minutes))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def greedy_state_count(path):
    """Dem so lan Greedy kiem tra mot diem ung vien bang try_visit.

    greedy.py khong tra ve bo dem, nen ta suy ra tu do dai lo trinh:
    moi vong lap kiem tra tat ca diem chua tham; neu chua tham het thi co
    them mot vong kiem tra cuoi khong tim duoc ung vien.
    """
    total_places = len(BASE_PLACES) - 1
    visited = len(path)
    checks = sum(total_places - i for i in range(visited))
    if visited < total_places:
        checks += total_places - visited
    return checks


def run_once(algorithm, start_time, end_time, matrix, places):
    """Chay mot lan va tra ve ket qua chuan hoa."""
    started = time.perf_counter()
    if algorithm == "Greedy":
        path, count, finish = greedy_search(START_POINT, start_time, end_time, matrix, places)
        states = greedy_state_count(path)
    elif algorithm == "A*":
        path, count, finish, states = astar_search(START_POINT, start_time, end_time, matrix, places)
    elif algorithm == "Vet can":
        path, count, finish, states = brute_force_search(START_POINT, start_time, end_time, matrix, places)
    else:
        raise ValueError(f"Thuat toan khong hop le: {algorithm}")
    elapsed = time.perf_counter() - started
    return {
        "algorithm": algorithm,
        "path": list(path),
        "num_visited": int(count),
        "finish_time": finish,
        "finish_clock": format_time(finish),
        "states": int(states),
        "runtime_seconds": elapsed,
    }


def run_and_average(algorithm, scenario, start_time, end_time, matrix, places, repeats=TIME_REPEATS):
    """Chay lap lai de lay thoi gian trung binh; ket qua duoc lay tu lan chay dau."""
    first = None
    elapsed_values = []
    for _ in range(max(1, repeats)):
        result = run_once(algorithm, start_time, end_time, matrix, places)
        if first is None:
            first = result
        elapsed_values.append(result["runtime_seconds"])
    first["scenario"] = scenario
    first["start_time"] = format_time(start_time)
    first["deadline"] = format_time(end_time)
    first["runtime_seconds_avg"] = sum(elapsed_values) / len(elapsed_values)
    first["runtime_repeats"] = len(elapsed_values)
    first.pop("runtime_seconds")
    first["path_names"] = " -> ".join(places[p]["name"] for p in first["path"])
    return first


def trace_path(path, start_time, end_time, matrix, places, start_point=START_POINT):
    """Tra ve gio den, gio bat dau tham, gio roi cua tung diem tren lo trinh.

    Dung try_visit de lay gio roi nen khop 100% voi cach cac thuat toan tinh.
    """
    rows = []
    current_time = start_time
    current_place = start_point
    for place_id in path:
        arrive = current_time + matrix[current_place][place_id]
        ok, leave = try_visit(current_time, end_time, current_place, place_id, matrix, places)
        if not ok:
            break
        rows.append({
            "place": places[place_id]["name"],
            "arrive": format_time(arrive),
            "visit_from": format_time(max(arrive, places[place_id]["open"])),
            "leave": format_time(leave),
        })
        current_time = leave
        current_place = place_id
    return rows


def print_tn2_trace(start_time=8 * 60, end_time=14 * 60):
    """In lo trinh TN2 cua 3 thuat toan kem gio den/gio roi, va diem Greedy bo lo."""
    chosen = {}
    for algorithm in ALGORITHMS:
        result = run_once(algorithm, start_time, end_time, BASE_MATRIX, BASE_PLACES)
        chosen[algorithm] = result["path"]
        print(f"\n=== {algorithm}: {result['num_visited']} diem, xong luc {result['finish_clock']} ===")
        for row in trace_path(result["path"], start_time, end_time, BASE_MATRIX, BASE_PLACES):
            print(f"  {row['place']:<34} den {row['arrive']}  tham tu {row['visit_from']}  roi {row['leave']}")
    missed = [BASE_PLACES[p]["name"] for p in chosen["A*"] if p not in chosen["Greedy"]]
    print("\nDiem A* di ma Greedy bo lo:", ", ".join(missed) if missed else "(khong co)")
    return chosen


def save_csv(rows, filename):
    """Luu danh sach dict thanh CSV bang UTF-8-SIG de mo de dang bang Excel."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    if not rows:
        return path
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def run_fixed_scenarios(repeats=TIME_REPEATS):
    """Chay TN1, TN2, TN3 va luu ket qua tung thuat toan vao CSV."""
    scenarios = []

    # TN1: 8 gio, tat ca dia diem tham quan mo 07:00-22:00.
    tn1_places = deepcopy(BASE_PLACES)
    for place_id in tn1_places:
        if place_id != START_POINT:
            tn1_places[place_id]["open"] = 7 * 60
            tn1_places[place_id]["close"] = 22 * 60
    scenarios.append(("TN1", 8 * 60, 16 * 60, BASE_MATRIX, tn1_places))

    # TN2: du lieu gio mo/dong cua goc, bat dau 08:00, gioi han 6 tieng.
    scenarios.append(("TN2", 8 * 60, 14 * 60, BASE_MATRIX, deepcopy(BASE_PLACES)))

    # TN3: 3 gio xuat phat x 3 do dai hanh trinh.
    for start_hour in (8 * 60, 9 * 60 + 30, 11 * 60):
        for duration_hours in (4, 6, 8):
            scenario_name = f"TN3_start_{format_time(start_hour).replace(':', '')}_{duration_hours}h"
            scenarios.append((scenario_name, start_hour, start_hour + duration_hours * 60,
                              BASE_MATRIX, deepcopy(BASE_PLACES)))

    rows = []
    for scenario_name, start_time, end_time, matrix, places in scenarios:
        for algorithm in ALGORITHMS:
            rows.append(run_and_average(algorithm, scenario_name, start_time, end_time,
                                        matrix, places, repeats=repeats))

    save_csv(rows, "fixed_scenarios_results.csv")
    return rows


def make_random_dataset(rng, base_matrix=BASE_MATRIX, base_places=BASE_PLACES):
    """Tao mot bo du lieu ngau nhien theo TN4, ma tran van doi xung."""
    matrix = [[0 for _ in row] for row in base_matrix]
    for i in range(len(base_matrix)):
        for j in range(i + 1, len(base_matrix)):
            factor = rng.uniform(0.6, 1.4)
            raw = base_matrix[i][j] * factor
            # Lam tron den boi so 5 phut gan nhat; dam bao duong di khong am.
            travel = max(0, int(5 * round(raw / 5)))
            matrix[i][j] = travel
            matrix[j][i] = travel

    places = deepcopy(base_places)
    open_options = (7 * 60, 8 * 60, 9 * 60)
    close_options = (11 * 60, 12 * 60, 17 * 60, 22 * 60)
    visit_options = (30, 60, 90)
    for place_id in places:
        if place_id == START_POINT:
            continue
        opening = rng.choice(open_options)
        closing = rng.choice(close_options)
        # Tat ca moc dong cua trong danh sach deu sau gio mo cua.
        places[place_id]["open"] = opening
        places[place_id]["close"] = closing
        places[place_id]["visit_time"] = rng.choice(visit_options)
    return matrix, places


def run_random_scenarios(n=RANDOM_DATASETS, seed=RANDOM_SEED):
    """TN4: chay 300 bo ngau nhien, xuat CSV va tra ve thong ke tong hop.

    Moi bo du lieu chay moi thuat toan mot lan de giu thoi gian thuc thi hop ly.
    Thoi gian benchmark lap 100 lan duoc ghi rieng trong CSV TN1-TN3.
    """
    rng = random.Random(seed)
    rows = []
    for dataset_id in range(1, n + 1):
        matrix, places = make_random_dataset(rng)
        results = {}
        for algorithm in ALGORITHMS:
            results[algorithm] = run_once(algorithm, 8 * 60, 14 * 60, matrix, places)

        greedy_count = results["Greedy"]["num_visited"]
        astar_count = results["A*"]["num_visited"]
        brute_count = results["Vet can"]["num_visited"]
        rows.append({
            "dataset_id": dataset_id,
            "greedy_count": greedy_count,
            "astar_count": astar_count,
            "brute_count": brute_count,
            "greedy_finish": results["Greedy"]["finish_clock"],
            "astar_finish": results["A*"]["finish_clock"],
            "brute_finish": results["Vet can"]["finish_clock"],
            "greedy_states": results["Greedy"]["states"],
            "astar_states": results["A*"]["states"],
            "brute_states": results["Vet can"]["states"],
            "greedy_runtime_seconds": results["Greedy"]["runtime_seconds"],
            "astar_runtime_seconds": results["A*"]["runtime_seconds"],
            "brute_runtime_seconds": results["Vet can"]["runtime_seconds"],
            "gap_brute_minus_greedy": brute_count - greedy_count,
            "astar_matches_brute": astar_count == brute_count,
        })

    save_csv(rows, "TN4_random_300_results.csv")
    gaps = [row["gap_brute_minus_greedy"] for row in rows]
    summary = {
        "datasets": len(rows),
        "greedy_optimal_rate": sum(row["greedy_count"] == row["brute_count"] for row in rows) / len(rows) if rows else 0,
        "average_gap": sum(gaps) / len(gaps) if gaps else 0,
        "max_gap": max(gaps) if gaps else 0,
        "astar_differs_from_brute": sum(not row["astar_matches_brute"] for row in rows),
        "gap_distribution": {gap: gaps.count(gap) for gap in sorted(set(gaps))},
    }
    save_csv([summary], "TN4_summary.csv")
    return rows, summary


def run_all(repeats=TIME_REPEATS, n_random=RANDOM_DATASETS, seed=RANDOM_SEED):
    """Chay toan bo TN1-TN4 va tra ve du lieu cho notebook."""
    fixed_rows = run_fixed_scenarios(repeats=repeats)
    random_rows, random_summary = run_random_scenarios(n=n_random, seed=seed)
    return fixed_rows, random_rows, random_summary


if __name__ == "__main__":
    print("Dang chay TN1-TN3 (do thoi gian trung binh qua", TIME_REPEATS, "lan)...")
    fixed = run_fixed_scenarios(repeats=TIME_REPEATS)
    print("Da luu:", OUTPUT_DIR / "fixed_scenarios_results.csv")
    print("Dang chay TN4 voi", RANDOM_DATASETS, "bo du lieu ngau nhien...")
    random_rows, summary = run_random_scenarios(n=RANDOM_DATASETS, seed=RANDOM_SEED)
    print("Da luu:", OUTPUT_DIR / "TN4_random_300_results.csv")
    print("Thong ke TN4:", summary)
    print("Luu y: neu astar_differs_from_brute > 0, can kiem tra lai A* va heuristic.")
