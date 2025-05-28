from datetime import datetime, timedelta


def generate_ultradian_cycles(
    wake_time_str="06:00:00", peak_minutes=90, trough_minutes=20, cycles=5, grog=20
):
    wake_time = datetime.strptime(wake_time_str, "%H:%M:%S")
    peak_duration = timedelta(minutes=peak_minutes)
    trough_duration = timedelta(minutes=trough_minutes)
    morning_grog = timedelta(minutes=grog)
    results = []

    # Adjust wake_time to account for morning grog
    wake_time += morning_grog

    for i in range(cycles):
        peak_start = wake_time
        peak_end = peak_start + peak_duration
        trough_end = peak_end + trough_duration

        results.append(
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "wake_time": wake_time.strftime("%H:%M:%S"),
                "cycle": i + 1,
                "peak_start": peak_start.strftime("%H:%M:%S"),
                "peak_end": peak_end.strftime("%H:%M:%S"),
                "trough_start": peak_end.strftime("%H:%M:%S"),
                "trough_end": trough_end.strftime("%H:%M:%S"),
            }
        )

        wake_time = trough_end  # move to the next cycle

    return results
