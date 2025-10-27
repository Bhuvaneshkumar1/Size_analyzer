import os
import subprocess
import sys
import argparse
import hashlib
import json
import csv
from tqdm import tqdm
from threading import Lock
from collections import defaultdict

lock = Lock()

# -------------------------
# Helper Functions
# -------------------------

def human_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B','KB','MB','GB','TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_item_size(path, pbar=None, max_depth=None, current_depth=0, ignore_hidden=False):
    """Return size of file or folder recursively."""
    if os.path.isfile(path):
        try:
            size = os.path.getsize(path)
        except (FileNotFoundError, PermissionError, OSError):
            size = 0
        if pbar:
            with lock:
                pbar.update(size)
                pbar.set_postfix_str(f"Scanning: {path}")
        return size
    elif os.path.isdir(path):
        if max_depth is not None and current_depth > max_depth:
            return 0
        total = 0
        try:
            entries = list(os.scandir(path))
        except (PermissionError, OSError):
            return 0
        for entry in entries:
            if ignore_hidden and entry.name.startswith('.'):
                continue
            total += get_item_size(entry.path, pbar, max_depth, current_depth + 1, ignore_hidden)
        return total
    return 0

def find_all_items(root_path, max_depth=None, ignore_hidden=False):
    """Recursively yield all files and folders."""
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True, followlinks=False):
        if ignore_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            filenames = [f for f in filenames if not f.startswith('.')]
        if max_depth is not None:
            rel_depth = dirpath.replace(root_path, '').count(os.sep)
            if rel_depth >= max_depth:
                dirnames[:] = []
                filenames = []
        for dirname in dirnames:
            yield os.path.join(dirpath, dirname)
        for filename in filenames:
            yield os.path.join(dirpath, filename)

def compute_hash(path, block_size=65536):
    """Compute MD5 hash for a file."""
    md5 = hashlib.md5()
    try:
        with open(path,'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                md5.update(block)
        return md5.hexdigest()
    except Exception:
        return None

def open_item(path):
    """Open file or folder cross-platform."""
    try:
        if os.path.isdir(path):
            if sys.platform.startswith('win'):
                subprocess.run(["explorer", os.path.normpath(path)])
            elif sys.platform.startswith('linux'):
                subprocess.run(["xdg-open", path])
            elif sys.platform.startswith('darwin'):
                subprocess.run(["open", path])
        elif os.path.isfile(path):
            if sys.platform.startswith('win'):
                os.startfile(path)
            elif sys.platform.startswith('linux'):
                subprocess.run(["xdg-open", path])
            elif sys.platform.startswith('darwin'):
                subprocess.run(["open", path])
    except Exception as e:
        print(f"Failed to open {path}: {e}")

# -------------------------
# Main Analysis Function
# -------------------------

def analyze_folder(root_path, top_n=10, max_depth=None, ignore_hidden=False, min_size=0, detect_duplicates=False, export_csv=None, export_json=None):
    print("Estimating total bytes for progress bar...")
    total_bytes = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        if ignore_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            filenames = [f for f in filenames if not f.startswith('.')]
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                if not os.path.islink(fp):
                    total_bytes += os.path.getsize(fp)
            except Exception:
                continue
    print(f"Total bytes to scan: {human_size(total_bytes)}")

    items = list(find_all_items(root_path, max_depth, ignore_hidden))
    results = []
    file_types = defaultdict(int)
    duplicates = defaultdict(list)

    with tqdm(total=total_bytes, desc="Scanning bytes", unit="B", unit_scale=True, unit_divisor=1024) as pbar:
        for path in items:
            size = get_item_size(path, pbar, max_depth, ignore_hidden=ignore_hidden)
            if size < min_size:
                continue
            results.append((path, size))
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower() or "NoExt"
                file_types[ext] += size
                if detect_duplicates:
                    h = compute_hash(path)
                    if h:
                        duplicates[h].append(path)

    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:top_n]

    print("\nTop {} largest items:\n".format(top_n))
    for i, (path, size) in enumerate(top_results, 1):
        type_name = "Folder" if os.path.isdir(path) else "File"
        print(f"{i}. [{type_name}] {path} — {human_size(size)}")

    print("\nFile type breakdown:")
    for ext, size in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
        print(f"{ext}: {human_size(size)}")

    if detect_duplicates:
        print("\nDuplicate files found:")
        for h, paths in duplicates.items():
            if len(paths) > 1:
                print(f"Hash {h}:")
                for p in paths:
                    print(f"   {p}")

    if top_results:
        print(f"\nOpening largest item: {top_results[0][0]}")
        open_item(top_results[0][0])

    if export_csv:
        with open(export_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Size(Bytes)", "Type"])
            for path, size in results:
                writer.writerow([path, size, "Folder" if os.path.isdir(path) else "File"])
        print(f"CSV report saved: {export_csv}")

    if export_json:
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump([{"path": p, "size": s, "type": "Folder" if os.path.isdir(p) else "File"} for p,s in results], f, indent=2)
        print(f"JSON report saved: {export_json}")

# -------------------------
# Command-line Interface
# -------------------------

def main():
    parser = argparse.ArgumentParser(description="Professional Disk Analysis Tool")
    parser.add_argument("path", help="Folder path to analyze")
    parser.add_argument("--top", type=int, default=10, help="Top N largest items")
    parser.add_argument("--max-depth", type=int, default=None, help="Maximum recursive depth")
    parser.add_argument("--ignore-hidden", action='store_true', help="Ignore hidden files/folders")
    parser.add_argument("--min-size", type=int, default=0, help="Minimum size in bytes to consider")
    parser.add_argument("--detect-duplicates", action='store_true', help="Detect duplicate files")
    parser.add_argument("--export-csv", help="Export results to CSV")
    parser.add_argument("--export-json", help="Export results to JSON")

    args = parser.parse_args()

    analyze_folder(
        args.path,
        top_n=args.top,
        max_depth=args.max_depth,
        ignore_hidden=args.ignore_hidden,
        min_size=args.min_size,
        detect_duplicates=args.detect_duplicates,
        export_csv=args.export_csv,
        export_json=args.export_json
    )

if __name__ == "__main__":
    main()
