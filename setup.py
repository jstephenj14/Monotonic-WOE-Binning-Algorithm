import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monotonic_binning", # Replace with your own username
    version="0.0.1",
    author="John Selvam",
    author_email="jstephenj14@gmail.com",
    description="Monotonic Variable Binning by WOE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jstephenj14/Monotonic-WOE-Binning-Algorithm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)