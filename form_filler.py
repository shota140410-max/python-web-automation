import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config
from sheets import SheetRow


class FormFiller:
    """Chromeを操作してWebフォームへ入力するクラスです。"""

    def __init__(self, config: Config):
        # config にはフォームURLやCSSセレクタなど、.envから読み込んだ設定が入っています。
        self.config = config

        # Chromeの操作に使うdriverです。start_browser() の中で実際に作成します。
        self.driver: WebDriver | None = None

    def start_browser(self) -> None:
        """Chromeを起動します。"""
        # Selenium 4 は基本的にChromeDriverを自動で見つけて起動できます。
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def open_form(self) -> None:
        """指定されたフォームURLを開きます。"""
        driver = self._get_driver()
        driver.get(self.config.form_url)

    def fill_and_submit(self, row: SheetRow) -> None:
        """1行分のデータをフォームに入力し、登録ボタンをクリックします。"""
        driver = self._get_driver()

        # 送信後に別ページへ移動するフォームでも次の行を処理できるよう、
        # 1件ごとにフォームURLを開き直します。
        driver.get(self.config.form_url)

        self._input_text(self.config.name_selector, row.name)
        self._input_text(self.config.email_selector, row.email)
        self._input_text(self.config.phone_selector, row.phone)
        self._input_text(self.config.address_selector, row.address)

        # 入力が終わったら、登録ボタンがクリックできる状態になるまで待ちます。
        submit_button = self._wait_until_clickable(self.config.submit_selector)
        submit_button.click()

        # 登録後すぐ次の行へ進むと、フォーム側の処理が間に合わないことがあります。
        # そのため、送信後に2秒待機します。
        time.sleep(2)

    def close(self) -> None:
        """Chromeを閉じます。"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _input_text(self, selector: str, value: str) -> None:
        """CSSセレクタで要素を探し、文字を入力します。"""
        element = self._wait_until_visible(selector)
        element.clear()
        element.send_keys(value)

    def _wait_until_visible(self, selector: str):
        """指定したCSSセレクタの要素が表示されるまで待ちます。"""
        driver = self._get_driver()
        wait = WebDriverWait(driver, self.config.wait_seconds)
        return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))

    def _wait_until_clickable(self, selector: str):
        """指定したCSSセレクタの要素がクリックできるまで待ちます。"""
        driver = self._get_driver()
        wait = WebDriverWait(driver, self.config.wait_seconds)
        return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))

    def _get_driver(self) -> WebDriver:
        """driverが未起動のまま使われた場合に、原因がわかるエラーを出します。"""
        if self.driver is None:
            raise RuntimeError("Chromeが起動していません。start_browser() を先に呼び出してください。")
        return self.driver
