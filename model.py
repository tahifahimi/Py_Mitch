import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier

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
                x.append([float(row[i]) for i in range(len(row)) if i != 1])
                line_count += 1
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
def reading_data2(filename):
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
                print(column_names)
            else:
                if row[1]=='n':
                    y.append(0)
                else:
                    y.append(1)
                x.append([float(row[i]) for i in range(len(row)) if i != 1])
                line_count += 1
        print(f'Processed {line_count} lines.')
    return column_names, np.array(x), np.array(y)


def data_preprocessing():
    # reading files
    column_names_temp, x_temp, y_temp = reading_data2("dataset/features_matrix.csv")
    column_names_temp.remove("flag")
    # column_names_temp.remove("reqId")
    # remove first column
    # x_temp = np.delete(x_temp, obj=0, axis=1)
    ind = column_names_temp.index("changeInParams")
    column_names_temp.remove("changeInParams")
    x_temp = np.delete(x_temp, obj=ind, axis=1)

    ind = column_names_temp.index("passwordInPath")
    column_names_temp.remove("passwordInPath")
    x_temp = np.delete(x_temp, obj=ind, axis=1)

    ind = column_names_temp.index("payInPath")
    column_names_temp.remove("payInPath")
    x_temp = np.delete(x_temp, obj=ind, axis=1)

    ind = column_names_temp.index("viewInParams")
    column_names_temp.remove("viewInParams")
    x_temp = np.delete(x_temp, obj=ind, axis=1)

    return x_temp, y_temp, column_names_temp


def chi_test():
    # using ch2 to extract 45 features
    from sklearn.feature_selection import chi2

    # we want maximum of chi_res[0] and minimum of chi_res[1]
    chi_res = chi2(x_temp, y_temp)
    index_min = np.argsort(chi_res[1])
    # find removing indeces
    removing = index_min[len(index_min) - 4:]
    for i in range(len(removing)):
        column_names_temp.remove(column_names_temp[removing[i]])
        x_temp = np.delete(x_temp, obj=i, axis=1)




def create_simple_test_model():
    from sklearn.ensemble import RandomForestClassifier
    # create the model
    model = RandomForestClassifier(n_estimators=500)
    return model.fit(x_train, y_train)
