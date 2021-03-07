from setuptools import setup, find_packages

with open("README.md", "r") as fh:
  long_description = fh.read()

with open("requirements.txt") as fh:
  install_requires = fh.read()

setup(
  name="w-subs",
  version="0.0.1",
  author="wwwwwwww",
  author_email="wvvwvvvvwvvw@gmail.com",
  description="",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/wwww-wwww/subs",
  install_requires=install_requires,
  packages=find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.6",
  entry_points={
    "console_scripts": [
      "asstext=tools.asstext:main",
      "downsize=tools.downsize:main",
      "fontname=tools.fontname:main",
      "midiass=tools.midiass:main",
    ],
  },
)
