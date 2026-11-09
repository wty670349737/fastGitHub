"""让 pytest 能从项目根目录导入顶层模块。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
