import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def build_hash_table(strings):
    hash_table = {}
    for string in strings:
        hash_value = hash(string)  # Calculate the hash value for the string
        hash_table[hash_value] = string  # Store the string in the hash table using the hash value as the key
    return hash_table

def check_string_in_list(string, hash_table):
    hash_value = hash(string)  # Calculate the hash value for the string
    return hash_value in hash_table  # Check if the hash value exists in the hash table

def read_list_from_file(filename):
    with open(filename, 'r') as file:
        data = file.readlines()
        # Remove newline characters and any leading/trailing whitespace
        data = [line.strip() for line in data]
    return data

def write_list_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write('\n'.join(data))

filename = "users.txt"
# Get the Selenium logger
#logging.getLogger('selenium').setLevel(logging.WARNING)
#logging.getLogger("requests").setLevel(logging.WARNING)
#logging.getLogger("urllib3").setLevel(logging.WARNING)

# Disable logging for the Chrome driver
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)

amountFriend = 5000
userName = "Username"
password = "Password"
commentFriend = "N"

# Enter Username
#print("Enter Username:")
#userName = input()

# Enter Password
#print("Enter Password:")
#password = input()

#print("How many friends you want to add:")
#amountFriend = int(input())

#print("Send default comment on friend page? Y/N")
#commentFriend = input().upper()

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--log-level=3")

# Set up Chrome driver
driver_service = Service('')  # Replace 'path_to_chromedriver' with the actual path to chromedriver executable
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Enter URL
driver.maximize_window()
driver.get("https://myanimelist.net/login.php")

# Enter Username/Password
driver.find_element(By.ID, "loginUserName").send_keys(userName)
driver.find_element(By.ID, "login-password").send_keys(password + Keys.ENTER)

# Check for login
time.sleep(1)
login = len(driver.find_elements(By.CLASS_NAME, "badresult"))
dataset = read_list_from_file(filename)
hash_table = build_hash_table(dataset)
start = time.time()
if login == 0:
    amountFriendCounter = 0

    # Navigate to Users
    while True:
        driver.get("https://myanimelist.net/users.php")
        time.sleep(2)

        friends = driver.find_elements(By.XPATH, "//*[@class='borderClass']/div[1]/a")

        for friend in friends:
            urlName = friend.text
            dataset = read_list_from_file(filename)
            if check_string_in_list(urlName, hash_table):
                print(f"Checked Duplicate: {friend.text}")
                continue
            driver.execute_script("window.open();")
            tabs = driver.window_handles
            driver.switch_to.window(tabs[1])
            driver.get("https://myanimelist.net/profile" + "/" + urlName)

            time.sleep(2)

            # Check if user exists
            is404 = len(driver.find_elements(By.CLASS_NAME, "error404"))

            # Check if request is available
            isRequest = len(driver.find_elements(By.CSS_SELECTOR, "[class*='icon-user-function icon-request js-user-function disabled']"))

            # Check if already a friend
            isFriend = len(driver.find_elements(By.CSS_SELECTOR, "[class*='icon-user-function icon-remove js-user-function']"))

            # Check if comments are available
            isComment = len(driver.find_elements(By.CLASS_NAME, "textarea"))

            if is404 > 0:
                print("There is no such a user name: " + urlName)
                driver.close()
                driver.switch_to.window(tabs[0])
                continue

            if isRequest > 0:
                print(urlName + " Is Not Accepting Friend Request")
                driver.close()
                driver.switch_to.window(tabs[0])
                continue

            if isFriend > 0:
                print(urlName + " is already a friend of yours")
                dataset.append(urlName)
                write_list_to_file(filename, dataset)
                hash_value = hash(urlName)  
                hash_table[hash_value] = urlName
                driver.close()
                driver.switch_to.window(tabs[0])
                continue

            if isComment > 0 and commentFriend == "Y":
                # Add Some Comments
                comments = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "textarea")))
                comments.send_keys("Hi there, I like watching anime and talking about it so I'm looking for friends.")

                submitButton = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='lastcomment']/div/form/div/input")))
                submitButton.click()

                time.sleep(2)
            elif isComment == 0 and commentFriend == "Y":
                print("User Doesn't have Comments Turned On")
            try:
                # Send Friend Request
                request = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='request']")))
                request.click()

                request_Submit = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/div[3]/input[1]")))
                request_Submit.click()

                amountFriendCounter += 1

                print(urlName + " Added")
                dataset.append(urlName)
                write_list_to_file(filename, dataset)
                hash_value = hash(urlName)  
                hash_table[hash_value] = urlName
                end = time.time()
                executiontime = end - start
                sleeptime = random.randint(25,36)-executiontime
                time.sleep(sleeptime)
                realend = time.time()
                print(f"Check Time: {realend-start}")
                start = time.time()
            except:
                continue

            if amountFriendCounter == amountFriend:
                driver.close()
                driver.switch_to.window(tabs[0])
                break
            driver.close()
            driver.switch_to.window(tabs[0])

        if amountFriendCounter != amountFriend:
            print("Not All " + str(amountFriend) + " Friends Added Refreshing User Page")
            continue

        driver.execute_script("alert('All Friends Added Successfully! Program Closing In 3 Seconds');")
        time.sleep(3)
        driver.quit()
        break
else:
    driver.execute_script("alert('Username/Password Is Wrong, Program Shutting Down In 2 Seconds');")
    time.sleep(2)
    driver.quit()
