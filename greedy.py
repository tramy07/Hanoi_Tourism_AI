# THUẬT TOÁN GREEDY (h lớn nhất; hòa thì thời gian di chuyển bé nhất)
# =========================================================
from common import try_visit


def greedy_search(start_point, start_time, end_time, matrix, places):
    current_place = start_point
    current_time = start_time

    all_places = list(places.keys()) if isinstance(places, dict) else list(range(len(places)))
    unvisited = [p for p in all_places if p != start_point]

    path = []
    states = 0  # tổng số lần gọi try_visit (lọc ứng viên + đếm h)

    while unvisited:
        candidates = []

        # Bước 1: lọc các điểm khả thi
        for nxt in unvisited:
            decide, finished_time = try_visit(current_time, end_time, current_place, nxt, matrix, places)
            states += 1
            if decide == True:
                # Bước 2: h = số điểm còn lại vẫn đi được sau khi thăm nxt
                h = 0
                for other in unvisited:
                    if other == nxt:
                        continue
                    ok, _ = try_visit(finished_time, end_time, nxt, other, matrix, places)
                    states += 1
                    if ok == True:
                        h += 1
                candidates.append((nxt, h, matrix[current_place][nxt], finished_time))

        if not candidates:
            break

        # Bước 3: h lớn nhất -> hòa thì thời gian di chuyển BÉ nhất -> hòa nữa thì index nhỏ hơn
        candidates.sort(key=lambda x: (-x[1], x[2], x[0]))
        best_candidate, _, _, best_finish_time = candidates[0]

        path.append(best_candidate)
        unvisited.remove(best_candidate)
        current_place = best_candidate
        current_time = best_finish_time

    return path, len(path), current_time, states
