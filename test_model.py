import csv
import pickle
import numpy as np
from sklearn.model_selection import train_test_split


def reading_data(filename):
    x = []
    y = []
    column_names = []
    data = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                column_names = [a for a in row]
                line_count += 1
                print(column_names)
            else:
                data.append([d for d in row])
                if row[1]=='n':
                    y.append(0)
                else:
                    y.append(1)
                # y.append(row[1])
                x.append([float(row[i]) for i in range(len(row)) if i != 1])
                # x.append([row[i] for i in range(len(row)) if i != 1 or i!=0])
                line_count += 1
        print(f'Processed {line_count} lines.')
    return column_names, np.array(x), np.array(y), data


column_names_temp, x, y = reading_data("dataset/features_matrix.csv")
column_names_temp.remove("flag")

# remove first column
column_names_temp.remove("reqId")
x = np.delete(x, obj=0, axis=1)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)

print(x_test)
# now open the js model and test with it
file = open('jsFiles/realclassifier.min.js', 'r')
code = file.read()
file.close()


import js2py
data=js2py.eval_js(code)
# print(data)