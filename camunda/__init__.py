from pathlib import Path

version_file_path = Path(__file__).parent / 'VERSION'
__version__ = version_file_path.read_text().strip()
