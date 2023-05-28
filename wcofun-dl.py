#!/usr/bin/python3
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import argparse
from os import makedirs
from os.path import join, exists
import subprocess
import re
from tqdm import tqdm
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def parse_args():
    parser = argparse.ArgumentParser(
                        prog='wcofun-downloader',
                        description='downloads anime from wcofun.net')
    parser.add_argument("-l", "--link", help="link to anime page.")
    parser.add_argument("-f", "--file", help="path to a file containing direct download links and names")
    parser.add_argument('-s', "--save", help="save links in file and specify the filename.")
    parser.add_argument('-o', '--out', default=".")
    return parser.parse_args()


def get_links(driver, link):
    driver.get(link)
    selector = "div.cat-eps>a"
    tags = driver.find_elements(By.CSS_SELECTOR, selector)
    arr = []
    for tag in tags:
        name = tag.get_attribute('title')
        link = tag.get_attribute('href')
        parts = name.split(" Episode ")
        if len(parts) < 2:
            parts = name.split(" English")
            name = parts[0][6:]
        else:
            parts2 = parts[1].split(" ")
            name = f"{parts2[0].rjust(2,'0')} - {parts[0][6:]}"
        arr.append((name, link))
    return arr


# get video link
def get_download_link(driver, link):
    driver.get(link)
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "#cizgi-js-0")))
    vid = driver.find_element(By.CSS_SELECTOR, "video")
    l = vid.get_attribute("src")
    # HACK
    if l == "":
        sleep(0.5)
        l = vid.get_attribute("src")
    return l


# take a link and perform the dl command
def download(name, link, out):
    p = subprocess.run([
        "curl",
        link,
        "-H",
        "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "-H",
        "Accept: video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
        "-H",
        "Accept-Language: en-GB,en;q=0.5",
        "-H",
        "Range: bytes=0-",
        "-H",
        "DNT: 1",
        "-H",
        "Connection: keep-alive",
        "-H",
        "Referer: https://embed.watchanimesub.net/",
        "-H",
        "Sec-Fetch-Dest: video", 
        "-H", 
        "Sec-Fetch-Mode: no-cors", 
        "-H", 
        "Sec-Fetch-Site: cross-site", 
        "-H", 
        "Accept-Encoding: identity", 
        "-L",
        "-s",
        "--output",
        f"{out}/{name}.mp4"])


def read_from_file(path):
    arr = []
    with open(path, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(";")
            arr.append((parts[0], parts[1]))
    return arr


def save_links(links, path):
    with open(path, "w+") as f:
        for name, link in links:
            f.write(f"{name};{link}\n")


if __name__ == "__main__":
    args = parse_args()
    if not exists(args.out):
        makedirs(args.out)
    options = webdriver.ChromeOptions() 
    options.add_argument('--headless')
    options.add_argument("--incognito")
    options.add_argument("--nogpu")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1280")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    userAgent = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"
    if args.link is not None:
        with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": userAgent})
            links = get_links(driver, args.link)
            print("getting download links")
            links = [(name, get_download_link(driver, link)) for name, link in tqdm(links)]
            if args.save is not None:
                save_links(links, args.save)
            else:
                for name, link in tqdm(links):
                    download(name, link, args.out)
    elif args.file is not None:
        links = read_from_file(args.file)
        for name, link in tqdm(links):
            download(name, link, args.out)