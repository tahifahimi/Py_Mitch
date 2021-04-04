from seleniumwire import webdriver
from urllib.parse import urlparse

class Py_Mitch:

    def __init__(self, browser_is="chrome"):
        if browser_is == "chrome":
            self.driver = webdriver.Chrome()
        elif browser_is == "firefox":
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Safari()

        self.requested_url = []
        self.active_collector = []
        self.sensitive_requests = []
        self.candidates = []

        self.collected_sensitive_requests = 0
        self.collected_total_request = 0


    def goodUrl(self, current_url, request_url):
        u = urlparse(request_url)
        s = urlparse(current_url)
        isGood = True
        if not u.scheme.startswith('http'):
            isGood = False
        if u.path.endswith('/chrome/newtab'):
            isGood = False
        # check that current url is a sub domain of the main domain
        # check domain is equal to hostname ????..............................
        if not u.hostname.find(s.hostname):
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
        if not gs:
            return flag

        for g in gs:
            if self.compareReq(g, r):
                flag = True
        return flag

    def parseParams(self, param):
        p = {}
        for k in param.keys():
            p[k] = p.get(k)
        return p

    def isSensitive(self, req):
        pass

    def on_requests(self):

        for request in self.driver.requests:
            req = {}
            if self.goodUrl(self.driver.current_url, request.url):
                req['method'] = request.method
                o = urlparse(request.url)
                req['url'] = o.scheme + "//" + o.hostname + "//" + o.path
                req['reqId'] = request.id
                req['response'] = {'body': request.response.body.decode('utf-8')}
                req['params'] = self.parseParams(o._asdict())

                if request.method == "POST":
                    if request.body.decode('utf-8') != '':
                        postBody = ''
                        # here remains --- line 140 to 160

                print("req is: ", req)

                # check this functions and inputs ...............................................
                if self.isSensitive(req) and (not self.isKnown(req, self.active_collector)):
                    # add code line 179 to 185
                    req['response']['status'] = request.response.status_code
                    if request.response.headers:
                        headers = {}
                        for k in request.response.headers.keys():
                            headers[k] = request.response.headers[k]
                        if headers:
                            req['response']['headers'] = headers

                    self.active_collector.append(req)
                    print("sensitive request is added", req)
                    self.collected_sensitive_requests += 1



                # add to total requests
                self.collected_total_request += 1

    def remove_all_requests(self):
        for req in self.driver.requests[:]:
            for req in self.driver.requests[:]:
                self.driver.requests.remove(req)



# another way
# url = "https://github.com"
# # Firefox
# # driver = webdriver.Firefox()
# # Chrome
# driver = webdriver.Chrome()
#
# # load the page
# driver.get(url)
#
# # Access and print requests via the `requests` attribute
# for request in driver.requests:
# 	if request.response:
# 		print(
# 			request.url,
# 			request.response.status_code,
# 			request.response.headers['Content-Type'])


# Safari: you need to tell Selenium Wire the port number you selected when you configured the browser in Browser Setup.
# driver = webdriver.Safari(seleniumwire_options={'port': 12345})

# Edge: you need to tell Selenium Wire the port number you selected when you configured the browser in Browser Setup.
# driver = webdriver.Edge(seleniumwire_options={'port': 12345})
