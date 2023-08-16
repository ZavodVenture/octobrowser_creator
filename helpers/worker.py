from entities import Wallet, Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from progress.bar import Bar
from time import sleep
from create import config_object
from random import sample
from string import ascii_letters, digits


def open_success_page(driver: webdriver.Chrome):
    driver.get('about:blank')
    script = '''let div = document.createElement("div");
div.textContent = "Profile is ready!";
div.style.fontSize = "36px";
div.style.fontWeight = "bold";
div.style.color = "green";
div.style.position = "absolute";
div.style.top = "50%";
div.style.left = "50%";
div.style.transform = "translate(-50%, -50%)";
document.body.appendChild(div);'''
    driver.execute_script(script)


def open_error_page(driver: webdriver.Chrome, error):
    driver.get('about:blank')
    script = f'''let div = document.createElement("div");
div.textContent = "An error occurred! {error}";
div.style.fontSize = "36px";
div.style.fontWeight = "bold";
div.style.color = "red";
div.style.position = "absolute";
div.style.top = "50%";
div.style.left = "50%";
div.style.transform = "translate(-50%, -50%)";
document.body.appendChild(div);'''
    driver.execute_script(script)


def worker(ws, wallet: Wallet, bar: Bar):
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", f'127.0.0.1:{ws}')
        driver = webdriver.Chrome(options=options)

        driver.get('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#onboarding/welcome')

        sleep(3)
        driver.refresh()

        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="onboarding__terms-checkbox"]'))).click()
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/ul/li[3]/button'))).click()
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div/button[1]'))).click()

        sleep(1)

        split = wallet.seed_phrase.split(' ')

        if len(split) != 12:
            open_error_page(driver, Error('Seed length error', 'The length of one of the seed-phrases is not equal to 12'))
            return

        for index in range(12):
            driver.find_element(By.ID, f'import-srp__srp-word-{index}').send_keys(split[index])

        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[4]/div/button'))).click()

        password = config_object.metamask_password if config_object.metamask_password else ''.join(sample(ascii_letters + digits, 30))

        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input'))).send_keys(password)
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input'))).send_keys(password)

        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/div[3]/label/input'))).click()

        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/form/button'))).click()

        WebDriverWait(driver, 15).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button'))).click()

        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button'))).click()
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[2]/button'))).click()

        open_success_page(driver)
    except Exception as e:
        try:
            open_error_page(driver, type(e))
        except:
            pass
    finally:
        bar.next()