black log_my_printer tests
autoflake -r --in-place log_my_printer tests
isort log_my_printer tests
mypy log_my_printer tests
flake8 log_my_printer tests
pylint log_my_printer tests