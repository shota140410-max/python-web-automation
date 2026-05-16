from dataclasses import dataclass

import gspread


@dataclass(frozen=True)
class SheetRow:
    """スプレッドシート1行分のデータです。row_number は実際の行番号です。"""

    row_number: int
    name: str
    email: str
    phone: str
    address: str
    status: str


class SheetClient:
    """Googleスプレッドシートの読み取り・更新を担当します。"""

    def __init__(self, credentials_file: str, spreadsheet_id: str, worksheet_name: str):
        # サービスアカウントJSONを使ってGoogle Sheets APIへ接続します。
        self.client = gspread.service_account(filename=credentials_file)
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        self.worksheet = self.spreadsheet.worksheet(worksheet_name)

    def get_rows(self, first_data_row: int, max_rows: int) -> list[SheetRow]:
        """A〜E列から最大 max_rows 件のデータを取得します。"""
        last_row = first_data_row + max_rows - 1

        # A列: 名前、B列: メール、C列: 電話、D列: 住所、E列: ステータス
        values = self.worksheet.get(f"A{first_data_row}:E{last_row}")

        rows: list[SheetRow] = []
        for index, row_values in enumerate(values):
            row_number = first_data_row + index

            # 行の列数が足りない場合でもエラーにならないよう、空文字で埋めます。
            padded_values = row_values + [""] * (5 - len(row_values))

            rows.append(
                SheetRow(
                    row_number=row_number,
                    name=padded_values[0],
                    email=padded_values[1],
                    phone=padded_values[2],
                    address=padded_values[3],
                    status=padded_values[4],
                )
            )

        return rows

    def mark_done(self, row_number: int, done_status: str) -> None:
        """指定行のE列に完了ステータスを書き込みます。"""
        self.worksheet.update_cell(row_number, 5, done_status)
