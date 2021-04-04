
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