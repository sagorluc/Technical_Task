import re
from datetime import time, timedelta

def is_valid_name(name):
    """Check if name contains only letters, spaces, and hyphens"""
    return bool(re.match(r'^[A-Za-z]+$', name))

def is_numeric_number(number):
    """Check if string contains only digits 0-9"""
    if not isinstance(number, str):
        return False
    return number.isdigit()

def is_employee_id(emp_id):
    """Check if employee ID contains only numbers"""
    return bool(re.match(r'^\d+$', emp_id))

def is_late_entry(first_punch_time):
    """Check if employee had late entry (after 09:30 AM)"""
    late_threshold = time(9, 30)  # 09:30 AM
    return first_punch_time.time() > late_threshold

def is_early_exit(last_punch_time):
    """Check if employee had early exit (before 05:00 PM)"""
    early_threshold = time(17, 0)  # 05:00 PM
    return last_punch_time.time() < early_threshold

def check_employee_ID(emp_id, elog, row_info):
    """Validate employee ID - required and must be numeric"""
    if not emp_id:
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Missing employee ID\n")
        return False
    
    if not is_employee_id(emp_id):
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Employee ID invalid: '{emp_id}' - must contain only numbers\n")
        return False
    
    return True

def check_first_name(first_name, elog, row_info):
    """Validate first name - required and must be alphabetic with spaces/hyphens"""
    if not first_name:
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Missing first name\n")
        return False
    
    if not is_valid_name(first_name):
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. First name character invalid: '{first_name}' - must contain only letters, spaces, and hyphens\n")
        return False
    
    return True

def check_last_name(last_name, elog, row_info):
    """Validate last name - required and must be alphabetic with spaces/hyphens"""
    if not last_name:
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Missing last name\n")
        return False
    
    if not is_valid_name(last_name):
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Last name character invalid: '{last_name}' - must contain only letters, spaces, and hyphens\n")
        return False
    
    return True

def check_timestamp_row(timestamp_raw, elog, row_info):
    """Validate timestamp - required and must be numeric"""
    if not timestamp_raw:
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Missing timestamp\n")
        return False
    
    if not is_numeric_number(timestamp_raw):
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Timestamp is not valid number: '{timestamp_raw}' - must contain only numbers\n")
        return False
    
    return True

def check_device(device, elog, row_info):
    """Validate device - optional field"""
    if not device:
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Missing device\n")
        return False
    
    if not re.match(r'^[A-Za-z0-9\s]+$', device):
        elog.write(f"File-Name: {row_info['file_name']}: ROW: {row_info['row_number']}. Device name invalid: '{device}' - must contain only letters, numbers, and spaces\n")
        return False
    
    return True

def calculate_working_hours(punches):
    """Calculate working hours from punch records"""
    if not punches:
        return timedelta(0)
    
    # Sort punches by timestamp
    sorted_punches = sorted(punches)
    
    first_punch = sorted_punches[0]
    last_punch = sorted_punches[-1]
    
    working_hours = last_punch - first_punch
    
    if len(sorted_punches) >= 2:
        max_gap = max((sorted_punches[i+1] - sorted_punches[i] for i in range(len(sorted_punches)-1)), 
                     default=timedelta(0))
        if max_gap > timedelta(hours=1):
            working_hours -= timedelta(hours=1) 
    
    return working_hours