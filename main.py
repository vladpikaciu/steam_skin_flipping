from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from termcolor import colored
from selenium.webdriver.chrome.options import Options


# Curent Time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
# Open file
f = open("data.txt", "a")
a = open("log.txt", "w+")
skin_stats = {
    'name': '',
    'selling_price': '',
    'buying_price': '',
    'sell_quantity': '',
    'buy_quantity': '',
}
order_quantity = 25
# Create file

chrome_options = Options()
# #chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# #chrome_options.add_argument("--no-sandbox") # linux only
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--user-data-dir=data")
chrome_options.add_extension('csgo_trader_extension.crx')


s=Service("/home/vladpikaciu/PycharmProjects/flipping/chromedriver")
driver = webdriver.Chrome(service=s, options=chrome_options)

# driver = webdriver.Chrome(service=s)

def wait_till(element, seconds=10):
    WebDriverWait(driver, seconds).until(
        EC.presence_of_element_located((element))
    )

def check_login():
    try:
        driver.find_element(by=By.CLASS_NAME, value="avatarIcon")
    except:
        print("User not logged in. Please log in.")
        driver.get("https://steamcommunity.com/login/home/?goto=")
        username = input("Please enter steam username: ")
        password = input("Please enter steam password: ")
        driver.find_element(by=By.ID, value="input_username").send_keys(username)
        driver.find_element(by=By.ID, value="input_password").send_keys(password)
        driver.find_element(by=By.ID, value="remember_login").click()
        driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[7]/div[4]/div[1]/div/div[1]/div/div/div/div/div[3]/div[1]/button").click()
        try:
            driver.find_element(by=By.ID, value="twofactorcode_entry")
            steam_guard = input("Please enter Steam Guard Code: ")
            driver.find_element(by=By.ID, value="twofactorcode_entry").send_keys(steam_guard)
            driver.find_element(by=By.XPATH, value="/html/body/div[3]/div[3]/div/div/div/form/div[4]/div[1]/div[1]").click()
            driver.find_element(by=By.CLASS_NAME, value="actual_persona_name")
        except:
            print("Incorect login details")

    else:
        print("Logged in")

# noinspection PyTypedDict
def scrape_page(min, max):
    counter = 1
    for pages in range(min, max):
        total_skins  = str((max - min) * 10)
        links = []
        if game == 1:
            steam_url = 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B0%5D=any&category_730_ProPlayer%5B0%5D=any&category_730_StickerCapsule%5B0%5D=any&category_730_TournamentTeam%5B0%5D=any&category_730_Weapon%5B0%5D=any&appid=730#p' + str(pages) + '_price_asc'
        elif game == 2:
            steam_url = 'https://steamcommunity.com/market/search?appid=304930#p' + str(pages) + '_quantity_desc'
        driver.get(steam_url)
        check_login()
        driver.get(steam_url)
        sleep(1)
        # Scrape all skins links from steam search
        for item in range(0,10):
            # Check if search results are visible
            try:
                wait_till((By.ID, "resultlink_1"))
            except TimeoutException:
                # Check if "too many requests" error visible
                try:
                    driver.find_element(by=By.PARTIAL_LINK_TEXT, value='too many requests recently.')
                    print('Too many request (Items page)')
                # Reload page if error not visible
                except:
                    driver.get(steam_url)
                    print("Items page needed reload")
            link = driver.find_element(by=By.ID, value='resultlink_' + str(item)).get_attribute('href') + '?cc=us'
            links.append(link)
        # Scrape every skin data
        for x in range(0, len(links)):
            driver.get(links[x])
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "market_listing_largeimage"))
                )
            except:
                print('Could not find skin data')
                # Check if "too many requests" error visible
                try:
                    driver.find_element(by=By.PARTIAL_LINK_TEXT, value='too many requests recently.')
                    print("Too many requests")
                    random_num = random.randint(30, 40)
                    sleep(random_num)
                # Reload if error message not visible
                except:
                    driver.get(links[x])
                    print("Error. Needed reload")
            # Check if item has tables
            try:
                wait_till((By.ID, "market_commodity_forsale"))
                sleep(1)
                sell_body = driver.find_element(by=By.ID, value='market_commodity_forsale').text
                buy_body = driver.find_element(by=By.ID, value='market_commodity_buyrequests').text
                if sell_body != 'There are no active listings for this item.':
                    clean_body = sell_body.split(' ')
                    sell_quantity = clean_body[0]
                    selling_price = clean_body[5]
                    name = driver.find_element(by=By.ID, value='largeiteminfo_item_name').text
                    skin_stats['name'] = name
                    skin_stats['selling_price'] = float(selling_price.strip('$'))
                    # noinspection PyTypedDict
                    skin_stats['sell_quantity'] = int(sell_quantity)
                else:
                    print('No active sell listings')
                    skin_stats['selling_price'] = 0
                    skin_stats['sell_quantity'] = 0
                if buy_body != 'There are no active listings for this item.':
                    clean_body = buy_body.split(' ')
                    buy_quantity = clean_body[0]
                    buy_price = clean_body[5]
                    skin_stats['buying_price'] = float(buy_price.strip('$'))
                    skin_stats['buy_quantity'] = int(buy_quantity)
                else:
                    print("No active buy listings")
                    skin_stats['buying_price'] = 0
                    skin_stats['buy_quantity'] = 0
            ## Check if it's weapon
            except TimeoutException:
                ## Make sure it loaded
                try:
                    wait_till((By.CLASS_NAME, "market_listing_table_header"), seconds=5)
                    buy_body = driver.find_element(by=By.ID, value='market_commodity_buyrequests').text
                    sell_body = driver.find_element(by=By.CLASS_NAME, value='market_table_value').text
                    if sell_body != '':
                        sell_quantity = driver.find_element(by=By.ID, value='searchResults_total').text
                        selling_price = sell_body[1:5]
                        name = driver.find_element(by=By.ID, value='largeiteminfo_item_name').text
                        skin_stats['name'] = name
                        skin_stats['selling_price'] = float(selling_price.strip('$'))
                        # noinspection PyTypedDict
                        skin_stats['sell_quantity'] = int(sell_quantity)
                    else:
                        print('No active sell listings')
                        skin_stats['selling_price'] = 0
                        skin_stats['sell_quantity'] = 0
                    if buy_body != 'There are no active listings for this item.':
                        clean_body = buy_body.split(' ')
                        buy_quantity = clean_body[0]
                        buy_price = clean_body[5]
                        skin_stats['buying_price'] = float(buy_price.strip('$'))
                        skin_stats['buy_quantity'] = int(buy_quantity)
                    else:
                        print("No active buy listings")
                        skin_stats['buying_price'] = 0
                        skin_stats['buy_quantity'] = 0
                except:
                    print('Page did not load correctly')
            finally:
                print(skin_stats)
                profit = str(round(((round(skin_stats['selling_price'] / 1.15, 2) / skin_stats[
                    'buying_price']) - 1.02) * 100)) + '%'
                a.write('\n' + str(round(skin_stats['selling_price'] / 1.15, 2)) + " | " + str(
                    skin_stats['buying_price']) + ' | ' + profit + ' | ' + skin_stats['name'] + ' |  Page ' + str(
                    pages))
                # Check if it's profitable
                if skin_stats['buy_quantity'] and skin_stats['sell_quantity'] >= order_quantity:
                    if skin_stats['selling_price'] / 1.15 - skin_stats['buying_price'] > 0.1:
                        profit = str(round(((round(skin_stats['selling_price'] / 1.15, 2) / skin_stats[
                            'buying_price']) - 1.02) * 100)) + '%'
                        print(colored(str(round(skin_stats['selling_price'] / 1.15, 2)) + ' | ' + str(
                            skin_stats['buying_price']) + '  | ' + profit, 'magenta'))
                        print(skin_stats['name'])
                        f.write('\n' + str(round(skin_stats['selling_price'] / 1.15, 2)) + str(skin_stats['buying_price']) + ' | ' + profit + ' | ' + skin_stats['name'] + ' |  Page ' + str(pages))
                print(colored(str(counter) + ' / ' + total_skins, 'yellow'))
                print(colored('OK', 'green'))
                counter += 1
                if counter >= int(total_skins):
                    print(colored(str(counter) + ' / ' + total_skins, 'yellow'))
                    print(colored('Finished', 'grey'))
                    break
                random_num = random.randint(15, 20)
                # print('sleep ' + str(random_num))
                sleep(random_num)


game = int(input('1. CSGO \n 2.UNTURED (page 200)   '))
start_page = int(input("Enter on which page to start: "))
end_page = int(input("Enter on which page to end: "))
if game is not None:
    f.write('\n'+"Start Session     " + current_time + '\n')
    scrape_page(start_page, end_page)
    f.write('\n')
    f.write("End Session     " + current_time + '\n')
    driver.close()
driver.quit()