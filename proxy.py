import time
from selenium import webdriver
"""first you should run chrome driver with consideration of your chrome version
    here we are using ChromeDriver 89.0.4389.23
    set the path to chrome  driver"""
path_chrome = 'D:\Term9\BSc.project\drivers\chromedriver.exe'
path_firefox = 'D:\Term9\BSc.project\drivers\geckodriver.exe'
#
driver = webdriver.Chrome(path_chrome)  # Optional argument, if not specified will search path.
driver.get('https://darmankade.com')
time.sleep(5) # Let the user actually see something!
search_box = driver.find_element_by_id('refferalBtn')
data = driver.find_element_by_name('q')

data.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5) # Let the user actually see something!
driver.quit()



from seleniumwire import webdriver
from urllib.parse import urlparse


def goodUrl(current_url, request_url):
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
    if current_url.find('nuxt') != -1 or u.path.endswith('.json') or u.path.endswith('.js') or u.path.endswith('.css') or u.path.endswith(
            '.png') or u.path.endswith('ttf') or u.path.endswith('.ico') or u.path.endswith('woff'):
        isGood = False
    return isGood

driver = webdriver.Chrome()
driver.get("https://darmankade.com")