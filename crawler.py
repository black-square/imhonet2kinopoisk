from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import data
import utils

DELAY = 20

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
    capa["pageLoadStrategy"] = "none"

    service_args = []
    #service_args.extend(["--verbose", "--log-path=chromedriver.log"])

    return webdriver.Chrome("/usr/local/bin/chromedriver",
        chrome_options=chrome_options,
        desired_capabilities=capa,
        service_args=service_args
    )

def Login(driver, args):
    driver.get("https://www.kinopoisk.ru")

    WebDriverWait(driver, DELAY).until( utils.wait_page_to_load )

    loginMenu = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__log-in'))
    )

    loginMenu.click()

    loginInput = WebDriverWait(driver, DELAY).until(utils.presence_of_frame_and_element(
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

    title = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'movie-header__title'))
    )

    res = data.ItemInfo()

    res.title = title.text
    res.year = driver.find_element_by_class_name('movie-header__years').text

    rating = utils.IfExists(driver.find_element_by_css_selector, '.user-rating__rating')
    watched = utils.IfExists(driver.find_element_by_css_selector, '.user-rating__icon-eye')

    if watched:
        res.rating = data.Rating.WATCHED
    elif rating:
        res.rating  = data.Rating(int(rating.text))

    folders = utils.IfExists(driver.find_element_by_css_selector, '.folder-button_filled')

    if folders:
        driver.find_element_by_class_name('movie-header__folder').click()
        WebDriverWait(driver, DELAY).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'folders-menu__section'))
        )

        folderItems = driver.find_elements_by_class_name('folders-menu__section')

        res.folders = []

        for idx, item in enumerate(folderItems):
            if utils.IfExists(item.find_element_by_css_selector, '.folders-menu__icon-folder_filled'):
                res.folders.append(idx)

    return res
