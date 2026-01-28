"""
DEPRECATED: This module is no longer used in the project after v1.0.0.
This module contains the InstallationManager class, which is used to manage
the installation of dependencies.
"""

import os
import platform
import subprocess
from pathlib import Path
import urllib.request


class InstallationManager:
    """用于管理依赖项安装的类"""

    def __init__(self):
        self.root_dir = Path.cwd()
        self.conda_dir = self.root_dir / "conda"
        self.env_name = "open_llm_vtuber"
        self.python_version = "3.10"

        # Platform specific settings
        self.platform = platform.system().lower()
        if self.platform == "windows":
            self.conda_executable = self.conda_dir / "Scripts" / "conda.exe"
            self.activate_script = self.conda_dir / "Scripts" / "activate.bat"
        else:
            self.conda_executable = self.conda_dir / "bin" / "conda"
            self.activate_script = self.conda_dir / "bin" / "activate"

    def download_miniconda(self):
        """下载适当的 Miniconda 安装程序"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "windows":
            url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
            installer = self.root_dir / "miniconda_installer.exe"
        elif system == "darwin":
            if machine == "arm64":
                url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            else:
                url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            installer = self.root_dir / "miniconda_installer.sh"
        else:  # Linux
            if machine == "aarch64":
                url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
            else:
                url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            installer = self.root_dir / "miniconda_installer.sh"

        print(f"Downloading Miniconda from {url}")
        urllib.request.urlretrieve(url, installer)
        return installer

    def install_miniconda(self, installer):
        """将 Miniconda 安装到本地目录"""
        if platform.system().lower() == "windows":
            subprocess.run(
                [str(installer), "/S", "/D=" + str(self.conda_dir)], check=True
            )
        else:
            os.chmod(installer, 0o755)
            subprocess.run(
                ["bash", str(installer), "-b", "-p", str(self.conda_dir)], check=True
            )

        # Clean up installer
        installer.unlink()

    def create_environment(self):
        """创建带有 Python 3.10 的 conda 环境"""
        subprocess.run(
            [
                str(self.conda_executable),
                "create",
                "-y",
                "-n",
                self.env_name,
                f"python={self.python_version}",
            ],
            check=True,
        )

    def install_conda_dependencies(self):
        """安装 conda 依赖项"""
        subprocess.run(
            [
                str(self.conda_executable),
                "install",
                "-y",
                "-n",
                self.env_name,
                "ffmpeg",
                "git",
            ],
            check=True,
        )

    def install_pip_dependencies(self):
        """安装 pip 依赖项"""
        # Activate environment first
        if platform.system().lower() == "windows":
            activate_cmd = f"call {self.activate_script} {self.env_name}"
        else:
            activate_cmd = f"source {self.activate_script} {self.env_name}"

        # Install requirements.txt
        pip_install_cmd = f"{activate_cmd} && pip install -r requirements.txt"
        pip_install_cmd += (
            " && pip install torch torchaudio funasr modelscope huggingface_hub onnx"
        )

        if platform.system().lower() == "windows":
            subprocess.run(pip_install_cmd, shell=True, check=True)
        else:
            subprocess.run(["bash", "-c", pip_install_cmd], check=True)

    def check_environment(self):
        """检查 'open-llm-vtuber' 环境是否存在，如果不存在则安装"""
        result = subprocess.run(
            [str(self.conda_executable), "env", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        if self.env_name not in result.stdout:
            self.create_environment()
            self.install_conda_dependencies()
            self.install_pip_dependencies()

    def setup(self):
        """运行完整的设置过程"""
        if not self.conda_dir.exists():
            installer = self.download_miniconda()
            self.install_miniconda(installer)

        # Create environment if it doesn't exist
        self.check_environment()
