## Attendance Log Processor

A simple, clear step-by-step guide explaining the project, how the code works, and how to run it.

---

### Project overview

This project reads raw attendance logs from multiple device files `(CSV / .log)`, cleans and validates rows, deduplicates records, computes per-employee daily summaries (first/last punch, total punches, working hours, late/early flags), and writes:

- `attendance_output/attendance_summary.json` — JSON summary grouped by date
- `attendance_output/attendance_summary.xlsx` — Excel report (human-friendly columns)
- `attendance_output/error_log.txt — reasons` for skipped/invalid rows

The code is divided into:
- `utils.py` — core reading, cleaning, processing, report generation
- `validation.py` — validators and small utility functions (name checks, timestamp checks, working hours computation)
- `process_attendance.py` — small runner that ties everything together
- `requirements.txt` — Python dependencies

---

### Quick start
1. Create a Python virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # on Linux/macOS
.venv\Scripts\activate      # on Windows (PowerShell)
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Put your log files into the `attendance_logs/` folder placed next to the scripts. Files may be `.csv` or `.log`. Each file should have columns:
```sql
emp_code, first_name, last_name, timestamp, device
```
- timestamp should be a Unix timestamp (integer seconds).
- If log files use spaces rather than commas, the reader attempts a whitespace split first, then falls back to comma separation.

4. Run the processor:
```bash
python process_attendance.py
```
5. Outputs will be in attendance_logs/attendance_output/:
- attendance_summary.json
- attendance_summary.xlsx
- error_log.txt

---

### What each file/function does — step-by-step
#### `utils.get_attendance_log_base_dir()`
  - Returns the base folder path where the script is located and constructs `attendance_logs` path.
  - Used by the runner to locate input log files.<br>
  ```python
    def get_attendance_log_base_dir():
        """
        Docstring:
        Return the attendance log folder path
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        attendance_log_dir = os.path.join(base_path, "attendance_logs")
        return attendance_log_dir
  ```
#### `utils.chunk_len_of_file(file_path)`
  - Returns the number of lines in a file (useful for estimating size).
  - Not required for processing but helpful diagnostics.
  ```python
    def chunk_len_of_file(file_path):
        """
        Docstring:
        Return the size of total dataset
        """
        with open(file_path, 'r') as f:
            total_size = sum(1 for _ in f)
        return total_size
  ```
#### `utils.read_and_clean_data(input_folder_path, error_log_txt)`
**Purpose:** read all files, validate rows, convert timestamps, deduplicate, and produce a cleaned list of records.

#### Step-by-step behavior:
1. Builds a set of files in input_folder_path with `.csv` or `.log` suffix.
2. Opens `error_log.txt` and writes a `header` with `timestamp`.
3. For each file:
  - Tries to read with whitespace separator; if that fails, attempts comma separator. This allows flexibility for plain `log` files or `CSVs`.
  - Normalizes to 5 columns: `emp_code`, `first_name`, `last_name`, `timestamp`, `device`. If columns do not match expected dimensions, logs error and skips the file.
4. For each row:
- Extracts and strips fields.
- Prepares `row_info` (file & row number) for clear error messages.
- Uses validation.py functions to validate each field:
    - `check_employee_ID` ensures emp_code exists and is numeric.
    - `check_first_name` and `check_last_name` ensure names are present and alphabetic.
    - `check_timestamp_raw` ensures the timestamp is numeric.
    - `check_device` ensures the device name exists and matches allowed characters.
- If any validator fails, the row is skipped and a message is appended to `error_log.txt`.
- If validations pass, tries to convert timestamp `(Unix seconds)` into a datetime object using - `datetime.utcfromtimestamp`.
- Deduplicates using a set keyed by `(emp_code, timestamp_int, device)` — duplicates are logged and skipped.
- Adds cleaned record to merged_data with fields:
```py
{
  "emp_code": str,
  "first_name": str,
  "last_name": str,
  "timestamp": datetime,
  "device": str,
  "date": datetime.date()  # the date portion
}
```
**Return:** merged_data — a list of validated, deduplicated records.

---

#### `utils.process_attendance_data(cleaned_data)`

**Purpose:** Build the attendance summary per date and per employee.

#### Step-by-step behavior:

1. Groups records into `employee_daily_data[date][emp_code]` = list of records.
2. For each date (sorted) and each employee (sorted numerically when possible):
- Collects punch times sorted chronologically.
- Computes:
    - `first_punch` (first datetime in list)
    - `last_punch` (last datetime)
    - `total_punches` (count)
- Uses validation utilities:
    - `validation.calculate_working_hours(punches)` — returns a timedelta of working hours (subtracts 1 hour if max gap between punches >1 hour, as a simple lunch break heuristic).
    - `validation.is_late_entry(first_punch)` — checks if first punch is after 09:30.
    - `validation.is_early_exit(last_punch)` — checks if last punch is before 17:00.

- Special handling for single-punch days:
    - Code sets `late/early` flags (there are two places applying logic; note below in "known quirks" section).
- Creates a record:
```py
{
  "emp_code": str,
  "first_punch": "HH:MM",
  "last_punch": "HH:MM",
  "total_punches": int,
  "working_hours": "HH:MM",
  "late_entry": 0/1,
  "early_exit": 0/1
}
```
3. Compiles and returns attendance_summary as:
```python
{ "YYYY-MM-DD": [ list of employee records... ], ... }
```
---

#### `utils.generate_excel_report(attendance_summary, output_file)`
- Converts the attendance_summary into a tabular pandas DataFrame with columns:
- Date | Emp Code | First Punch | Last Punch | Total Punches | Working Hours | Late Entry | Early Exit
- Late Entry and Early Exit are rendered as "Yes" / "No".
Writes Excel using openpyxl engine.
#### `utils.save_json_summary(attendance_summary, output_file)`
- Dumps the attendance_summary to JSON with indent=2.

---

#### `validation.py` — helper rules
- Name, ID checks:
    - `is_valid_name`, `is_employee_id` ensure proper characters.
- Row validators (check_*) write human-readable messages to the provided elog (error log) and return boolean `pass/fail`.
- Working hours computation:
    - calculate_working_hours(punches):
        - If there are ≥ 2 punches: last - first.
        - If the maximum gap between consecutive punches is more than 1 hour, the function subtracts 1 hour from working hours (simple lunch break heuristic).
- `Late/early` helpers:
    - `is_late_entry` — true if first punch is after 09:30.
    - `is_early_exit` — true if last punch is before 17:00.

---

#### Example JSON output structure
```json
{
  "2025-09-24": [
    {
      "emp_code": "10023",
      "first_punch": "09:05",
      "last_punch": "18:10",
      "total_punches": 4,
      "working_hours": "09:05",
      "late_entry": 0,
      "early_exit": 0
    },
    {
      "emp_code": "10025",
      "first_punch": "11:00",
      "last_punch": "11:00",
      "total_punches": 1,
      "working_hours": "00:00",
      "late_entry": 1,
      "early_exit": 1
    }
  ]
}
```
