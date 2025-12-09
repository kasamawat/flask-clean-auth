import os
import sys

# เพิ่ม path ของ root project (โฟลเดอร์ที่มีไฟล์ tests/ และ src/) เข้า sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)