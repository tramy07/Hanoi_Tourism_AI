from common import try_visit

# hàm tính h: đếm số điểm chưa thăm mà từ current_place lúc current_time vẫn đi được
def count_feasible(current_time, end_time, current_place, remaining, matrix, places):
    count = 0
    for nxt in remaining:
        decide, finished_time = try_visit(current_time, end_time, current_place, nxt, matrix, places)
        if decide == True:
            count = count + 1
    return count


# A*: tìm lộ trình thăm được nhiều điểm nhất (hòa thì xong sớm hơn),
# chỉ mở rộng nhánh có f = g + h cao nhất và bỏ nhánh không thể tốt hơn.
# Trả về: lộ trình, số điểm, giờ kết thúc, số phương án đã mở rộng.
def astar_search(start_point, start_time, end_time, matrix, places):
    to_visit = []
    for i in range(len(places)):
        if i != start_point:
            to_visit.append(i)

    h0 = count_feasible(start_time, end_time, start_point, to_visit, matrix, places)
    first_state = {
        'place': start_point,
        'time': start_time,
        'path': [],
        'f': h0
    }
    queue = [first_state]
    best_num = 0
    best_time = start_time
    best_path = []
    expanded = 0

    while queue:
        # chọn phương án có f cao nhất (hòa f thì xong sớm hơn)
        chosen = queue[0]
        for s in queue:
            if s['f'] > chosen['f'] or (s['f'] == chosen['f'] and s['time'] < chosen['time']):
                chosen = s
        queue.remove(chosen)

        current_place = chosen['place']
        current_time = chosen['time']
        path = chosen['path']
        f = chosen['f']

        # cắt tỉa: nhánh này không thể hơn kỷ lục
        if f < best_num:
            continue

        expanded = expanded + 1

        # cập nhật kỷ lục
        g = len(path)
        if g > best_num or (g == best_num and current_time < best_time):
            best_num = g
            best_time = current_time
            best_path = path

        # các điểm chưa thăm của phương án này
        remaining = []
        for p in to_visit:
            if p not in path:
                remaining.append(p)

        # thử đi thêm từng điểm, sinh phương án mới
        for nxt in remaining:
            decide, finished_time = try_visit(current_time, end_time, current_place, nxt, matrix, places)
            if decide == True:
                new_path = path + [nxt]
                new_remaining = remaining.copy()
                new_remaining.remove(nxt)
                h = count_feasible(finished_time, end_time, nxt, new_remaining, matrix, places)
                new_f = len(new_path) + h
                if new_f >= best_num:
                    queue.append({
                        'place': nxt,
                        'time': finished_time,
                        'path': new_path,
                        'f': new_f
                    })

    return best_path, best_num, best_time, expanded