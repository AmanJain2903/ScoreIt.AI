# To install python package

### For editable mode -> pip install -e .
### For normal mode -> pip install . 


# To run pytests

### COVERAGE_FILE=code_coverage/.coverage pytest --cov=src --cov-report=html:code_coverage/coverage_report tests/

### Only unit tests -> pytest -m unit / pytest --cov=src -m unit tests/
### Only integration tests -> pytest -m integration / pytest --cov=src -m integration tests/
## To run both -> pytest


