import os
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager  # type: ignore


def get_browser() -> webdriver.Firefox | webdriver.Remote:
    docker = os.environ.get("DOCKER", "false") == "true"
    if docker:
        browser = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.FIREFOX)
    else:
        gecko = Service(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=gecko)  # type: ignore
    return browser


def relative_path(cwd: str, path: str) -> str:
    return os.path.join(cwd, path)


def path_params_to_url(params: dict[str, Any]) -> str:
    return "?" + "&".join(f"{key}={value}" for key, value in params.items())
