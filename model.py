import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
from sklearn_porter import Porter

def reading_data(filename):
    x = []
    y = []
    column_names = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                column_names = [a for a in row]
                line_count += 1
                # print(column_names)
            else:
                y.append(row[1])
                # if row[1]=='n':
                #     y.append(0)
                # else:
                #     y.append(1)
                # y.append(row[1])
                x.append([float(row[i]) for i in range(len(row)) if i != 1])
                # x.append([row[i] for i in range(len(row)) if i != 1 or i!=0])
                line_count += 1
        # print(f'Processed {line_count} lines.')
    return column_names, np.array(x), np.array(y)

def create_model():
    column_names_temp, x, y = reading_data("dataset/features_matrix.csv")
    column_names_temp.remove("flag")

    # remove first column
    column_names_temp.remove("reqId")
    x = np.delete(x, obj=0, axis=1)

    model = RandomForestClassifier(500)
    model.fit(x, y)
    return model

import joblib

def load_or_create_model():
    # check the exisitng of the model in the direstory or create that
    # return create_model()
    # return pickle.load(open('model/created_model.pkl', 'rb'))
    return joblib.load('estimator.pkl')

def port_to_js(model, filename):
    porter = Porter(model, language='js')
    output = porter.export(embed_data=True)
    file = open(filename, "w")
    file.write(output)
    file.close()

# import pickle
# import joblib
# if __name__ == "__main__":
#     # model = create_model()
#     # joblib.dump(model, 'estimator.pkl', compress=0)
#     model = joblib.load('estimator.pkl')
#     porter = Porter(model, language='js')
#     output = porter.export(embed_data=True)
#     file = open('estimator.js', "w")
#     file.write(output)
#     file.close()
#     # pickle.dump(model, open("model/created_model", 'wb'))
#
#     # port_to_js(model, "model/created_model.js")
#
