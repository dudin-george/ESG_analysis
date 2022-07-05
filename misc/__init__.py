import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.firefox import GeckoDriverManager  # type: ignore
from selenium.webdriver.firefox.service import Service


def get_browser() -> webdriver.Firefox:
    docker = os.environ.get("DOCKER", "false") == "true"
    if docker:
        browser = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.FIREFOX)
    else:
        gecko = Service(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=gecko)  # type: ignore
    return browser
