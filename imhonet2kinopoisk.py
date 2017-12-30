from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#mobile_emulation = { "deviceName": "Nexus 6" }

mobile_emulation = {
    "deviceMetrics": { 
        "width": 360, "height": 640, "pixelRatio": 3.0, 
        #Workaround for:
        #   https://bugs.chromium.org/p/chromedriver/issues/detail?id=2172
        #   https://bugs.chromium.org/p/chromedriver/issues/detail?id=2103 
        "touch": False 
    },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" 
}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options = chrome_options)
driver.get("https://www.kinopoisk.ru")
#elem = driver.find_element_by_xpath('//a[@class="header-auth-partial-component__link" and not(@href)]')
elem = driver.find_element_by_class_name('header__log-in')

elem.click()

assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()