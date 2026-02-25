
import utils
from pathlib import Path

def process_attendance():
    atten_logs_dir = utils.get_attendance_log_base_dir()
    input_folder_path = Path(atten_logs_dir)
    # print(input_folder)
    
    
    make_ouput_folder = input_folder_path / 'attendance_output'
    make_ouput_folder.mkdir(parents=True, exist_ok=True)
    # print(make_ouput_folder)
    # print(os.listdir(make_ouput_folder))
    
    output_folder_path = Path(make_ouput_folder)
    # print(output_folder_path)
    error_log_txt = output_folder_path / "error_log.txt"
    json_out_path = output_folder_path / "attendance_summary.json"
    excel_out_path = output_folder_path / "attendance_summary.xlsx" 
    error_log_txt.touch(exist_ok=True)
    json_out_path.touch(exist_ok=True)
    excel_out_path.touch(exist_ok=True)
    
    # print(os.listdir(output_folder_path))
    
    clean_data = utils.read_and_clean_data(input_folder_path, error_log_txt)
    print("1. Cleaned the dataset done")
    
    process_data = utils.process_attendance_data(clean_data)
    utils.save_json_summary(process_data, json_out_path)
    print("2. Save data in json format done")
    utils.generate_excel_report(process_data, excel_out_path)
    print("3. Generate a excel file done")
    
    

if __name__ == "__main__":
    process_attendance()
