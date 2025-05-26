from setuptools import setup, find_packages

setup(
    name='src',
    version='0.1.0',
    author='Aman Jain',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True, 
    package_data={
        "src.jd_extractor_agent": ["config.yml", "data/*.txt"], 
        "src.resume_extractor_agent": ["config.yml", "data/*.txt"],
        "src.education_matching": ["config.yml"],
        "src.experience_matching": ["config.yml"],
        "src.skill_matching": ["config.yml"],
        "src.tools_matching": ["config.yml"],
        "src.certification_matching": ["config.yml"],
        "src.designation_matching": ["config.yml"],
        "src.utils": ["config.yml"],
    },
    install_requires=[
    "dotenv==0.9.9",
    "python-dotenv==1.1.0",
    "openai==1.77.0",
    "cryptography==44.0.3",
    "typing==3.7.4.3",
    "pyyaml",
    "pytest==8.3.5",
    "pytest-mock==3.14.0",
    "pytest-cov==6.1.1",
    "pytest-xdist==3.6.1",
    "pytest-rerunfailures==15.1",
    "flaky==3.8.1",
    "sentence-transformers==4.1.0",
    "scikit-learn==1.6.1",
    "pandas==2.2.3",
    "numpy==2.2.5",
    "regex==2024.11.6",
    "tqdm==4.67.1",
    "ruff==0.11.8",
    "bandit==1.8.3",
    "pylint==3.3.6",
    "psutil==7.0.0",
    "pymupdf==1.25.5",
    "pdf2image==1.17.0",
    "pillow==11.2.1",
    "requests==2.32.3",
    "beautifulsoup4==4.13.4",
    "trafilatura==2.0.0",
    "selenium==4.32.0",
    "Flask==3.1.0",
    "flask-cors==5.0.1",
    "flasgger==0.9.7.1",
    "bcrypt==4.3.0",
    "PyJWT==2.10.1",
    "pymongo==4.12.1",
    "mongomock==4.3.0",
    "torch==2.7.0",
    "huggingface-hub==0.30.2",
    "gunicorn==20.1.0",
    "google-auth==2.40.2",
    "google-auth-oauthlib==1.2.2"
]
)

# To install the package, run the following command in the terminal:
# pip install .
# To uninstall the package, run the following command in the terminal:
# pip uninstall src