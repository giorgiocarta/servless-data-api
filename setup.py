import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="servless-data-api",
    version="0.0.1",
    description="A servless repo",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Giorgio Carta",

    package_dir={"": "./"},
    packages=[''],

    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 1 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "Typing :: Typed"
    ]

)
