import chainlit as cl
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
import time
import os



# API key for Google Generative AI
api_key = 'AIzaSyANaYZ8rmgmGJrTIQYUTECoVvQYXc0Gbyo'
genai.configure(api_key=api_key)

# Initialize the Gemini models
model_1 = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are an assistant for browsing the internet and doing important tasks. Give a step-by-step instruction about the query.")
model_2 = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are an assistant for browsing the internet. Extract important links and output them or create a search prompt to be used on Google. export only the link or the search prompt. Don't export unnecessary words!")

def setup_driver():
    """Set up Selenium WebDriver."""
    logging.info("Setting up Selenium WebDriver")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)

def search_on_google(query):
    """Perform a Google search for the given query."""
    driver = setup_driver()
    try:
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        logging.info("Found %d search results")
        screenshot_path = "screenshot.png"  # Save the screenshot as a PNG file
        driver.save_screenshot(screenshot_path)
        logging.info("Screenshot taken")
        print(f"Screenshot saved at: {screenshot_path}")
        
        #search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        

        # Extract search result links
        #results = driver.find_elements(By.CSS_SELECTOR, "a h3")
        #links = [link.find_element(By.XPATH, "..").get_attribute("href") for link in results if link]
        #logging.info("Found %d search results", len(links))
        #return links, driver
    except Exception as e:
        logging.error("An error occurred during search: %s", e)
        driver.quit()
        raise


def follow_links_and_execute_instructions(driver, links, instructions):
    """Follow links and execute instructions on each website."""
    try:
        for i, link in enumerate(links):
            logging.info("Opening link: %s", link)
            driver.get(link)
    except Exception as e:
        logging.error("Error during link interaction: %s", e)

@cl.on_message
async def main(message: cl.Message):
    """Handles incoming messages from the user."""
    try:
        # Generate response using the Gemini model
        response_1 = model_1.generate_content(message.content)
        prompt_1 = response_1.text
        response_2 = model_2.generate_content(prompt_1)
        prompt_2 = response_2.text

        # Send the responses back to the user
        await cl.Message(content=response_1.text).send()
        await cl.Message(content=response_2.text).send()
        logging.info("Searching Google for: %s", prompt_2)

        screenshot_path= search_on_google(prompt_2)
        
        #follow_links_and_execute_instructions(driver, links, prompt_2)

        # Check if the screenshot exists and send it to the user
        if os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as img_file:
                await cl.Image(name="Search Results Screenshot", content=img_file.read()).send()

        # Take a screenshot of the new page and send it to the user
        if os.path.exists("screenshot.png"):
            with open("screenshot.png", "rb") as img_file:
                await cl.Image(name="New Page Screenshot", content=img_file.read()).send()
        
    except Exception as e:
        # Handle potential errors during processing
        await cl.Message(content=f"An error occurred: {str(e)}").send()

if __name__ == "__main__":
    cl.app.start()