# -*- coding: utf-8 -*-
from os.path import isdir, join
from os import makedirs
import sys
import re
import imghdr
import base64
import time

import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

http_regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)" #https://ihateregex.io/expr/url/


def process_svg(svg_container):
    embedded_images = svg_container.find_elements_by_tag_name("image")

    svg_content = svg_container.get_attribute("innerHTML")

    replacements = {}

    for image in embedded_images:
        image_url = image.get_attribute("xlink:href")
        if not re.match(http_regex, image_url):
            continue
        if image_url in replacements:
            continue

        image_file = requests.get(image_url)
        image_type = imghdr.what(None, h=image_file.content)
        if not image_type:
            continue
        b64_content = base64.b64encode(image_file.content).decode()

        embedded_text = f"data:image/{image_type};base64,{b64_content}"

        replacements[image_url] = embedded_text

    for url, embedded_image in replacements.items():
        svg_content = svg_content.replace(url, embedded_image)

    return svg_content


def capture_gslide(gslide_url, save_folder=''):
    """ take screenshots of Google Slide
        gslide_url: url to the google slide presentation
        save_folder: where to save the captured images to
    """
    
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=3840x2160")
    options.add_argument("headless")

    driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(),
        options=options
    )

    driver.get(gslide_url)
    time.sleep(1)

    actions = ActionChains(driver)
    actions.send_keys(Keys.END)
    actions.perform()
    time.sleep(3) # should actually wait until it is fully loaded; 3 seconds is plenty.

    hover_slide_number = driver.find_element_by_id(":d")

    n_slides = int(hover_slide_number.get_attribute("innerHTML"))

    keys = Keys()
    actions = ActionChains(driver)
    actions.send_keys(keys.ARROW_LEFT)

    for folder in [ 
        join(save_folder, "svg"),
        join(save_folder, "svg_processed"),
        join(save_folder, "png")
    ]:
        if not isdir(folder):
            makedirs(folder) 

    def save_page(page_nr):
        svg_container = driver.find_element_by_class_name("punch-viewer-svgpage-svgcontainer")
    
        svg_unprocessed = svg_container.get_attribute("innerHTML")
        svg_processed = process_svg(svg_container)

        svg_file = join(save_folder, "svg", f"{page_nr}.svg")
        processed_svg_file = join(save_folder, "svg_processed", f"{page_nr}.svg")
        png_file = join(save_folder, "png", f"{page_nr}.png")

        with open(svg_file, "wb") as file:
            file.write(svg_unprocessed.encode("utf-8"))

        with open(processed_svg_file, "wb") as file:
            file.write(svg_processed.encode("utf-8"))

        try:
            svg_container.screenshot(png_file)
        except WebDriverException as e:
            if hasattr(e, 'msg') and "screenshot with 0 width" in e.msg:
                viewer = driver.find_element_by_class_name("punch-viewer-content")
                viewer.screenshot(png_file)

        print(f"Page {page_nr} was captured.")

    for page_nr in range(n_slides, 0, -1):
        try:
            save_page(page_nr)
        except StaleElementReferenceException:
            time.sleep(5)
            try: 
                save_page(page_nr)
            except:
                print("Error saving page {page_nr}.")

        time.sleep(2) # todo: figure out a way to tell when new slide is succesfully loaded; then this weird repetition wouldn't be necessary

        actions.perform()

    print('DONE')

if __name__ == "__main__":
    args = sys.argv

    gslide_url = args[1]
    save_folder = args[2]

    if not isdir(save_folder):
        makedirs(save_folder)

    capture_gslide(args[1], args[2])
