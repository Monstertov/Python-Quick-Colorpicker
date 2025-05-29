from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quick-colorpicker",
    version="1.0.0",
    author="Monstertov",
    author_email="rob@monstertov.nl",  # Replace with your email
    description="A professional cross-platform color picking utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Monstertov/quick-colorpicker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pynput==1.7.6",
        "pyautogui==0.9.54",
        "Pillow==10.2.0",
        "pyperclip>=1.8.2",
        "rich>=12.0.0",
    ],
    entry_points={
        "console_scripts": [
            "quick-colorpicker=quick_colorpicker.main:main",
        ],
    },
) 