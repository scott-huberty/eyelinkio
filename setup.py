import os
import platform
import subprocess
import sys
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from wheel.bdist_wheel import bdist_wheel

class CMakeExtension(Extension):
    """Dummy wrapper for CMake build."""
    def __init__(self, name, py_limited_api=False):
        super().__init__(name, sources=[], py_limited_api=py_limited_api)

class build_ext(_build_ext):
    def run(self):
        src_dir = (Path(__file__).parent / "src").resolve()
        libedf2asc_dir = src_dir / "libedf2asc"
        assert libedf2asc_dir.exists(), f"{libedf2asc_dir} does not exist"
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={build_temp}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ]
        build_args = ["--config", "Release", "--", "-j4"]
        subprocess.check_call(["cmake", str(libedf2asc_dir)] + cmake_args, cwd=build_temp)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=build_temp)

    def build_extension(self, ext):
        pass

class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if python.startswith("cp"):
            return "cp39", "abi3", plat
        return python, abi, plat

setup(
    ext_modules=[CMakeExtension("edf2asc", py_limited_api=True)],
    cmdclass={
        "build_ext": build_ext,
        "bdist_wheel": bdist_wheel_abi3,
    },
)