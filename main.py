from time import sleep
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from datetime import datetime
from termcolor import colored


# Variables
page = 45
# Curent Time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
# Open file
f = open("data.txt", "a")

skin_stats = {
    'name': '',
    'selling_price': '',
    'buying_price': '',
    'sell_quantity': '',
    'buy_quantity': '',
}
# Create file

s=Service("C:/Users/Vlad/PycharmProjects/chromedriver.exe")
driver = webdriver.Chrome(service=s)

def wait_till(element):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((element))
    )


def scrape_page(min, max):
    counter = 1
    for pages in range(min, max):
        total_skins  = str((max - min) * 10)
        links = []
        if game == 1:
            steam_url = 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Type%5B%5D=tag_CSGO_Tool_Sticker&appid=730#p' + str(pages) + '_price_asc'
        elif game == 2:
            steam_url = 'https://steamcommunity.com/market/search?appid=304930#p' + str(pages) + '_quantity_desc'
        print('#p'+str(pages))
        driver.get(steam_url)
        sleep(5)
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
            link = driver.find_element(by=By.ID, value='resultlink_' + str(item)).get_attribute('href')
            links.append(link)
        # Scrape every skin data
        for x in range(0, len(links)):
            driver.get(links[x])
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "hover_item_name"))
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
                wait_till((By.CLASS_NAME, "market_commodity_orders_header_promote"))
                sell_body = driver.find_element(by=By.ID, value='market_commodity_forsale').text
                buy_body = driver.find_element(by=By.ID, value='market_commodity_buyrequests').text
                if sell_body != 'There are no active listings for this item.':
                    clean_body = sell_body.split(' ')
                    sell_quantity = clean_body[0]
                    selling_price = clean_body[5]
                    name = driver.find_element(by=By.ID, value='largeiteminfo_item_name').text
                    skin_stats['name'] = name
                    skin_stats['selling_price'] = float(selling_price.strip('$'))
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
                # Check if it's profitable
                if skin_stats['buy_quantity'] and skin_stats['sell_quantity'] >= 40:
                    if skin_stats['selling_price'] / 1.15 - skin_stats['buying_price'] > 0.1:
                        profit = str(round(((round(skin_stats['selling_price'] / 1.15, 2) / skin_stats[
                            'buying_price']) - 1.02) * 100)) + '%'
                        print(colored(str(round(skin_stats['selling_price'] / 1.15, 2)) + ' | ' + str(
                            skin_stats['buying_price']) + '  | ' + profit, 'magenta'))
                        print(skin_stats['name'])
                        f.write('\n' + str(round(skin_stats['selling_price'] / 1.15, 2)) + str(
                            skin_stats['buying_price']) + ' | ' + profit + ' | ' + skin_stats[
                                    'name'] + ' |  Page ' + str(pages))
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
            # Not tables
            except TimeoutException:
                print('Not Sticker')
                wait_till((By.CLASS_NAME, "market_listing_table_header"))
                sell_body = driver.find_element(by=By.ID, value='market_commodity_buyrequests').text
                buy_body = driver.find_element(by=By.CLASS_NAME, value='market_listing_price market_listing_price_with_fee').text
                print(sell_body+ " "+ buy_body)

game = int(input('1. CSGO \n 2.UNTURED (page 200)   '))
start_page = int(input("Enter on which page to start: "))
end_page = int(input("Enter on which page to end: "))
if game is not None:
    f.write('\n'+"Start Session     " + current_time + '\n')
    scrape_page(start_page, end_page)
    f.write('\n')
    f.write("End Session     " + current_time + '\n')
    driver.close()
