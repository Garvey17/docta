"""Pytest configuration ensuring data_pipeline and project root are on sys.path."""

import sys
from pathlib import Path

# Add project root and data_pipeline dir to sys.path
data_pipeline_dir = Path(__file__).resolve().parent
project_root = data_pipeline_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(data_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(data_pipeline_dir))
