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
    # Regex to match timestamps like 00:00:01,000 --> 00:00:05,000
    time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")

    with open(input_file, 'r', encoding='utf-8-sig') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            match = time_pattern.match(line)
            if match:
                start, end = match.groups()
                # Parse, shift, and re-format
                start_time = parse_time(start) + offset
                end_time = parse_time(end) + offset
                outfile.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            else:
                outfile.write(line)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output") # New output directory
    offset_file = os.path.join(base_dir, "offset.txt")

    # --- 1. Read offset value ---
    if not os.path.exists(offset_file):
        print("No 'offset.txt' file found next to the script.")
        return
    with open(offset_file, "r", encoding="utf-8") as f:
        try:
            offset_seconds = float(f.read().strip())
        except ValueError:
            print("Invalid offset value in 'offset.txt'. Must be a number (e.g., 2.5 or -1.2).")
            return

    # --- 2. Find SRT files in input directory ---
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created missing input folder at: {input_dir}")
        print("Please put your .srt files there and run again.")
        return

    srt_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".srt")]
    
    if not srt_files:
        print("No .srt files found in the 'input' folder.")
        return

    # --- 3. Prepare Output Directory ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # --- 4. Process Batch ---
    print(f"Applying offset of {offset_seconds} seconds to {len(srt_files)} files...")
    print("-" * 40)

    for filename in srt_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            shift_srt(input_path, output_path, offset_seconds)
            print(f"[OK] {filename}")
        except Exception as e:
            print(f"[ERROR] Could not process {filename}: {e}")

    print("-" * 40)
    print("Batch processing complete.")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")