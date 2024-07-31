from datetime import datetime, timedelta


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_time_difference(last_record, mining_hours):
    last_time = datetime.strptime(last_record, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    time_diff = current_time - last_time
    eight_hours = timedelta(hours=mining_hours)

    if time_diff >= eight_hours:
        return True
    else:
        remaining_time = eight_hours - time_diff
        hours, remainder = divmod(remaining_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        remaining_time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        return remaining_time_str
