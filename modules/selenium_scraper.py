"""
Advanced Selenium Scraper Module
Handles web automation for various online services like TTS, image generation, etc.
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json


class SeleniumScraper:
    """Advanced Selenium-based web scraper for automation tasks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = config.get("selenium", {}).get("headless", False)
        self.implicit_wait = config.get("selenium", {}).get("implicit_wait", 10)
        self.page_load_timeout = config.get("selenium", {}).get("page_load_timeout", 30)
        
    async def initialize_driver(self):
        """Initialize Chrome WebDriver with optimized settings"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Suppress Chrome logging messages
            chrome_options.add_argument("--log-level=3")  # Only show fatal errors
            chrome_options.add_argument("--disable-logging")
            
            window_size = self.config.get("selenium", {}).get("window_size", {})
            chrome_options.add_argument(f"--window-size={window_size.get('width', 1920)},{window_size.get('height', 1080)}")
            
            # Try to get ChromeDriver path
            try:
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(self.implicit_wait)
                self.driver.set_page_load_timeout(self.page_load_timeout)
                return True
            except Exception as e1:
                # If ChromeDriverManager fails, try without it (uses system PATH)
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    self.driver.implicitly_wait(self.implicit_wait)
                    self.driver.set_page_load_timeout(self.page_load_timeout)
                    return True
                except Exception as e2:
                    print(f"Error initializing driver: {e1}")
                    print(f"Fallback attempt also failed: {e2}")
                    print("💡 Make sure Chrome/Chromium is installed and ChromeDriver is in your PATH")
                    return False
        except Exception as e:
            print(f"Error initializing driver: {e}")
            return False
    
    def _is_driver_valid(self) -> bool:
        """Check if the driver session is still valid"""
        if not self.driver:
            return False
        try:
            # Try to get current URL to check if session is alive
            _ = self.driver.current_url
            return True
        except:
            return False
    
    async def _ensure_driver(self) -> bool:
        """Ensure driver is initialized and valid, reinitialize if needed"""
        if not self._is_driver_valid():
            # Clean up invalid driver
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            # Reinitialize
            return await self.initialize_driver()
        return True
    
    async def cleanup(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    async def text_to_speech_elevenlabs(self, text: str, voice_id: str = "default") -> Optional[str]:
        """Generate TTS using ElevenLabs website"""
        try:
            # Ensure driver is valid
            if not await self._ensure_driver():
                return None
            
            # Navigate to ElevenLabs TTS page
            url = "https://elevenlabs.io/app/voice-clone"
            try:
                self.driver.get(url)
            except Exception as e:
                # Session might have been lost, try to reinitialize
                if "invalid session" in str(e).lower() or "session deleted" in str(e).lower():
                    if await self._ensure_driver():
                        self.driver.get(url)
                    else:
                        return None
                else:
                    raise
            
            await asyncio.sleep(3)  # Wait for page load
            
            # Try to find and fill the text input
            try:
                # Look for text input area (common selectors for TTS sites)
                text_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
                text_input.clear()
                text_input.send_keys(text)
                
                # Look for generate/convert button
                generate_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Convert') or contains(text(), 'Create')]"))
                )
                generate_btn.click()
                
                # Wait for audio to be generated
                await asyncio.sleep(5)
                
                # Look for download button or audio element
                try:
                    download_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')] | //a[contains(text(), 'Download')]"))
                    )
                    
                    # Get the audio URL or download it
                    audio_url = download_btn.get_attribute("href")
                    if not audio_url:
                        # Try to find audio element directly
                        audio_elem = self.driver.find_element(By.TAG_NAME, "audio")
                        audio_url = audio_elem.get_attribute("src")
                    
                    return audio_url
                except TimeoutException:
                    # If download button not found, try to get audio from page
                    audio_elem = self.driver.find_element(By.TAG_NAME, "audio")
                    return audio_elem.get_attribute("src")
                    
            except Exception as e:
                print(f"Error in TTS generation: {e}")
                return None
                
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid session" in error_msg or "session deleted" in error_msg:
                # Try to recover by reinitializing
                print("⚠️ Browser session lost, attempting to recover...")
                if await self._ensure_driver():
                    # Retry once
                    try:
                        url = "https://elevenlabs.io/app/voice-clone"
                        self.driver.get(url)
                        await asyncio.sleep(3)
                        # Return None to let the alternative method try
                        return None
                    except:
                        pass
            print(f"Error in text_to_speech_elevenlabs: {e}")
            return None
    
    async def text_to_speech_alternative(self, text: str) -> Optional[str]:
        """Alternative TTS using Speechify or similar service"""
        try:
            # Ensure driver is valid
            if not await self._ensure_driver():
                return None
            
            url = "https://speechify.com/text-to-speech-online/"
            try:
                self.driver.get(url)
            except Exception as e:
                # Session might have been lost, try to reinitialize
                if "invalid session" in str(e).lower() or "session deleted" in str(e).lower():
                    if await self._ensure_driver():
                        self.driver.get(url)
                    else:
                        return None
                else:
                    raise
            await asyncio.sleep(3)
            
            # Find text input
            text_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea | //input[@type='text']"))
            )
            text_input.clear()
            text_input.send_keys(text)
            
            # Find and click generate button
            generate_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'generate') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'convert')]"))
            )
            generate_btn.click()
            
            await asyncio.sleep(5)
            
            # Get audio URL
            audio_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "audio"))
            )
            return audio_elem.get_attribute("src")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid session" in error_msg or "session deleted" in error_msg:
                print("⚠️ Browser session lost in alternative TTS")
            print(f"Error in text_to_speech_alternative: {e}")
            return None
    
    async def scrape_website_content(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Generic website scraper with custom selectors"""
        try:
            if not self.driver:
                success = await self.initialize_driver()
                if not success or not self.driver:
                    return {}
            
            self.driver.get(url)
            await asyncio.sleep(3)
            
            results = {}
            for key, selector in selectors.items():
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    results[key] = element.text if element.text else element.get_attribute("innerHTML")
                except:
                    results[key] = None
            
            return results
            
        except Exception as e:
            print(f"Error scraping website: {e}")
            return {}
    
    async def fill_form(self, url: str, form_data: Dict[str, str]) -> bool:
        """Fill and submit forms on websites"""
        try:
            if not self.driver:
                await self.initialize_driver()
            
            self.driver.get(url)
            await asyncio.sleep(3)
            
            for field_name, value in form_data.items():
                try:
                    # Try multiple selectors
                    selectors = [
                        (By.NAME, field_name),
                        (By.ID, field_name),
                        (By.XPATH, f"//input[@placeholder='{field_name}']"),
                        (By.XPATH, f"//textarea[@placeholder='{field_name}']")
                    ]
                    
                    element = None
                    for by, selector in selectors:
                        try:
                            element = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((by, selector))
                            )
                            break
                        except:
                            continue
                    
                    if element:
                        element.clear()
                        element.send_keys(value)
                        
                except Exception as e:
                    print(f"Error filling field {field_name}: {e}")
            
            # Try to submit form
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
                submit_btn.click()
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Error filling form: {e}")
            return False
    
    async def take_screenshot(self, url: str, save_path: str) -> Optional[str]:
        """Take a screenshot of a webpage"""
        try:
            if not self.driver:
                success = await self.initialize_driver()
                if not success or not self.driver:
                    return None
            
            self.driver.get(url)
            await asyncio.sleep(3)
            
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
            self.driver.save_screenshot(save_path)
            return save_path
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    async def download_file(self, url: str, save_path: str) -> Optional[str]:
        """Download file from URL using Selenium"""
        try:
            if not self.driver:
                await self.initialize_driver()
            
            # Configure download preferences
            download_prefs = {
                "download.default_directory": os.path.abspath(os.path.dirname(save_path)),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            
            chrome_options = Options()
            chrome_options.add_experimental_option("prefs", download_prefs)
            
            self.driver.get(url)
            await asyncio.sleep(2)
            
            # If direct download link, it should start automatically
            # Otherwise, try to find download button
            try:
                download_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'download')] | //button[contains(text(), 'Download')]"))
                )
                download_btn.click()
                await asyncio.sleep(5)
            except:
                pass
            
            return save_path if os.path.exists(save_path) else None
            
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
