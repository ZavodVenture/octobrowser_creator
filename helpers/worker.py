from entities import Wallet, Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from progress.bar import Bar
from time import sleep
from create import config_object
from random import sample
from string import ascii_letters, digits
from webdriver_manager.chrome import ChromeDriverManager


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
        service = Service(executable_path=ChromeDriverManager('120.0.6099.71').install())
        options = Options()
        options.add_experimental_option("debuggerAddress", f'127.0.0.1:{ws}')
        driver = webdriver.Chrome(options=options, service=service)

        driver.get('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html')

        try:
            WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, '//div[@class="critical-error"]')))
        except:
            pass
        else:
            driver.refresh()

        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="onboarding__terms-checkbox"]'))).click()
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-import-wallet"]'))).click()
        WebDriverWait(driver, 1)
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="metametrics-i-agree"]'))).click()

        WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.ID, 'import-srp__srp-word-0')))

        seed = wallet.seed_phrase.split(' ')

        if len(seed) != 12:
            open_error_page(driver, Error('Seed length error', 'The length of one of the seed-phrases is not equal to 12'))
            return

        for j in range(12):
            driver.find_element(By.ID, f'import-srp__srp-word-{j}').send_keys(seed[j])

        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="import-srp-confirm"]'))).click()

        password = config_object.metamask_password if config_object.metamask_password else ''.join(sample(ascii_letters + digits, 30))

        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, '//input[@data-testid="create-password-new"]'))).send_keys(password)
        WebDriverWait(driver, 20).until(ec.presence_of_element_located(((By.XPATH, '//input[@data-testid="create-password-confirm"]')))).send_keys(password)
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, '//input[@data-testid="create-password-terms"]'))).click()

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="create-password-import"]'))).click()

        driver.implicitly_wait(5)

        while 1:
            try:
                sleep(5)
                driver.find_element(By.XPATH, '//div[@class="loading-overlay"]')
            except:
                break
            else:
                driver.refresh()
                continue

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-complete-done"]'))).click()
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-next"]'))).click()
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-done"]'))).click()

        open_success_page(driver)
    except Exception as e:
        try:
            open_error_page(driver, type(e))
        except:
            pass
    finally:
        bar.next()
