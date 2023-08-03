from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="gologin_py", 
    version="0.1",
    packages=["gologin_py"],
    package_dir={"gologin_py": "."},
    install_requires=requirements,
)