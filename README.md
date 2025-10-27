---


# Size Analyzer

A **professional disk and folder analysis tool** built in Python.  
It scans directories recursively, measures sizes of files and folders, detects duplicates, and exports detailed reports in CSV and JSON formats.  

Whether you’re cleaning up a cluttered drive or profiling massive data directories, **Size Analyzer** gives you full situational awareness of your storage.

---

## 🔧 Features

- 📁 **Recursive Folder Analysis** – Measure file and directory sizes at any depth  
- 🚫 **Hidden File Ignoring** – Skip hidden files/folders with one flag  
- 🧮 **Human-Readable Sizes** – Auto converts bytes to KB, MB, GB, etc.  
- 🧩 **File Type Breakdown** – Summarizes total space per file extension  
- 🧍 **Duplicate Detection** – Find identical files using MD5 hashing  
- 📊 **Export Options** – Save results to CSV or JSON for external processing  
- ⚙️ **Progress Bar** – Visual progress tracking with `tqdm`  
- 🪟 **Cross-Platform File Opening** – Works on Windows, Linux, and macOS  

---

## 🧰 Requirements

- Python 3.8+
- Dependencies:
  ```bash
  pip install tqdm

*(Everything else comes from the Python standard library.)*

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/<yourusername>/Size_analyzer.git
cd Size_analyzer
```

Optionally, make it globally available:

```bash
pip install .
```

---

## 💻 Usage

### Basic Command

```bash
python size_analyzer.py <folder_path>
```

### Optional Arguments

| Argument              | Type  | Description                                |
| --------------------- | ----- | ------------------------------------------ |
| `--top`               | `int` | Show top N largest items (default: 10)     |
| `--max-depth`         | `int` | Limit recursive scan depth                 |
| `--ignore-hidden`     | flag  | Ignore hidden files and folders            |
| `--min-size`          | `int` | Only include items larger than given bytes |
| `--detect-duplicates` | flag  | Detect duplicate files by MD5 hash         |
| `--export-csv`        | `str` | Save results to a CSV file                 |
| `--export-json`       | `str` | Save results to a JSON file                |

---

### Example Commands

**Analyze a folder deeply and export results:**

```bash
python size_analyzer.py /path/to/folder --top 20 --export-csv report.csv
```

**Ignore hidden files and limit depth:**

```bash
python size_analyzer.py ./project --ignore-hidden --max-depth 3
```

**Detect duplicate files larger than 1MB:**

```bash
python size_analyzer.py /data --min-size 1048576 --detect-duplicates
```

---
**if you to check each and every item not considering the size use 0 in the --min-size** 
```bash
python size_analyzer.py /data --min-size 0 --detect-duplicates
```

## 📦 Output Examples

### Console Output

```
Estimating total bytes for progress bar...
Total bytes to scan: 2.41 GB
Scanning bytes: 100%|████████████████████| 2.41G/2.41G [00:45<00:00, 54.1MB/s]

Top 10 largest items:

1. [File] /data/video.mp4 — 1.02 GB
2. [Folder] /data/archive — 980.30 MB
...

File type breakdown:
.mp4: 1.20 GB
.zip: 980.30 MB
.csv: 12.4 MB
```

### Exported CSV

| Path            | Size(Bytes) | Type   |
| --------------- | ----------- | ------ |
| /data/video.mp4 | 1099511627  | File   |
| /data/archive   | 1023983042  | Folder |

---

## ⚡ Performance Tips

* Use `--max-depth` for massive drives to avoid endless recursion.
* `--ignore-hidden` speeds up scans on Unix-like systems.
* Duplicate detection (`--detect-duplicates`) increases runtime due to hashing; use it wisely.

---

## 🧠 Design Notes

* Thread-safe progress updates using `Lock` from `threading`
* Uses `hashlib` for secure MD5 checksum comparison
* JSON/CSV exports are UTF-8 encoded for universal compatibility
* Handles permission errors gracefully

---

## 🪪 License

This project is licensed under the **MIT License**.
You can freely modify, distribute, and integrate it, as long as you include attribution.

---

## 🧑‍💻 Author

**Devil King**
Application and Web Developer
*Building small tools to rule big systems.*

---



---
This README covers:  
- Command-line usage  
- Dependencies  
- Examples  
- File structure clarity  
- Clean markdown formatting  
