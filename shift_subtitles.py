import sys
from datetime import timedelta, datetime
import re

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

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python shift_subtitles.py input.srt output.srt offset_seconds")
    else:
        input_path, output_path, offset = sys.argv[1], sys.argv[2], float(sys.argv[3])
        shift_srt(input_path, output_path, offset)
        print(f"Subtitles shifted by {offset} seconds and saved to '{output_path}'.")
