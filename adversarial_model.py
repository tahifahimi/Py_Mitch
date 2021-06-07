import csv
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
import time


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
                print(column_names)
            else:
                if row[1]=='n':
                    y.append(0)
                else:
                    y.append(1)
                # y.append(row[1])
                x.append([float(row[i]) for i in range(len(row)) if i != 1])
                # x.append([row[i] for i in range(len(row)) if i != 1 or i!=0])
                line_count += 1
        print(f'Processed {line_count} lines.')
    return column_names, np.array(x), np.array(y)

def encode_to_one_hot(arr):
    from numpy import argmax
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import OneHotEncoder
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(arr)
    print(integer_encoded)
    # binary encode
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    print(onehot_encoded)
    # invert first example
    inverted = label_encoder.inverse_transform([argmax(onehot_encoded[0, :])])
    print(inverted)
    return onehot_encoded

# using ch2 to extract 45 features
from sklearn.feature_selection import chi2

# reading files
column_names_temp, x_temp, y_temp = reading_data("dataset/features_matrix.csv")
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


# we want maximum of chi_res[0] and minimum of chi_res[1]
chi_res = chi2(x_temp, y_temp)
index_min = np.argsort(chi_res[1])
# find removing indeces
removing = index_min[len(index_min)-4:]
for i in range(len(removing)):
    column_names_temp.remove(column_names_temp[removing[i]])
    x_temp = np.delete(x_temp, obj=i, axis=1)



"""error ---> we should use 10 fold nested cross validation with 10 percentage for test-----------------------------------------------------
https://machinelearningmastery.com/nested-cross-validation-for-machine-learning-with-python/
"""
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
# y_train = y_train.reshape((-1, 1))
# y_test = y_test.reshape((-1, 1))

# save the start time
start_time = time.time()

from sklearn.ensemble import RandomForestClassifier
# create the model
model = RandomForestClassifier(n_estimators=500)



from art.estimators.classification.scikitlearn import ScikitlearnRandomForestClassifier
# Create the ART classifier
classifier = ScikitlearnRandomForestClassifier(model=model)

onehot_encoded = encode_to_one_hot(y_train)

# twos = np.repeat(2, len(y_train))
# combined = np.vstack((y_train, twos)).T

# Train the ART classifier
classifier.fit(x_train, onehot_encoded)

# Evaluate the ART classifier on benign test examples
predictions = classifier.predict(x_test)

# test = label_encoder.fit_transform(y_test)
# test = test.reshape(len(test), 1)
# test_encoded = onehot_encoder.fit_transform(test)

test_encoded = encode_to_one_hot(y_test)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(test_encoded, axis=1)) / len(y_test)
print("Accuracy on benign test examples: {}%".format(accuracy * 100))

#save the model
classifier.save("adversial_rf_model_9145", "./")



# create an attack
from art.attacks.evasion import BoundaryAttack
attack = BoundaryAttack(classifier)
attack_data = attack.generate(x_test, test_encoded)
np.savetxt("attackVector632.csv", attack_data, delimiter=",")

# now check the attack data on the robust model
robust_predict = classifier.predict(attack_data)

# create a simple classifier
simple_model = RandomForestClassifier(n_estimators=500).fit(x_train, y_train)
# check prediction of attack data in simple model
simple_predict = simple_model.predict(attack_data)

from numpy import argmax
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
label_encoder.fit(y_test)
t = 0
for i in range(len(simple_predict)):
    inverted = label_encoder.inverse_transform([argmax(robust_predict[i, :])])
    if inverted == y_test[i]:
        t += 1

f = 0
for i in range(len(simple_predict)):
    if simple_predict[i] == y_test[i]:
        f += 1


# use another attack model
# from art.attacks.evasion import DecisionTreeAttack
# tree_attacker = DecisionTreeAttack(classifier)
# tree_attack_sample = tree_attacker.generate(x_test, test_encoded)

"""output....: """
# t
# Out[31]: 605
# f
# Out[32]: 601
# simple_predict.shape
# Out[33]: (632,)

end_time = time.time()
print("time of random forest : ", end_time-start_time)


# load the model again
import pickle
loaded_model = pickle.load(open("adversial_rf_model_9145.pickle", 'rb'))

from sklearn_porter import Porter
porter = Porter(loaded_model, language='js')
output = porter.export(embed_data=True)
file = open("robustclassifier.js", "w")
file.write(output)
# Out[6]: 24092671
file.close()



from css_html_js_minify import process_single_js_file
# create .min.js file
process_single_js_file('robustclassifier.js', overwrite=False)


# conver the main classifier to a model --> it is not possible....