import os
import hashlib

# Define the path to the project and the structure file
#project_path = "/mnt/data/skrizhal_protocol"
project_path = "./"
structure_file = os.path.join(project_path, "doc", "Структура_файлов.md")

# Function to calculate the MD5 hash of a file
def calculate_md5(file_path):
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return None

# Function to parse the structure file and extract expected MD5 hashes
def parse_structure_file():
    file_md5s = {}
    try:
        with open(structure_file, "r", encoding="utf-8") as f:
            for line in f:
                if " # md5:" in line:
                    parts = line.split(" # md5:")
                    file_path = parts[0].strip().replace("├── ", "").replace("│   ├── ", "").replace("/", os.sep)
                    md5_hash = parts[1].split()[0]
                    file_md5s[file_path] = md5_hash
        return file_md5s
    except FileNotFoundError:
        print("Structure file not found.")
        return {}

# Function to check the files against the expected MD5 hashes
def check_files(file_md5s):
    results = []
    for file, expected_md5 in file_md5s.items():
        absolute_path = os.path.join(project_path, file)
        if os.path.isfile(absolute_path):  # Only process files
            current_md5 = calculate_md5(absolute_path)
            if current_md5 == expected_md5:
                results.append(f"{file} +")
            else:
                results.append(f"{file} -")
        elif os.path.isdir(absolute_path):
            results.append(f"{file} Directory - Skipped")
        else:
            results.append(f"{file} Missing -")
    return results

# Main function for a single execution
def main():
    print("Starting one-time file integrity check...")
    file_md5s = parse_structure_file()
    results = check_files(file_md5s)
    for result in results:
        print(result)
    print("File integrity check completed.")

if __name__ == "__main__":
    main()
