from setuptools import setup, find_packages

setup(
    name='src',
    version='0.2.0',
    author='Aman Jain',
    packages=find_packages(),
    include_package_data=True, 
    package_data={
        "src.jd_extractor_agent": ["config.yml", "data/*.txt"], 
        "src.resume_extractor_agent": ["config.yml", "data/*.txt"],
    },
    install_requires=[
        'dotenv',
        'openai',
        'cryptography',
        'typing',
        'pyyaml',
        'pytest',
        'pytest-mock',
        'pytest-cov',
    ],
)

# To install the package, run the following command in the terminal:
# pip install .
# To uninstall the package, run the following command in the terminal:
# pip uninstall src