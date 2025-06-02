import subprocess

modules = [
    "main.py",
    "kafka_consumer.py",
    "storage.py",
    "tests/test_main.py"
]


command = [
    "pdoc",
    *modules,
    "-o docs"
]

subprocess.run(command)
