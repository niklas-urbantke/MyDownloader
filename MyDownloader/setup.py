"""
Setup Configuration for MyDownloader
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README_V3.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="mydownloader",
    version="3.0.0",
    author="UST-Germany",
    author_email="",
    description="Ultimate Music & Video Downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mydownloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Multimedia :: Video :: Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mydownloader=mydownloader.__main__:main",
        ],
        "gui_scripts": [
            "mydownloader-gui=mydownloader.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mydownloader": [
            "assets/*",
            "assets/icons/*",
        ],
    },
    zip_safe=False,
    keywords="youtube downloader music video mp3 playlist",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mydownloader/issues",
        "Source": "https://github.com/yourusername/mydownloader",
    },
)
