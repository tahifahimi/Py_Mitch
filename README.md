# PY_MITCH
This program is a reimplementation and improvement from the [Mitch](https://github.com/alviser/mitch)

## Description 
In this project we make the Mitch to be platform free

## Getting Started

### Dependencies
you can install requirements from requirements.txt
It is platform free (win - linux)

### installing
first you need to install [selenium-wire](https://pypi.org/project/selenium-wire/) and then install [Chrome](https://chromedriver.chromium.org/getting-started) or [Firefox](https://github.com/mozilla/geckodriver/releases) webdriver based on your python version. If you are using Windows you need to add webdriver to you Variable Path.
After that just run the program with :

```
python background.py
```

## Model 
the model is available (estimator.pkl) but if you want to create new Model, you might use the dataset from the article[[1]](#1).

## simple summary of the Article

|               | reaons        |
| ------------- |:-------------:|
| using 2 accounts| to simulate forging a request into another session ... for example Alice forge request into Bob session |
| using unauthenticate session      | to make sure every request needs the authentication( because CSRF is only appliable into requests that needs authentication |
| using Alice2 session | to be sure that there is no entry in the requests that can be depend on the time or anti-csrf tokens |

