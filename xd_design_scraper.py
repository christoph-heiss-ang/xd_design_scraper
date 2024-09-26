import os
import time
import re
import base64  # Import the base64 module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # Replace with the password required to access the website
    PASSWORD = 'NextG&dkdDs58'

    # URL of the Adobe XD shared link
    URL = 'https://xd.adobe.com/view/26d8fab4-3538-4275-7791-5efc7f7c266c-50e9/'

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/chromium-browser'  # Update this path if necessary
    # Uncomment the following line to run in headless mode
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--lang=en-US")  # Set language to English

    # Path to Chromedriver executable
    chromedriver_path = '/usr/bin/chromedriver'  # Update this path if necessary

    # Initialize the WebDriver with Service and Options
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(URL)

        # Wait for the page to load
        wait = WebDriverWait(driver, 30)

        # Wait for the password input to be present
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))

        # Enter the password
        password_input.send_keys(PASSWORD)

        # Find and click the submit button (which may initially be disabled)
        submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

        # Wait until the submit button is enabled
        wait.until(lambda d: submit_button.is_enabled())
        submit_button.click()

        time.sleep(10)

        # Wait for the main content to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-auto="screenNumbers"]')))

        # Create the 'design' directory if it doesn't exist
        os.makedirs('design', exist_ok=True)

        # Retrieve and process the screen numbers text
        try:
            screen_numbers_text = driver.find_element(By.CSS_SELECTOR, 'div[data-auto="screenNumbers"]').text
            print(f"Screen numbers text: '{screen_numbers_text}'")

            # Use regex to extract the total number of screens
            match = re.search(r'(\d+)\D+(\d+)', screen_numbers_text)
            if match:
                current_screen = int(match.group(1))
                total_screens = int(match.group(2))
            else:
                print("Could not extract total number of screens.")
                total_screens = 1  # Default to 1 or handle appropriately

            print(f"Total screens: {total_screens}")
        except Exception as e:
            print(f"An error occurred while retrieving total screens: {e}")
            total_screens = 1  # Default to 1 or handle appropriately

        for i in range(total_screens):
            try:
                # Wait until the canvas element is present
                canvas = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas#canvas-1')))

                # Scroll to the canvas element
                driver.execute_script("arguments[0].scrollIntoView(true);", canvas)
                
                #Screenshot
                canvas_base64 = canvas.screenshot_as_base64
                image_data = base64.b64decode(canvas_base64)
                filename = f"{i+1:03d}.png"
                with open(os.path.join('design', filename), 'wb') as f:
                    f.write(image_data)
                print(f"Saved {filename}")
                # Extract the canvas content as a data URL
                # try:
                #     data_url = driver.execute_script("""
                #         var canvas = document.querySelector('canvas#canvas-1');
                #         return canvas.toDataURL('image/png').substring(22);  // Remove 'data:image/png;base64,'
                #     """)
                # except JavascriptException as js_exc:
                #     print(f"JavaScript exception occurred: {js_exc}")
                #     data_url = None

                # if data_url:
                #     # Decode the base64 data and save the image
                #     image_data = base64.b64decode(data_url)
                #     filename = f"{i+1:03d}.png"
                #     with open(os.path.join('design', filename), 'wb') as f:
                #         f.write(image_data)
                #     print(f"Saved {filename}")
                # else:
                #     print(f"Failed to retrieve canvas data on screen {i+1}")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Design image not found on screen {i+1}: {e}")

            # Click the 'Next' button to go to the next screen
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button[data-auto="nextBtn"]')
                next_button.click()
                # Wait for the canvas to update before proceeding
                time.sleep(1)  # Adjust or use an explicit wait if necessary
            except NoSuchElementException:
                print("Next button not found or reached the last screen.")
                break

        print("All designs have been saved.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
