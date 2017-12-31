import argparse
import shlex
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

DELAY = 20

def DumpHtml(driver):
    with open("dump.html", "w", encoding='utf-8') as text_file:
        text_file.write(driver.execute_script("return document.documentElement.outerHTML"))

class presence_of_frame_and_element(object):
    def __init__(self, frame_locator, elem_locator):
        self.frame_locator = frame_locator
        self.elem_locator = elem_locator

    def __call__(self, driver):
        try:
            if self.frame_locator:
                driver.switch_to.frame(driver.find_element(*self.frame_locator))
            else:
                driver.switch_to.default_content()
            return driver.find_element(*self.elem_locator)
        except NoSuchFrameException:
            return False

def CreateDriver():   
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
 
    capa = DesiredCapabilities.CHROME
    
    #Option breaks wait for element functionalty
    #capa["pageLoadStrategy"] = "none"

    return webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options, desired_capabilities=capa)

def Login(driver, args):
    driver.get("https://www.kinopoisk.ru")

    loginMenu = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__log-in'))
    )

    loginMenu.click()

    loginInput = WebDriverWait(driver, DELAY).until(presence_of_frame_and_element(
        (By.NAME,'kp2-authapi-iframe'),
        (By.NAME, 'login')
    ))

    loginInput.clear()
    loginInput.send_keys(args.user)

    passInput = driver.find_element_by_name('password')
    passInput.clear()
    passInput.send_keys(args.password)

    submit = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'button.auth__signin'))
    )

    submit.click()
    driver.switch_to.default_content()

    WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__auth-status'))
    )

def GetItemInfo(driver, url):
    driver.get(url)

    loginMenu = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__log-in'))
    )

DESCRIPTION = '''\
Imhonet to Kinopoisk
'''

EPILOG = '''\

Additional info:
 - Arguments can be stored in a text file and the name of this file can be 
   passes as an argument with prefix '@', e.g.:

        taf.py @base_args.conf @my_args.conf --osd Log

   The file allows breaking arguments on multiple lines and supports 
   comments starting with '#'
'''

def main():
    def sh_split(arg_line):
        for arg in shlex.split(arg_line, comments=True):
            yield arg

    parser = argparse.ArgumentParser( fromfile_prefix_chars='@', description=DESCRIPTION, epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter )
    parser.convert_arg_line_to_args = sh_split

    parser.add_argument( '-u', '--user', metavar='NAME', required=True,  help="Username on Kinopoisk" )
    parser.add_argument( '-p', '--password', metavar='PASS', required=True,  help="Password on Kinopoisk" )

    args = parser.parse_args()

    try:
        driver = None
        driver = CreateDriver()
        Login(driver, args)
        GetItemInfo(driver, "http://www.kinopoisk.ru/film/45275/")
    except:
        if driver:
            DumpHtml(driver)
        raise
    finally:
        if driver is not None:
            driver.close()

if __name__ == '__main__':
    main()