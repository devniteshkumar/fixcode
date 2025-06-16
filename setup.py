from setuptools import setup, find_packages

setup(
    name="fixcode",
    version="1.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "fixcode=fixcode.cli:main",
        ],
    },
)
