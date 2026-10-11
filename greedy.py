import itertools

#  THUẬT TOÁN GREEDY (DÙNG try_visit MỖI BƯỚC)
# =========================================================
from common import try_visit
def greedy_search(start_point, start_time, end_time, matrix, places):
    current_place = start_point
    current_time = start_time

    # Lấy danh sách các điểm cần thăm (loại trừ điểm xuất phát)
    all_places = list(places.keys()) if isinstance(places, dict) else list(range(len(places)))
    unvisited = [p for p in all_places if p != start_point]

    path = []

    while unvisited:
        candidates = []

        # Bước 2: Gọi try_visit cho từng điểm chưa thăm
        for nxt in unvisited:
            decide, finished_time = try_visit(current_time, end_time, current_place, nxt, matrix, places)
            if decide == True:
                travel_time = matrix[current_place][nxt]
                candidates.append((nxt, travel_time, finished_time))

        # Bước 3: Không còn ứng viên hợp lệ -> Dừng
        if not candidates:
            break

        # Bước 4: Chọn ứng viên có thời gian di chuyển ngắn nhất (matrix nhỏ nhất).
        # Nếu hòa, ưu tiên điểm có số thứ tự (index) nhỏ hơn.
        candidates.sort(key=lambda x: (x[1], x[0]))
        best_candidate, _, best_finish_time = candidates[0]

        # Bước 5: Cập nhật lộ trình và trạng thái
        path.append(best_candidate)
        unvisited.remove(best_candidate)
        current_place = best_candidate
        current_time = best_finish_time

    num_visited = len(path)
    return path, num_visited, current_time


