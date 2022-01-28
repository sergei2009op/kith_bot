import os, sys, csv


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


def read_file(file_name):
    content = []
    extension = file_name.split('.')[-1]

    try:
        with open(resource_path(file_name), 'r', encoding='utf-8') as f:
            if extension == 'txt':
                content = f.readlines()
            elif extension == 'csv':
                content = list(csv.DictReader(f, delimiter=','))
    except:
        print(f'{file_name} not found')

    return content


def write_file(file_name, content):
    with open(resource_path(file_name), 'w', encoding='utf-8') as f:
        f.writelines("\n".join(content))