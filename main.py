import os
from playwright.sync_api import sync_playwright, Playwright, expect
import itertools
import time
import random
import shutil

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def chunk_images(folder_images, n):
    # Create a dictionary to store the chunks
    chunks = {}
    
    # Iterate over all the folders and image files in the dictionary
    for folder_name, image_files in folder_images.items():
        # Create an iterator for the image files
        it = iter(image_files)
        
        # Chunk the image files into groups of n
        folder_chunks = list(iter(lambda: list(itertools.islice(it, n)), []))
        
        # Add the chunks to the dictionary, using the folder name as the key
        chunks[folder_name] = folder_chunks
    
    return chunks

def extract_text_from_text_files(directory_path):
    # Create a dictionary to store the text from each folder
    folder_text = {}

    # # Iterate over all the folders and files in the directory
    for root, dirs, files in os.walk(directory_path):
        # Find the text file in the image files
        text_file = [os.path.join(os.path.basename(root), file) for file in files if file.endswith('.txt')]

        # If a text file was found
        if text_file:
            
            folder_name = os.path.basename(root)
            # If the folder name is 'processed', skip this iteration of the loop
            if folder_name == 'processed':
                continue

            # Open the text file and read the text from it
            with open(text_file[0], 'r') as file:
                text = file.read()

            # Add the text to the dictionary, using the folder name as the key
            folder_text[folder_name] = text

    return folder_text

def run(playwright: Playwright) -> None:

    # Set the email and password for the website
    email = "example@example.com"
    password = "p@ssw0rd"
    
    directory_path = os.path.dirname(os.path.realpath(__file__))

    # Create a dictionary to store the images from each folder
    folder_images = {}

    # Iterate over all the folders and files in the directory
    for root, dirs, files in os.walk(directory_path):
        # Filter out the image files and create paths with only the folder name and the image file name
        image_files = [os.path.join(os.path.basename(root), file) for file in files if file.endswith('.png') or file.endswith('.jpg')]
        
        # If there are any image files in the current folder
        if image_files:

            # Get the name of the folder
            folder_name = os.path.basename(root)
            # If the folder name is 'processed', skip this iteration of the loop
            if folder_name == 'processed':
                continue
            
            # Add the image files to the dictionary, using the folder name as the key
            folder_images[folder_name] = image_files

    folder_chunks = chunk_images(folder_images, 1)
    # Use the function to extract the text from the text files
    folder_text = extract_text_from_text_files(directory_path)

    # Launch the browser and log into the website
    browser = playwright.firefox.launch(headless=False) # Firefox is more stable than Chromium
    # browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto("https://www.cafepress.com/sell")
    page.get_by_label("Email").click()
    page.get_by_label("Email").fill(email) # change this to your email
    page.get_by_label("Email").press("Enter")
    page.get_by_label("Email").press("Tab")
    page.get_by_label("Password").fill(password) # change this to your password
    time.sleep(1)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")
    page.get_by_text("Design Library").click()
    # loop through the folder_chunks and upload the images
    for folder_name, chunks in folder_chunks.items():
        for images in chunks:
            page.wait_for_load_state("networkidle")
            page.get_by_role("button", name="Add Design").click()
            page.locator(".el-upload__input").nth(0).set_input_files(images)
            page.get_by_role("button", name="Add Details").click()
            page.wait_for_load_state("networkidle")
            if(len(images) > 1):
                page.locator("label").filter(has_text="Apply to All").locator("span").nth(1).click()
            page.get_by_placeholder("The name that will be shown").first.click()
            page.get_by_placeholder("The name that will be shown").first.fill(folder_name)
            page.get_by_text("Anyone").first.click()
            page.get_by_placeholder("Add search tag").first.click()
            page.get_by_placeholder("Add search tag").first.fill(folder_text[folder_name])
            page.get_by_role("button", name="Add Tag").first.click()
            page.get_by_role("button", name="Save").first.click()
            page.get_by_role("button", name="Make Products").click()
            page.wait_for_load_state("networkidle")
            # loop through the images and add them to the products
            for i in range(1, len(images)) :
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                page.wait_for_selector('input[placeholder="Search products"]')
                time.sleep(1)
                page.get_by_placeholder("Search products").click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                page.get_by_role("button", name="Next").click()
                page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            page.wait_for_selector('input[placeholder="Search products"]')
            time.sleep(1)
            page.get_by_placeholder("Search products").click()
            time.sleep(1)
            page.get_by_role("button", name="Save").click()
            for image in images:
                shutil.move(image, 'processed/' + os.path.basename(image))
            time.sleep(random.randint(5, 10)) # 15 to 30 seconds wait time

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)