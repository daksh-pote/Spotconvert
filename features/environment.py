from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from flask import url_for
import threading
import time
from app import app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def before_all(context):
    logger.info("Setting up test environment")
    app.config['TESTING'] = True
    context.client = app.test_client()
    
    # Start Flask server
    context.server = threading.Thread(target=lambda: app.run(port=5000))
    context.server.daemon = True
    context.server.start()
    time.sleep(2)  # Wait for server to start
    # Push app context so url_for and other Flask helpers work in steps
    context.app_context = app.app_context()
    context.app_context.push()
    logger.info("Flask server started")

def before_scenario(context, scenario):
    logger.info(f"Starting scenario: {scenario.name}")
    # Initialize WebDriver for UI and Acceptance tests (both need a browser)
    tags = [t.lower() for t in (list(scenario.feature.tags) + list(scenario.tags))]
    if 'ui' in tags or 'acceptance' in tags:
        logger.info("Setting up WebDriver for UI test")
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Install ChromeDriver
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver installed at: {driver_path}")
            
            # Initialize WebDriver
            service = Service(driver_path)
            context.driver = webdriver.Chrome(service=service, options=options)
            context.driver.set_window_size(1280, 800)
            context.driver.implicitly_wait(10)
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        logger.info("Cleaning up WebDriver")
        try:
            context.driver.quit()
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")

def after_all(context):
    logger.info("Cleaning up test environment")
    if hasattr(context, 'server'):
        context.server.join(1)
    # Pop app context if it was pushed
    if hasattr(context, 'app_context'):
        try:
            context.app_context.pop()
        except Exception:
            pass
    logger.info("Test environment cleanup complete")
