import subprocess

modules = [
    "main.py",
    "kafka_consumer.py",
    "storage.py",
    "tests/test_main.py"
]

port = "8081"

command = [
    "pdoc",
    *modules,
    "--port", port,
    "--host", "0.0.0.0"
]

subprocess.run(command)
