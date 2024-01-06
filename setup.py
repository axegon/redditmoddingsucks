from codecs import open as fopen
from setuptools import setup, find_packages  # type: ignore
from setuptools import find_namespace_packages, setup  # type: ignore

setup(
    name="redditmoddingsucks",
    version="0.1.0",
    url="https://github.com/axegon/redditmoddingsucks",
    packages=find_namespace_packages(include=["redditmoddingsucks.*"]),
    python_requires=">=3.11.0",
    install_requires=fopen("requirements.txt").read().split("/n"),
    package_data={"": ["commitment.html", "py.typed", "*.md"]},
    entry_points={
        "console_scripts": [
            "redditmodqueue=redditmoddingsucks.cli:modqueue_client",
        ],
    },
)
