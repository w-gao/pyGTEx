from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# test_requirements = [
#     "pytest",
#     "pytest-cov"
# ]


setup(
    name="pyGTEx",
    version="0.2.0",
    description="Retrieve Genotype-Tissue Expression (GTEx) data programmatically.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/w-gao/pyGTEx",
    author="William Gao",
    author_email="me@wlgao.com",
    packages=find_packages(include=["pyGTEx", "pyGTEx.*"]),
    python_requires=">=3.7",
    install_requires=requirements,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="GTEx",
)
