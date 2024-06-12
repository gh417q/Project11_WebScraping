from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd


URL = "https://www.nhl.com/"
BEST = 10

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", value=True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

# Page behavior is not constant, different sequences are possible, call the one that works
# (Select 'Regular Season'; click 'Get Stats') if 'Playoffs' selected; click 'Skaters'
def sequence_1():
    wait = WebDriverWait(driver, 5)
    stats_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#\:r1\:")))
    select_value = stats_select.get_attribute('value')
    print(f"Currently selected: {select_value}")
    if select_value == "Playoffs":
        stats_select.click()
        stats_select.send_keys(Keys.ARROW_UP)
        stats_select.send_keys(Keys.ENTER)
        wait = WebDriverWait(driver, 5)
        get_stats = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="home-tabpanel"]/form/button')))
        # driver.find_element(By.XPATH, value='//*[@id="home-tabpanel"]/form/button')
        get_stats.click()
    driver.find_element(By.ID, value="skaters").click()

# Page behavior is not constant, different sequences are possible, call the one that works
# Click 'Skaters'; select 'Regular Season' if 'Playoffs' selected. No 'Get Stats' button here
def sequence_2():
    wait = WebDriverWait(driver, 5)
    tab_skaters = wait.until(EC.element_to_be_clickable((By.ID, "skaters")))
    tab_skaters.click()
    wait = WebDriverWait(driver, 5)
    stats_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#\:r9\:")))
    select_value = stats_select.get_attribute('value')
    print(f"Currently selected: {select_value}")
    if select_value == "Playoffs":
        print("Switching to 'Regular Season'")
        stats_select.click()
        stats_select.send_keys(Keys.ARROW_UP)
        stats_select.send_keys(Keys.ENTER)


# I. Get to the page
try:
    driver.find_element(By.XPATH,value='//a[contains(@href,"/stats")]').click()
except ElementNotInteractableException:
    driver.find_element(By.XPATH, value='/html/body/div[1]/header/div/button').click()
    wait = WebDriverWait(driver, 15)
    stats_menu = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href,"/stats")]')))
    stats_menu.click()
    sequence_2()


# II. Get the information
def get_title() -> list:
    header_row = []
    wait = WebDriverWait(driver, 30)
    # wait for the last column to appear
    wait.until(EC.presence_of_element_located((By.XPATH,
                                               f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[1]/div/div/div[25]/div')))
    for k in range(2, 26):
        header_cell = driver.find_element(By.XPATH,
                                          value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[1]/div/div/div[{k}]/div')
        column_title = header_cell.get_attribute("title")
        # print(column_title)
        header_row.append(column_title)
    return header_row

def get_table() -> list:
    rows = []
    for k in range(BEST):
        current_row = []
        player = driver.find_element(By.XPATH,
                                      value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[2]/div[{k + 1}]/div/div[2]/div/a')
        # print(player.get_attribute("text"))
        current_row.append(player.get_attribute("text"))
        for m in range(3, 5):
            row_cell = driver.find_element(By.XPATH,
                                           value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[2]/div[{k + 1}]/div/div[{m}]/div')
            # print(row_cell.text)
            current_row.append(row_cell.text)
        for m in range(5, 11):
            row_cell = driver.find_element(By.XPATH, value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[2]/div[{k + 1}]/div/div[{m}]')
            # print(row_cell.text)
            current_row.append(row_cell.text)
        row_cell = driver.find_element(By.XPATH, value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[2]/div[{k + 1}]/div/div[11]/span')
        # print(row_cell.text)
        current_row.append(row_cell.text)
        for m in range(12, 26):
            row_cell = driver.find_element(By.XPATH, value=f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[2]/div[{k + 1}]/div/div[{m}]')
            # print(row_cell.text)
            current_row.append(row_cell.text)
        rows.append(current_row)
    return rows


# III. Make CSV document
title = get_title()
df = pd.DataFrame(np.array(get_table()), columns=title)
df.to_csv('NHL-top10-points.csv', index=False)

# IV. Get statistics by goals
driver.find_element(By.XPATH, value='//*[@id="season-tabpanel"]/div[4]/div[1]/div[1]/div/div/div[8]').click()

# V. Make CSV document
wait = WebDriverWait(driver, 30)
# wait for the last column to appear
wait.until(EC.presence_of_element_located((By.XPATH,
                                           f'//*[@id="season-tabpanel"]/div[4]/div[1]/div[1]/div/div/div[25]/div')))
title = get_title()
df = pd.DataFrame(np.array(get_table()), columns=title)
df.to_csv('NHL-top10-goals.csv', index=False)
