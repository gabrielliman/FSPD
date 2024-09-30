import os
import subprocess

def run_diff_ignoring_order(folder1, folder2):
    # List of files in both folders
    files1 = os.listdir(folder1)
    files2 = os.listdir(folder2)

    # Ensure only common files are compared
    common_files = set(files1).intersection(files2)

    # Iterate over the common files and run diff after sorting
    for file_name in common_files:
        file1_path = os.path.join(folder1, file_name)
        file2_path = os.path.join(folder2, file_name)
        
        try:
            # Sort the files before comparing them
            with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                sorted_file1 = sorted(f1.readlines())
                sorted_file2 = sorted(f2.readlines())
                
            # Create temporary sorted files
            temp_file1 = file1_path + '.sorted'
            temp_file2 = file2_path + '.sorted'
            
            with open(temp_file1, 'w') as tf1, open(temp_file2, 'w') as tf2:
                tf1.writelines(sorted_file1)
                tf2.writelines(sorted_file2)
                
            # Run diff on the sorted files
            result = subprocess.run(['diff', temp_file1, temp_file2], capture_output=True, text=True)
            if result.returncode == 0:
                pass
                #print(f"No differences found in {file_name} (ignoring line order)")
            else:
                print(f"Differences found in {file_name} (ignoring line order)")
            
            # Remove temporary files
            os.remove(temp_file1)
            os.remove(temp_file2)
            
        except Exception as e:
            print(f"Error comparing {file_name}: {e}")

if __name__ == "__main__":
    folder1 = "outputs"
    folder2 = "outputs_res"
    run_diff_ignoring_order(folder1, folder2)
