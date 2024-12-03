import os

dirs = [
    'static',
    'templates',
    'agentes',
]

base_dir = os.path.dirname(os.path.abspath(__file__))

for dir_name in dirs:
    dir_path = os.path.join(base_dir, dir_name)
    os.makedirs(dir_path, exist_ok=True)
