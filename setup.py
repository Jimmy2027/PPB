from setuptools import setup

setup(
    name="PPB",
    version="9999",
    description="Your Pythonic Personal Paste Bin",
    author="Hendrik Klug",
    author_email="klugh@ethz.ch",
    url="https://github.com/Jimmy2027/PPB",
    keywords=["personal-paste-bin"],
    packages=["ppb"],
    entry_points={
        "console_scripts": ["ppb = ppb.__main__:main"]
    },
    provides=["ppb"],
    python_requires='>=3.7',
)
