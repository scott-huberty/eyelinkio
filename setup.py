import os
import platform
import pprint
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext as _build_ext
from wheel.bdist_wheel import bdist_wheel

if platform.system() == "Linux":
    lib_files = ["libedf2asc.so"]
elif platform.system() == "Darwin":
    lib_files = ["libedf2asc.dylib"]
elif platform.system() == "Windows":
    lib_files = ["edf2asc.dll"]
else:
    raise Exception(f"Unsupported platform {platform.system()}")

class CMakeExtension(Extension):
    """Dummy Wrapper for CMake build"""

    def __init__(self, name, py_limited_api=True):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[], py_limited_api=py_limited_api)


class build_ext(_build_ext):
    def run(self):
        """Build libedf2asc with cmake as part of the extension build process."""
        src_dir = Path(__file__).parent / "src" / "libedf2asc"
        assert src_dir.exists(), f"Source directory {src_dir} does not exist"
        # This is an unfortunate hack to get new env vars within a GH Actions step
        # (no way to use before-build to inject env vars back into the environment)
        check_env = os.environ
        if "GITHUB_ENV" in check_env:
            print("Using GITHUB_ENV instead of os.environ")  # noqa: T201
            check_env = dict(
                line.split("=", maxsplit=1)
                for line in Path(os.environ["GITHUB_ENV"]).read_text().splitlines()
                if "=" in line
            )
            pprint.pprint(check_env)  # noqa: T203
        with TemporaryDirectory() as build_dir:  # str
            args = [
                "cmake",
                "-S",
                str(src_dir),
                "-B",
                build_dir,
                "-DCMAKE_BUILD_TYPE=Release",
                f"-DPython3_EXECUTABLE={sys.executable}",
            ]
        for key in (
            "CMAKE_GENERATOR",
            "CMAKE_GENERATOR_PLATFORM",
            "Python3_SABI_LIBRARY"
        ):
            if key in check_env:
                args.append(f"-D{key}={check_env[key]}")
        subprocess.run(args, check=True)
        subprocess.run(
            ["cmake", "--build", build_dir, "--config", "Release"], check=True
        )
        # locate the built files and copy them to libedf2asc
        build_dir = Path(build_dir)
        if platform.system() == "Windows":
            libedf2asc = build_dir / "Release" / lib_files[0]
            libedfapi_dir = src_dir.parent / "libedfapi" / "windows"
        elif platform.system() == "Linux":
            libedf2asc = build_dir / lib_files[0]
            libedfapi_dir = src_dir.parent / "libedfapi" / "linux"
        elif platform.system() == "Darwin":
            libedf2asc = build_dir / lib_files[0]
            libedfapi_dir = src_dir.parent / "libedfapi" / "macos"
        else:
            raise Exception(f"Unsupported platform {platform.system()}")
        assert libedf2asc.exists(), f"Built library {libedf2asc} does not exist"
        assert libedfapi_dir.exists(), f"edfapi directory {libedfapi_dir} does not exist"
        dst = Path(self.build_lib) / "eyelinkio" / "libedfapi" / libedf2asc.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"Moving {libedf2asc.name} to {dst}")  # noqa: T201
        shutil.move(lib, dst)
        # Copy the edfapi library
        print(f"Copying {libedfapi_dir} to {dst.parent}")  # noqa: T201
        shutil.copytree(libedfapi_dir, dst.parent / "libedfapi")
    super.run()

# Adapted from 
# https://github.com/mscheltienne/antio/setup.py
class bdist_wheel_abi3(bdist_wheel):  # noqa: D101
    def get_tag(self):  # noqa: D102
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            # on CPython, our wheels are abi3 and compatible back to 3.2,
            # but let's set it to our min version anyway
            return "cp39", "abi3", plat

        return python, abi, plat


setup(
    ext_modules=[CMakeExtension("libedf2asc", py_limited_api=True)],
    cmdclass={
        "build_ext": build_ext,
        "bdist_wheel": bdist_wheel_abi3,
    },
)