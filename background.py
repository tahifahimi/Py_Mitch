from seleniumwire import webdriver
from urllib.parse import urlparse
import multiprocessing

# inner imports :
from sensitivity import *
from model import *
from guess_csrfs import *


class Py_Mitch:
    """This class contain the main program
        inputs:
            browser_is : introduce the type of the browser to be used by Mitch
            url : this is the url of the login page
            domain : domain of the web page
    """
    def __init__(self, browser_is="chrome", url="https://darmankade.com", domain="darmankade.com"):
        self.log_sensitivity = {}
        self.phase = 0
        if browser_is == "chrome":
            self.driver = webdriver.Chrome()
        elif browser_is == "firefox":
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Safari()
        self.main_domain = domain
        self.driver.get(url)
        self.lock = multiprocessing.Lock()

        # urls that mitch search for vulnerabilities in them
        self.search_urls = []
        self.active_collector = []
        self.alice1_requests = []
        self.sensitive_requests = []
        self.main_sensitive_req = []
        self.bob_requests = []
        self.candidates = []
        self.null_collector = []
        self.unauth_requests = []
        self.collected_sensitive_requests = 0
        self.collected_total_request = 0
        self.classifier = load_or_create_model()

    def goodUrl(self, current_url, domain):
        # s = urlparse(request_url)
        u = urlparse(current_url)
        isGood = True

        if not u.scheme.startswith('http'):
            isGood = False
        if u.path.endswith('/chrome/newtab'):
            isGood = False
        if domain not in current_url:
            isGood = False
        return isGood


    def sameParams(self, a, b):
        flag = True
        if len(a.keys()) != len(b.keys()):
            flag = False
        else:
            for k in a.keys():
                if k not in b.keys():
                    flag = False
        return flag

    def compareReq(self, a, b):
        return a['method'] == b['method'] and a['url'] == b['url'] and self.sameParams(a, b)

    def isKnown(self, r, gs):
        flag = False
        if gs == []:
            return False
        if not gs:
            flag = True

        for g in gs:
            if self.compareReq(g, r):
                flag = True
        return flag

    def parseParams(self, param):
        p = {}
        for k in param.keys():
            if p.get(k) is not None:
                p[k] = p.get(k)
        return p


    def on_requests(self, arr):
        for request in self.driver.requests:
            req = {}
            # visiting url is the url of the main frame from the browser
            isMainFrame = False
            # check for the main frame
            if request.response is not None and request.response.headers['Content-Type'] is not None:
                if 'html' in request.response.headers['Content-Type'] and self.main_domain in request.url:
                    isMainFrame = True
                    # print("we have a main frame in : ", request)

            if isMainFrame and self.goodUrl(request.url, self.main_domain):
                req['method'] = request.method
                o = urlparse(request.url)
                req['url'] = o.scheme + "://" + o.hostname + "//" + o.path
                req['reqId'] = request.id
                req['response'] = {}
                # trying to take the body --> taking body from the driver
                try:
                    req['response']['body'] = self.driver.page_source
                    # req['response']['body'] = request.response.body.decode('utf-8')
                except:
                    print("except in body decoding")
                req['params'] = self.parseParams(o._asdict())
                if request.method == "POST":
                    if request.body.decode('utf-8') != '':
                        postBody = {}
                        data = request.body.decode('utf-8')
                        if data.startswith("{"):
                            data = data.replace('{', '')
                            data = data.replace('}', '')
                            data = data.split(',')
                            for d in data:
                                k, v = d.split(':')
                                postBody[k[0].replace('\'', '')] = v[0].replace('\'', '')
                        else:
                            # check this part .................????????????????/
                            # print("data is : ", data)
                            data = data.replace("%5B", '[')
                            data = data.replace("%5D", ']')
                            temp = data.split("&")
                            for t in temp:
                                d = t.split("=")
                                postBody[d[0]] = [d[1]]
                        for k in postBody.keys():
                            req['params'][k] = postBody[k]
                        # here remains --- line 140 to 160

                # print("req is: ", req)

                sen = False
                sensitivity = isSensitive(req, self.classifier)
                if isinstance(sensitivity, int):
                    if sensitivity == 1:
                        sen = True
                        # print("sensitive Request in : ", req['url'])
                else:
                    if sensitivity != 'n':
                        sen = True
                    #     print("sensitive Request in : ", req['url'])
                    # else:
                    #     print("here we have trouble : ", sensitivity)

                if sen and (not self.isKnown(req, arr)):
                    req['headers'] = request.headers
                    self.main_sensitive_req.append(request)
                    # add code line 179 to 185
                    req['response']['status'] = request.response.status_code
                    if request.response.headers is not None:
                        headers = {}
                        for k in request.response.headers.keys():
                            headers[k] = request.response.headers[k]
                        if headers != {}:
                            req['response']['headers'] = headers

                    arr.append(req)
                    # print("sensitive request is added", req)
                    self.collected_sensitive_requests += 1
                # add to total requests
                self.collected_total_request += 1
        del self.driver.requests

    def call_url(self, request_urls, arr):
        import time
        for url in request_urls:
            try:
                self.driver.get(url)
                time.sleep(15)
                self.on_requests(arr)
            except:
                print("error in link : ", url)

    def logged_in_Alice(self):
        self.lock.acquire()
        # here we need to add another phase for starting Alice
        print("Alice logged in ")
        # self.active_collector = self.sensitive_requests
        del self.driver.requests
        self.phase = 0
        self.call_url(self.search_urls, self.sensitive_requests)
        print("alice sensitive requests are : ", self.sensitive_requests)
        self.lock.release()

    def finished_Alice1(self):
        self.lock.acquire()
        print("Alice run finished, preparing CSRF test forms...")
        print("Please logout from the current session and notify the extension")
        input()
        self.phase = 1
        self.lock.release()

    def logged_out_Alice1(self):
        print("Alice logged out, please login as Bob and notify the extension")
        self.lock.acquire()
        input()
        self.phase = 2
        self.lock.release()

    def logged_in_bob(self):
        self.lock.acquire()
        print("Logged in as Bob, testing sensitive requests...")
        del self.driver.requests
        self.call_url(self.search_urls, self.bob_requests)
        print("bob requests are: ", self.bob_requests)
        print("...please logout from Bob's account and notify the extension")
        input()
        self.phase = 3
        self.lock.release()

    def logged_out_bob(self):
        print("Logged out as Bob, please login as Alice again and notify the extension")
        input()
        self.active_collector =[]
        self.phase = 4

    def logged_in_Alice2(self):
        print("Logged in as Alice again, testing sensitive requests...")
        self.lock.acquire()
        del self.driver.requests
        # self.active_collector = self.alice1_requests
        # self.replayRequests(self.alice1_requests)
        self.call_url(self.search_urls, self.alice1_requests)
        print("...please logout from Alice's account and notify the extension")
        input()
        self.phase = 5
        self.lock.release()

    def logged_out_Alice2(self):
        print("Logged out as Alice, testing unauth sensitive requests...")
        self.lock.acquire()
        # self.active_collector = self.unauth_requests
        del self.driver.requests
        self.replayRequests(self.unauth_requests)
        print("all data collected")
        self.phase = 6
        self.lock.release()


    # we change the guessCSRFs function and removes tellCSRFs
    def make_conclusion(self):
        print("making conclusion")
        candidates, resulting_candidates = guessCSRFs(self.sensitive_requests, self.alice1_requests, self.bob_requests, self.unauth_requests)
        print("search for possible CSRFs finished, please expand the array presented here to see candidates:")
        print(candidates)
        print("resulting candidates are :")
        print(resulting_candidates)
        # results_url = tellCSRFs(self.sensitive_requests, self.alice1_requests, self.bob_requests, self.unauth_requests)

    def log(self):
        print("collected sensitive url :")
        for cs in self.sensitive_requests:
            print(cs['url'])

        print("size of the arrays: ")
        print("alice1, bob, alice2, unauth")
        print(len(self.sensitive_requests), "    ", len(self.bob_requests), "     ", len(self.alice1_requests),
              "           ", len(self.unauth_requests))

    def replayRequests(self, unauth_requests):
        import requests
        session = requests.Session()
        for r in self.main_sensitive_req:
            req = {}
            req['method'] = r.method
            o = urlparse(r.url)
            req['url'] = o.scheme + "://" + o.hostname + "//" + o.path
            req['reqId'] = r.id
            req['params'] = r.params
            if r.method.upper() == "POST":
                if r.body.decode('utf-8') != '':
                    postBody = {}
                    data = r.body.decode('utf-8')
                    if data.startswith("{"):
                        data = data.replace('{', '')
                        data = data.replace('}', '')
                        data = data.split(',')
                        for d in data:
                            k, v = d.split(':')
                            postBody[k[0].replace('\'', '')] = v[0].replace('\'', '')
                    else:
                        # check this part .................????????????????/
                        # print("data is : ", data)
                        data = data.replace("%5B", '[')
                        data = data.replace("%5D", ']')
                        temp = data.split("&")
                        for t in temp:
                            d = t.split("=")
                            postBody[d[0]] = [d[1]]
                    for k in postBody.keys():
                        req['params'][k] = postBody[k]
            if r.method.upper() == "POST":
                res = session.request(method=r.method, url=r.url, params=r.body, headers={"Content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
                # session.request(method=r.method, url=r.url, data=data.encode("utf-8"),
                #                 headers={"Content-Type": "application/json; charset=UTF-8"})
                # session.request(method=r.method, url=r.url, data=json.dumps(postBody),
                #                 headers={"Content-Type": "application/json; charset=UTF-8"})

            else:
                res = session.po
            # res = session.get(r['url'], data=r['params'], headers=r['headers'])
            req['response'] = {}
            req['response']['body'] = res.text

            req['response']['status'] = res.status_code
            if res.headers is not None:
                headers = {}
                for k in res.headers.keys():
                    headers[k] = res.headers[k]
                if headers != {}:
                    req['response']['headers'] = headers

            unauth_requests.append(req)


"""you can use the selenium requests instead of working with requests"""

if __name__ == "__main__":
    file = open('test/test.txt')
    domain = file.readline().replace('\n', '').split(' ')[1]
    login_url = file.readline().replace('\n', '').split(' ')[1]

    mitch = Py_Mitch("firefox", login_url, domain)
    # mitch = Py_Mitch("chrome", login_url, domain)

    mitch.search_urls = file.read().split('\n')
    # mitch.search_urls = ["http://appeto.ir/platform#/media", "http://appeto.ir/platform#/account"]
    print("mitch created")

    while True:
        if login_url not in mitch.driver.current_url:
            break

    mitch.logged_in_Alice()
    mitch.finished_Alice1()
    mitch.logged_out_Alice1()
    mitch.logged_in_bob()
    mitch.logged_out_bob()
    mitch.logged_in_Alice2()
    mitch.logged_out_Alice2()

    print(mitch.collected_total_request, "    ", mitch.collected_sensitive_requests)
    mitch.make_conclusion()
    # print("mitch main sensitive requests: ", mitch.main_sensitive_req)
    print("a complete log is in : ")
    mitch.log()

    mitch.driver.close()

