import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """アプリ全体で使う設定値をまとめるクラスです。"""

    google_credentials_file: str
    spreadsheet_id: str
    worksheet_name: str
    form_url: str
    first_data_row: int
    max_rows: int
    done_status: str
    wait_seconds: int
    name_selector: str
    email_selector: str
    phone_selector: str
    address_selector: str
    submit_selector: str


def _get_required_env(name: str) -> str:
    """必須の環境変数を取得します。未設定ならわかりやすいエラーにします。"""
    value = os.getenv(name)
    if not value:
        raise ValueError(f".env に {name} を設定してください。")
    return value


def _get_int_env(name: str, default: int) -> int:
    """数値の環境変数を取得します。未設定なら初期値を使います。"""
    value = os.getenv(name)
    if not value:
        return default

    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{name} は数値で設定してください。現在の値: {value}") from error


def load_config() -> Config:
    """`.env` を読み込み、Configとして返します。"""
    load_dotenv()

    return Config(
        google_credentials_file=_get_required_env("GOOGLE_CREDENTIALS_FILE"),
        spreadsheet_id=_get_required_env("SPREADSHEET_ID"),
        worksheet_name=_get_required_env("WORKSHEET_NAME"),
        form_url=_get_required_env("FORM_URL"),
        first_data_row=_get_int_env("FIRST_DATA_ROW", 2),
        max_rows=_get_int_env("MAX_ROWS", 600),
        done_status=os.getenv("DONE_STATUS", "完了"),
        wait_seconds=_get_int_env("WAIT_SECONDS", 10),
        name_selector=_get_required_env("NAME_SELECTOR"),
        email_selector=_get_required_env("EMAIL_SELECTOR"),
        phone_selector=_get_required_env("PHONE_SELECTOR"),
        address_selector=_get_required_env("ADDRESS_SELECTOR"),
        submit_selector=_get_required_env("SUBMIT_SELECTOR"),
    )
