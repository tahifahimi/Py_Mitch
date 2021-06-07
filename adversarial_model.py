import csv
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
import time
from model import load_or_create_model, data_preprocessing
from art.estimators.classification.scikitlearn import ScikitlearnRandomForestClassifier

x, y, column_name = data_preprocessing()
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)


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

def simple_robust_model(simpleModel):
    # Create the ART classifier
    classifier = ScikitlearnRandomForestClassifier(model=model)

    onehot_encoded = encode_to_one_hot(y_train)

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

    # save the model
    classifier.save("robust_model.pkl", "./")

def generate_attack_vector():
    # create an attack
    from art.attacks.evasion import BoundaryAttack
    attack = BoundaryAttack(classifier)
    attack_data = attack.generate(x_test, test_encoded)
    np.savetxt("attackVector632.csv", attack_data, delimiter=",")

    # now check the attack data on the robust model
    robust_predict = classifier.predict(attack_data)

    # create a simple classifier
    # simple_model = RandomForestClassifier(n_estimators=500).fit(x_train, y_train)
    simple_model = load_or_create_model()
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


"""create an adversarial model with the use of art( adversarial robustness toolkit) 
    this model would be robust against the evasion attacks"""
if __name__=="__main__":
    model = load_or_create_model()
    simple_robust_model(model)

    print("if you want to generate the attack vector and test the model enter yes ...")
    if input()=="yes":
        generate_attack_vector()


def model_to_js():
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