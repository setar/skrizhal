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

# Function to update only MD5 hashes while preserving descriptions
def update_md5_hashes():
    updated_lines = []
    try:
        with open(structure_file, "r", encoding="utf-8") as f:
            for line in f:
                if " # md5:" in line:
                    parts = line.split(" # md5:")
                    file_path = parts[0].strip().replace("├── ", "").replace("│   ├── ", "").replace("/", os.sep)
                    description = parts[1].split(" ", 1)[1].strip() if len(parts[1].split(" ", 1)) > 1 else ""
                    absolute_path = os.path.join(project_path, file_path)
                    if os.path.isfile(absolute_path):
                        md5_hash = calculate_md5(absolute_path)
                        updated_lines.append(f"{file_path} # md5:{md5_hash} {description}")
                    else:
                        updated_lines.append(line.strip())  # Preserve the line as-is for missing files
                else:
                    updated_lines.append(line.strip())
    except FileNotFoundError:
        print("Structure file not found.")

    # Write updated lines back to the structure file
    with open(structure_file, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))
    print("MD5 hashes updated successfully.")

if __name__ == "__main__":
    update_md5_hashes()
