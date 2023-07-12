import shutil
from pathlib import Path

# 获取当前文件夹的路径
current_dir = Path(".")
# 遍历当前文件夹及其所有子文件夹
for path in current_dir.glob("**/__pycache__"):
    # 删除文件夹及其中的所有内容
    shutil.rmtree(path)
