import os, sys, zipfile, csv, time


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


autofill_data = []


def read_autofill_data(user_num):
    with open(resource_path('autofill.csv'), 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for i, row in enumerate(reader):
            if i == user_num:
                autofill_data.append(row)
0

read_autofill_data(0)
print(autofill_data)