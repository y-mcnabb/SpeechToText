import os


def get_size_mb(file):
    """Get filesize in MB"""
    size_bytes = os.path.getsize(file)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def suffix_to_filename(file_path, suffix):
    """Adds a suffix to the end of the filename (but before the extension)"""
    base_name, extension = os.path.splitext(file_path)
    new_file_path = f"{base_name}{suffix}{extension}"
    return new_file_path
