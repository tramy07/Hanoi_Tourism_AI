
# THUẬT TOÁN VÉT CẠN (DÙNG evaluate ĐỂ ĐÁNH GIÁ MỖI HOÁN VỊ)
# =========================================================
import itertools
from common import try_visit, evaluate

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
