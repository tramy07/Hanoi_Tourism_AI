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


# =========================================================
# THUẬT TOÁN VÉT CẠN (DÙNG evaluate ĐỂ ĐÁNH GIÁ MỖI HOÁN VỊ)
# =========================================================

def brute_force_search(start_point, start_time, end_time, matrix, places):
    all_places = list(places.keys()) if isinstance(places, dict) else list(range(len(places)))
    places_to_visit = [p for p in all_places if p != start_point]

    best_full_perm = []
    best_num_visited = -1
    best_end_time = float('inf')
    total_evaluated = 0

    # Bước 1: Tạo tất cả hoán vị của các điểm
    for perm in itertools.permutations(places_to_visit):
        total_evaluated += 1

        # Bước 2: Gọi hàm evaluate của bạn để đánh giá hoán vị này
        num_visited, finish_time = evaluate(perm, start_time, end_time, start_point, matrix, places)

        # Bước 3: Chọn thứ tự tốt nhất (nhiều điểm nhất -> kết thúc sớm hơn)
        if num_visited > best_num_visited:
            best_num_visited = num_visited
            best_end_time = finish_time
            best_full_perm = perm
        elif num_visited == best_num_visited:
            if finish_time < best_end_time:
                best_end_time = finish_time
                best_full_perm = perm

    # Cắt chuỗi hoán vị đúng bằng số điểm đi được thực tế
    actual_path = list(best_full_perm[:best_num_visited])

    # Trả về: Lộ trình thực tế, số điểm, giờ kết thúc, số hoán vị đã duyệt
    return actual_path, best_num_visited, best_end_time, total_evaluated
