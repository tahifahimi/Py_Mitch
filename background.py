
from seleniumwire import webdriver
from urllib.parse import urlparse

# inner imports :
from sensitivity import *

class Py_Mitch:

    def __init__(self, browser_is="chrome"):
        if browser_is == "chrome":
            self.driver = webdriver.Chrome()
        elif browser_is == "firefox":
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Safari()

        self.requested_url = "https://darmankade.com"

        self.active_collector = []
        self.sensitive_requests = []
        self.candidates = []

        self.collected_sensitive_requests = 0
        self.collected_total_request = 0

    def call_url(self):
        self.driver.get(self.requested_url)

    def goodUrl(self, current_url, request_url):
        s = urlparse(request_url)
        u = urlparse(current_url)
        isGood = True
        if not u.scheme.startswith('http'):
            isGood = False
        if u.path.endswith('/chrome/newtab'):
            isGood = False
        if not u.hostname.find(s.hostname) != -1:
            isGood = False
        # maybe we should remove requests of loading elements of the page.....................................
        if current_url.find('nuxt') != -1 or u.path.endswith('.js') or u.path.endswith('.json') or u.path.endswith('.css') or u.path.endswith('.png') or u.path.endswith('ttf') or u.path.endswith('.ico') or u.path.endswith('woff'):
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
            flag = True

        for g in gs:
            if self.compareReq(g, r):
                flag = True
        return flag

    def parseParams(self, param):
        p = {}
        for k in param.keys():
            p[k] = p.get(k)
        return p


    def on_requests(self):

        for request in self.driver.requests:
            req = {}
            # visiting url is the url of the main frame from the browser
            if self.goodUrl(request.url, self.driver.current_url):
                req['method'] = request.method
                o = urlparse(request.url)
                req['url'] = o.scheme + "//" + o.hostname + "//" + o.path
                req['reqId'] = request.id
                req['response'] = {}
                try:
                    req['response']['body'] = request.response.body.decode('utf-8')
                except:
                    print("except in body decoding")
                req['params'] = self.parseParams(o._asdict())

                if request.method == "POST":
                    if request.body.decode('utf-8') != '':
                        postBody = ''
                        # here remains --- line 140 to 160

                print("req is: ", req)

                # check this functions and inputs ...............................................
                if isSensitive(req) and (not self.isKnown(req, self.active_collector)):
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

import time
if __name__ == "__main__":
    mitch = Py_Mitch()
    print("mitch created")
    mitch.call_url()
    print("called")
    time.sleep(5)
    mitch.on_requests()
    print("end of requests")
    print(mitch.collected_total_request, "    ", mitch.collected_sensitive_requests)

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
