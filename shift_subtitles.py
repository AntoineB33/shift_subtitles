import os
import re
from datetime import datetime, timedelta

def parse_time(time_str):
    """Convert SRT timestamp to timedelta."""
    return datetime.strptime(time_str, "%H:%M:%S,%f") - datetime(1900, 1, 1)

def format_time(td):
    """Convert timedelta back to SRT timestamp (clamped at 0)."""
    total_ms = int(td.total_seconds() * 1000)
    if total_ms < 0:
        total_ms = 0
    hours, remainder = divmod(total_ms, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def shift_srt(input_file, output_file, offset_seconds):
    offset = timedelta(seconds=offset_seconds)
    time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")

    with open(input_file, 'r', encoding='utf-8-sig') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            match = time_pattern.match(line)
            if match:
                start, end = match.groups()
                start_time = parse_time(start) + offset
                end_time = parse_time(end) + offset
                outfile.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            else:
                outfile.write(line)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    offset_file = os.path.join(base_dir, "offset.txt")
    output_file = os.path.join(base_dir, "output.srt")

    # --- Find SRT file in input directory ---
    srt_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".srt")]
    if not srt_files:
        print("No .srt file found in the 'input' folder.")
        return
    input_file = os.path.join(input_dir, srt_files[0])

    # --- Read offset value ---
    if not os.path.exists(offset_file):
        print("No 'offset.txt' file found next to the script.")
        return
    with open(offset_file, "r", encoding="utf-8") as f:
        try:
            offset_seconds = float(f.read().strip())
        except ValueError:
            print("Invalid offset value in 'offset.txt'. Must be a number (e.g., 2.5 or -1.2).")
            return

    # --- Shift subtitles ---
    shift_srt(input_file, output_file, offset_seconds)
    print(f"Shifted subtitles by {offset_seconds} seconds.")
    print(f"Created: {output_file}")

if __name__ == "__main__":
    main()
