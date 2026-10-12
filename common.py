def try_visit(current_time, end_time, current_location, next_location, matrix, places):
    arrive_time = current_time + matrix[current_location][next_location]
    total_spend_time = max(arrive_time, places[next_location]['open']) + places[next_location]['visit_time']
    if total_spend_time > places[next_location]['close'] or total_spend_time > end_time:
        return False, None
    else:
        return True, total_spend_time

def evaluate(path, start_time, end_time, start_point, matrix, places):
    current_time = start_time
    num_of_visited_places = 0
    current_place = start_point
    for i in range(len(path)):
        aim_location = path[i]
        decide, finished_time =try_visit(current_time, end_time, current_place, aim_location, matrix, places)
        if decide == True:
            current_time = finished_time
            num_of_visited_places += 1
            current_place = aim_location
        else:
            return num_of_visited_places, current_time
    return num_of_visited_places, current_time

def data_change(data):
    def time_to_minutes(time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    for location in data.values():
        if isinstance(location["open"], str):
            location["open"] = time_to_minutes(location["open"])
        if isinstance(location["close"], str):
            location["close"] = time_to_minutes(location["close"])
    return 0
