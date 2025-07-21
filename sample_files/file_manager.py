import base64
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import tarfile
import threading
import urllib.parse
import zipfile
from datetime import datetime


class FileManager:
    def __init__(self):
        self.base_path = "/home/user/documents"
        self.temp_path = "/tmp"
        self.backup_path = "/backup"
        self.lock = threading.Lock()

    def list_files(self, directory=None):
        if directory is None:
            directory = self.base_path

        try:
            files = os.listdir(directory)
            return files
        except:
            return []

    def read_file(self, filepath):
        try:
            with open(filepath, "r") as f:
                return f.read()
        except:
            return None

    def write_file(self, filepath, content):
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return True
        except:
            return False

    def copy_file(self, source, destination):
        try:
            shutil.copy2(source, destination)
            return True
        except:
            return False

    def move_file(self, source, destination):
        try:
            shutil.move(source, destination)
            return True
        except:
            return False

    def delete_file(self, filepath):
        try:
            os.remove(filepath)
            return True
        except:
            return False

    def create_directory(self, dirpath):
        try:
            os.makedirs(dirpath, exist_ok=True)
            return True
        except:
            return False

    def delete_directory(self, dirpath):
        try:
            shutil.rmtree(dirpath)
            return True
        except:
            return False

    def get_file_info(self, filepath):
        try:
            stat = os.stat(filepath)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "permissions": oct(stat.st_mode)[-3:],
            }
        except:
            return None

    def search_files(self, pattern, directory=None):
        if directory is None:
            directory = self.base_path

        results = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if pattern in file:
                        results.append(os.path.join(root, file))
        except:
            pass

        return results

    def compress_file(self, filepath, archive_path):
        try:
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "w") as zipf:
                    zipf.write(filepath, os.path.basename(filepath))
            elif archive_path.endswith(".tar.gz"):
                with tarfile.open(archive_path, "w:gz") as tarf:
                    tarf.add(filepath, arcname=os.path.basename(filepath))
            return True
        except:
            return False

    def extract_archive(self, archive_path, extract_to):
        try:
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zipf:
                    zipf.extractall(extract_to)
            elif archive_path.endswith(".tar.gz"):
                with tarfile.open(archive_path, "r:gz") as tarf:
                    tarf.extractall(extract_to)
            return True
        except:
            return False

    def calculate_hash(self, filepath, algorithm="md5"):
        try:
            if algorithm == "md5":
                hash_func = hashlib.md5()
            elif algorithm == "sha1":
                hash_func = hashlib.sha1()
            elif algorithm == "sha256":
                hash_func = hashlib.sha256()
            else:
                return None

            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)

            return hash_func.hexdigest()
        except:
            return None

    def backup_file(self, filepath):
        try:
            backup_name = f"{os.path.basename(filepath)}.backup"
            backup_path = os.path.join(self.backup_path, backup_name)
            shutil.copy2(filepath, backup_path)
            return True
        except:
            return False

    def execute_file(self, filepath):
        try:
            # Execute any file (dangerous!)
            result = subprocess.run([filepath], capture_output=True, text=True)
            return result.stdout
        except:
            return None

    def change_permissions(self, filepath, permissions):
        try:
            os.chmod(filepath, int(permissions, 8))
            return True
        except:
            return False

    def find_duplicates(self, directory=None):
        if directory is None:
            directory = self.base_path

        hash_dict = {}
        duplicates = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    file_hash = self.calculate_hash(filepath)
                    if file_hash:
                        if file_hash in hash_dict:
                            duplicates.append((filepath, hash_dict[file_hash]))
                        else:
                            hash_dict[file_hash] = filepath
        except:
            pass

        return duplicates

    def sync_directories(self, source, destination):
        try:
            # Simple sync - copy all files from source to destination
            for root, dirs, files in os.walk(source):
                for dir in dirs:
                    src_dir = os.path.join(root, dir)
                    dst_dir = os.path.join(
                        destination, os.path.relpath(src_dir, source)
                    )
                    os.makedirs(dst_dir, exist_ok=True)

                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(
                        destination, os.path.relpath(src_file, source)
                    )
                    shutil.copy2(src_file, dst_file)

            return True
        except:
            return False

    def execute_command(self, command):
        # Dangerous command execution
        try:
            result = subprocess.check_output(command, shell=True)
            return result.decode()
        except:
            return None

    def download_file(self, url, destination):
        # No URL validation
        try:
            result = subprocess.check_output(f"curl -o {destination} {url}", shell=True)
            return True
        except:
            return False

    def upload_file(self, filepath, url):
        # No URL validation
        try:
            result = subprocess.check_output(f"curl -T {filepath} {url}", shell=True)
            return True
        except:
            return False

    def encrypt_file(self, filepath, password):
        # Weak encryption
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            encrypted = base64.b64encode(content).decode()
            with open(filepath + ".enc", "w") as f:
                f.write(encrypted)
            return True
        except:
            return False

    def decrypt_file(self, filepath, password):
        # Weak decryption
        try:
            with open(filepath, "r") as f:
                encrypted = f.read()
            decrypted = base64.b64decode(encrypted)
            with open(filepath[:-4], "wb") as f:
                f.write(decrypted)
            return True
        except:
            return False

    def serialize_data(self, data, filepath):
        # Dangerous pickle usage
        try:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
            return True
        except:
            return False

    def deserialize_data(self, filepath):
        # Dangerous pickle usage
        try:
            with open(filepath, "rb") as f:
                return pickle.load(f)
        except:
            return None

    def create_symlink(self, target, link_path):
        # No validation
        try:
            os.symlink(target, link_path)
            return True
        except:
            return False

    def mount_filesystem(self, device, mount_point):
        # Dangerous system operation
        try:
            result = subprocess.check_output(
                f"mount {device} {mount_point}", shell=True
            )
            return True
        except:
            return False

    def format_drive(self, device):
        # Extremely dangerous operation
        try:
            result = subprocess.check_output(f"format {device}", shell=True)
            return True
        except:
            return False

    def change_owner(self, filepath, user, group):
        # Dangerous operation
        try:
            result = subprocess.check_output(
                f"chown {user}:{group} {filepath}", shell=True
            )
            return True
        except:
            return False

    def create_user(self, username, password):
        # Dangerous system operation
        try:
            result = subprocess.check_output(
                f"useradd -m -p {password} {username}", shell=True
            )
            return True
        except:
            return False


def main():
    fm = FileManager()

    print("File Manager")
    print(
        "Commands: list, read, write, copy, move, delete, mkdir, rmdir, info, search, compress, extract, hash, backup, execute, chmod, duplicates, sync, cmd, download, upload, encrypt, decrypt, serialize, deserialize, symlink, mount, format, chown, useradd"
    )
    print("Type 'quit' to exit")

    while True:
        try:
            command = input("Enter command: ").strip().split()

            if not command:
                continue

            if command[0] == "quit":
                break
            elif command[0] == "list":
                files = fm.list_files()
                for file in files:
                    print(file)
            elif command[0] == "read" and len(command) > 1:
                content = fm.read_file(command[1])
                if content:
                    print(content)
                else:
                    print("Error reading file")
            elif command[0] == "write" and len(command) > 2:
                success = fm.write_file(command[1], command[2])
                print("File written" if success else "Error writing file")
            elif command[0] == "copy" and len(command) > 2:
                success = fm.copy_file(command[1], command[2])
                print("File copied" if success else "Error copying file")
            elif command[0] == "move" and len(command) > 2:
                success = fm.move_file(command[1], command[2])
                print("File moved" if success else "Error moving file")
            elif command[0] == "delete" and len(command) > 1:
                success = fm.delete_file(command[1])
                print("File deleted" if success else "Error deleting file")
            elif command[0] == "mkdir" and len(command) > 1:
                success = fm.create_directory(command[1])
                print("Directory created" if success else "Error creating directory")
            elif command[0] == "rmdir" and len(command) > 1:
                success = fm.delete_directory(command[1])
                print("Directory deleted" if success else "Error deleting directory")
            elif command[0] == "info" and len(command) > 1:
                info = fm.get_file_info(command[1])
                if info:
                    print(
                        f"Size: {info['size']}, Modified: {info['modified']}, Permissions: {info['permissions']}"
                    )
                else:
                    print("Error getting file info")
            elif command[0] == "search" and len(command) > 1:
                results = fm.search_files(command[1])
                for result in results:
                    print(result)
            elif command[0] == "compress" and len(command) > 2:
                success = fm.compress_file(command[1], command[2])
                print("File compressed" if success else "Error compressing file")
            elif command[0] == "extract" and len(command) > 2:
                success = fm.extract_archive(command[1], command[2])
                print("Archive extracted" if success else "Error extracting archive")
            elif command[0] == "hash" and len(command) > 1:
                file_hash = fm.calculate_hash(command[1])
                if file_hash:
                    print(f"Hash: {file_hash}")
                else:
                    print("Error calculating hash")
            elif command[0] == "backup" and len(command) > 1:
                success = fm.backup_file(command[1])
                print("File backed up" if success else "Error backing up file")
            elif command[0] == "execute" and len(command) > 1:
                output = fm.execute_file(command[1])
                if output:
                    print(output)
                else:
                    print("Error executing file")
            elif command[0] == "chmod" and len(command) > 2:
                success = fm.change_permissions(command[1], command[2])
                print(
                    "Permissions changed" if success else "Error changing permissions"
                )
            elif command[0] == "duplicates":
                duplicates = fm.find_duplicates()
                for dup in duplicates:
                    print(f"Duplicate: {dup[0]} and {dup[1]}")
            elif command[0] == "sync" and len(command) > 2:
                success = fm.sync_directories(command[1], command[2])
                print("Directories synced" if success else "Error syncing directories")
            elif command[0] == "cmd" and len(command) > 1:
                cmd = " ".join(command[1:])
                output = fm.execute_command(cmd)
                if output:
                    print(output)
                else:
                    print("Error executing command")
            elif command[0] == "download" and len(command) > 2:
                success = fm.download_file(command[1], command[2])
                print("File downloaded" if success else "Error downloading file")
            elif command[0] == "upload" and len(command) > 2:
                success = fm.upload_file(command[1], command[2])
                print("File uploaded" if success else "Error uploading file")
            elif command[0] == "encrypt" and len(command) > 2:
                success = fm.encrypt_file(command[1], command[2])
                print("File encrypted" if success else "Error encrypting file")
            elif command[0] == "decrypt" and len(command) > 2:
                success = fm.decrypt_file(command[1], command[2])
                print("File decrypted" if success else "Error decrypting file")
            elif command[0] == "serialize" and len(command) > 2:
                data = {"test": "data"}
                success = fm.serialize_data(data, command[1])
                print("Data serialized" if success else "Error serializing data")
            elif command[0] == "deserialize" and len(command) > 1:
                data = fm.deserialize_data(command[1])
                if data:
                    print(f"Data: {data}")
                else:
                    print("Error deserializing data")
            elif command[0] == "symlink" and len(command) > 2:
                success = fm.create_symlink(command[1], command[2])
                print("Symlink created" if success else "Error creating symlink")
            elif command[0] == "mount" and len(command) > 2:
                success = fm.mount_filesystem(command[1], command[2])
                print("Filesystem mounted" if success else "Error mounting filesystem")
            elif command[0] == "format" and len(command) > 1:
                success = fm.format_drive(command[1])
                print("Drive formatted" if success else "Error formatting drive")
            elif command[0] == "chown" and len(command) > 3:
                success = fm.change_owner(command[1], command[2], command[3])
                print("Owner changed" if success else "Error changing owner")
            elif command[0] == "useradd" and len(command) > 2:
                success = fm.create_user(command[1], command[2])
                print("User created" if success else "Error creating user")
            else:
                print("Invalid command or missing arguments")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except:
            print("An error occurred")


if __name__ == "__main__":
    main()
