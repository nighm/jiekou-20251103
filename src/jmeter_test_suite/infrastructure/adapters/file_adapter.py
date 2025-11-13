"""TODO: add documentation."""

import os
import shutil
from pathlib import Path


class FileAdapter:
    """TODO: add documentation."""

    def __init__(self) -> None:
        """TODO: add documentation."""

    def create_directory(self, directory_path: str) -> bool:
        """TODO: add documentation."""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
            return False

    def file_exists(self, file_path: str) -> bool:
        """TODO: add documentation."""
        return os.path.exists(file_path)

    def directory_exists(self, directory_path: str) -> bool:
        """TODO: add documentation."""
        return os.path.exists(directory_path) and os.path.isdir(directory_path)

    def get_file_size(self, file_path: str) -> int | None:
        """TODO: add documentation."""
        try:
            if self.file_exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            print(f"获取文件大小失败: {str(e)}")
            return None

    def list_files(self, directory_path: str, pattern: str = "*") -> list[str]:
        """TODO: add documentation."""
        try:
            if not self.directory_exists(directory_path):
                return []

            path = Path(directory_path)
            files = list(path.glob(pattern))
            return [str(f) for f in files if f.is_file()]
        except Exception as e:
            print(f"列出文件失败: {str(e)}")
            return []

    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """TODO: add documentation."""
        try:
            # Create目标目录
            dst_dir = os.path.dirname(dst_path)
            if dst_dir:
                self.create_directory(dst_dir)

            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            print(f"复制文件失败: {str(e)}")
            return False

    def move_file(self, src_path: str, dst_path: str) -> bool:
        """TODO: add documentation."""
        try:
            # Create目标目录
            dst_dir = os.path.dirname(dst_path)
            if dst_dir:
                self.create_directory(dst_dir)

            shutil.move(src_path, dst_path)
            return True
        except Exception as e:
            print(f"移动文件失败: {str(e)}")
            return False

    def delete_file(self, file_path: str) -> bool:
        """TODO: add documentation."""
        try:
            if self.file_exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

    def delete_directory(self, directory_path: str) -> bool:
        """TODO: add documentation."""
        try:
            if self.directory_exists(directory_path):
                shutil.rmtree(directory_path)
            return True
        except Exception as e:
            print(f"删除目录失败: {str(e)}")
            return False

    def read_file_content(self, file_path: str, encoding: str = "utf-8") -> str | None:
        """TODO: add documentation."""
        try:
            if not self.file_exists(file_path):
                return None

            with open(file_path, encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return None

    def write_file_content(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> bool:
        """TODO: add documentation."""
        try:
            # Create directory
            directory = os.path.dirname(file_path)
            if directory:
                self.create_directory(directory)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败: {str(e)}")
            return False
