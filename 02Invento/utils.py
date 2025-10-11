import os
import json
from pathlib import Path
import traceback
from collections import defaultdict
from datetime import datetime, time
import pandas as pd
import validation

def get_attendance_log_base_dir():
    """
    Docstring:
    Return the attendance log folder path
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    attendance_log_dir = os.path.join(base_path, "attendance_logs")
    return attendance_log_dir

def chunk_len_of_file(file_path):
    """
    Docstring:
    Return the size of total dataset
    """
    with open(file_path, 'r') as f:
        total_size = sum(1 for _ in f)
    return total_size

def read_and_clean_data(input_folder_path, error_log_txt):
    """
    Docstring:
    Read and clean attendance data from multiple log files
    
    Args:
        input_folder_path (str): Path to folder containing log files
        error_log_txt (str): Path to error log file
    
    Returns:
        list: Cleaned and merged attendance records
    """
    data_set = set()
    merged_data = []

    files = [p for p in Path(input_folder_path).iterdir() 
             if p.suffix.lower() in (".csv", ".log")]
    
    with open(error_log_txt, "w", encoding="utf-8") as elog:
        elog.write("Error log for attendance processing\n")
        elog.write(f"Run at: {datetime.utcnow().isoformat()}Z\n\n")
        
        for f_path in files:
            try:
                try:

                    data_frame = pd.read_csv(f_path, header=None, dtype=str, sep=r"\s+", engine='python')
                except:
                    # comma separator fallback
                    data_frame = pd.read_csv(f_path, header=None, dtype=str, sep=",", engine='python')
                

                if len(data_frame.columns) >= 5:
                    data_frame = data_frame.iloc[:, :5]  # first 5 columns
                    data_frame.columns = ["emp_code", "first_name", "last_name", "timestamp", "device"]
                elif len(data_frame.columns) == 4:
                    data_frame.columns = ["emp_code", "first_name", "last_name", "timestamp", "device"]
                    # data_frame["device"] = "Unknown"
                else:
                    elog.write(f"File:{f_path.name} -> Invalid format: expected 4-5 columns, got {len(data_frame.columns)}\n")
                    continue
                
                for index, row in data_frame.iterrows():
                    try:
                        emp_code = str(row.get("emp_code") or "").strip()
                        first_name = str(row.get("first_name") or "").strip()
                        last_name = str(row.get("last_name") or "").strip()
                        timestamp_raw = str(row.get("timestamp") or "").strip()
                        device = str(row.get("device") or "").strip()

                        row_info = {"file_name": f_path.name, "row_number": index + 1}
                        
                        is_valid = True
                        
                        if not validation.check_employee_ID(emp_code, elog, row_info):
                            is_valid = False
                        
                        if not validation.check_first_name(first_name, elog, row_info):
                            is_valid = False

                        if not validation.check_last_name(last_name, elog, row_info):
                            is_valid = False
                        
                        if not validation.check_timestamp_row(timestamp_raw, elog, row_info):
                            is_valid = False
                        
                        if not validation.check_device(device, elog, row_info):
                            is_valid = False
                        
                        # any validation failed, just skip
                        if not is_valid:
                            continue

                        # timestamp convert unix to datetime
                        try:
                            int_timestamp = int(timestamp_raw)
                            punch_time = datetime.utcfromtimestamp(int_timestamp)
                        except (ValueError, TypeError, OSError) as e:
                            elog.write(f"File:{f_path.name} -> Row:{index + 1} -> Invalid timestamp '{timestamp_raw}': {str(e)}\n")
                            continue

                        # duplicate data and log them
                        data_key = (emp_code, int_timestamp, device)
                        if data_key in data_set:
                            elog.write(
                                f"File:{f_path.name} -> Row:{index + 1} -> Duplicate data: {emp_code} {first_name} {last_name} {timestamp_raw} {device}\n"
                            )
                            continue
                        data_set.add(data_key)

                        merged_data.append({
                            "emp_code": emp_code,
                            "first_name": first_name,
                            "last_name": last_name,
                            "timestamp": punch_time,
                            "device": device,
                            "date": punch_time.date()
                        })

                    except Exception as e:
                        elog.write(f"File:{f_path.name} -> Row:{index + 1} -> Error: {str(e)}\n")
                        elog.write(traceback.format_exc() + "\n")

            except Exception as e:
                elog.write(f"Failed reading file {f_path.name} -> {repr(e)}\n")
                elog.write(traceback.format_exc() + "\n")

    return merged_data


def process_attendance_data(cleaned_data):
    """
    Docstring:
    Process cleaned attendance data to generate daily summaries
    
    Args:
        cleaned_data (list): List of cleaned attendance records
    
    Returns:
        dict: Processed attendance summary by date
    """
    # group by employee and date
    employee_daily_data = defaultdict(lambda: defaultdict(list))
    
    for record in cleaned_data:
        employee_daily_data[record["date"]][record["emp_code"]].append({
            "timestamp": record["timestamp"],
            "first_name": record["first_name"],
            "last_name": record["last_name"],
            "device": record["device"]
        })
    
    attendance_summary = {}
    
    for date in sorted(employee_daily_data.keys()):
        date_str = date.isoformat()
        attendance_summary[date_str] = []
        
        for emp_code in sorted(employee_daily_data[date].keys()):
            records = employee_daily_data[date][emp_code]
            punches = [record["timestamp"] for record in records]
            
            punches.sort() # punches chronologically
            
            first_punch = punches[0]
            last_punch = punches[-1]
            total_punches = len(punches)
            
            working_hours_td = validation.calculate_working_hours(punches)
            working_hours_str = f"{working_hours_td.seconds // 3600:02d}:{(working_hours_td.seconds % 3600) // 60:02d}"
        
            late_entry = 1 if validation.is_late_entry(first_punch) else 0
            early_exit = 1 if validation.is_early_exit(last_punch) else 0
            
            if total_punches == 1:
                punch_time = first_punch.time()
                if punch_time > time(9, 30):  # after 09:30 AM
                    late_entry = 1
                    early_exit = 0
                elif punch_time < time(17, 0):  # before 05:00 PM  
                    late_entry = 0
                    early_exit = 1
                else:
                    late_entry = 0
                    early_exit = 0
            
            if total_punches == 1: # single punch case
                late_entry = 1  
                early_exit = 1 
            
            attendance_summary[date_str].append({
                "emp_code": emp_code,
                "first_punch": first_punch.strftime("%H:%M"),
                "last_punch": last_punch.strftime("%H:%M"),
                "total_punches": total_punches,
                "working_hours": working_hours_str,
                "late_entry": late_entry,
                "early_exit": early_exit
            })
    
    return attendance_summary


def generate_excel_report(attendance_summary, output_file):
    """
    Docstring:
    Generate Excel report from attendance summary
    
    Args:
        attendance_summary (dict): Processed attendance data
        output_file (str): Output Excel file path
    """
    excel_data = []
    
    for date, records in attendance_summary.items():
        for record in records:
            excel_data.append({
                "Date": date,
                "Emp Code": record["emp_code"],
                "First Punch": record["first_punch"],
                "Last Punch": record["last_punch"],
                "Total Punches": record["total_punches"],
                "Working Hours": record["working_hours"],
                "Late Entry": "Yes" if record["late_entry"] else "No",
                "Early Exit": "Yes" if record["early_exit"] else "No"
            })
    
    if excel_data:
        df = pd.DataFrame(excel_data)
        df.to_excel(output_file, index=False, engine='openpyxl')


def save_json_summary(attendance_summary, output_file):
    """
    Docstring:
    Save attendance summary as JSON file
    
    Args:
        attendance_summary (dict): Processed attendance data
        output_file (str): Output JSON file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(attendance_summary, f, indent=2, ensure_ascii=False)
        