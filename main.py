import traceback

from config import load_config
from form_filler import FormFiller
from sheets import SheetClient, SheetRow


def find_blank_fields(row: SheetRow) -> list[str]:
    """フォーム入力前に、必須項目が空欄になっていないか確認します。"""
    blank_fields: list[str] = []

    # strip() は前後の空白を取り除きます。空白だけの入力も空欄として扱います。
    if not row.name.strip():
        blank_fields.append("名前")
    if not row.email.strip():
        blank_fields.append("メールアドレス")
    if not row.phone.strip():
        blank_fields.append("電話番号")
    if not row.address.strip():
        blank_fields.append("住所")

    return blank_fields


def ask_start_confirmation(total_rows: int, target_rows: int) -> bool:
    """実行前に、ユーザーへ処理開始の最終確認をします。"""
    print("")
    print("========================================")
    print("処理開始前の確認")
    print("========================================")
    print(f"読み取った行数: {total_rows}件")
    print(f"今回処理予定の行数: {target_rows}件")
    print("Chrome上でログインとフォーム表示の準備ができていることを確認してください。")
    print("処理を開始すると、フォームへの入力と登録ボタンのクリックを自動で行います。")
    answer = input("処理を開始しますか？開始する場合は y を入力してください: ")

    return answer.strip().lower() == "y"


def main() -> None:
    """ツール全体の処理を上から順番に実行します。"""
    # .env に書いた設定値を読み込みます。
    config = load_config()

    print("Googleスプレッドシートに接続しています...")
    # スプレッドシート操作用のクラスを作成します。
    sheet_client = SheetClient(
        credentials_file=config.google_credentials_file,
        spreadsheet_id=config.spreadsheet_id,
        worksheet_name=config.worksheet_name,
    )

    print("スプレッドシートからデータを読み取っています...")
    rows = sheet_client.get_rows(
        first_data_row=config.first_data_row,
        max_rows=config.max_rows,
    )

    if not rows:
        print("処理対象の行がありません。")
        return

    # 完了済みの行は処理対象から外します。二重登録を防ぐためです。
    target_rows = [row for row in rows if row.status != config.done_status]

    if not ask_start_confirmation(total_rows=len(rows), target_rows=len(target_rows)):
        print("処理をキャンセルしました。")
        return

    # 件数集計用の変数です。最後にまとめて表示します。
    success_count = 0
    skipped_count = 0
    error_count = 0

    form_filler = FormFiller(config)

    try:
        print("Chromeを起動します...")
        form_filler.start_browser()
        form_filler.open_form()

        print("")
        print("Chromeで必要なログインを手動で行ってください。")
        print("ログインとフォーム表示の準備ができたら、この画面でEnterキーを押してください。")
        input("Enterで処理開始: ")

        for index, row in enumerate(rows, start=1):
            # 1行処理するたびに、全体の何件目かを表示します。
            print("")
            print(f"[進捗 {index}/{len(rows)}] {row.row_number}行目を確認しています。")

            # すでに完了している行は二重登録を避けるため処理しません。
            if row.status == config.done_status:
                print(f"{row.row_number}行目: すでに完了のため処理しません。")
                skipped_count += 1
                continue

            print(f"{row.row_number}行目: 処理を開始します。名前={row.name}")

            try:
                # Webフォームへ入力する前に、スプレッドシート側の空欄をチェックします。
                blank_fields = find_blank_fields(row)
                if blank_fields:
                    raise ValueError(f"必須項目が空欄です: {', '.join(blank_fields)}")

                form_filler.fill_and_submit(row)
                sheet_client.mark_done(row.row_number, config.done_status)
                success_count += 1
                print(f"{row.row_number}行目: 完了として記録しました。")
            except Exception:
                # エラーが出た行を黙って飛ばさず、内容を表示して処理を止めます。
                error_count += 1
                print("")
                print(f"{row.row_number}行目でエラーが発生しました。")
                print("この行は完了として記録していません。")
                print("エラー内容:")
                traceback.print_exc()
                break

        print("")
        print("========================================")
        print("処理を終了しました。")
        print("========================================")
        print(f"読み取った行数: {len(rows)}件")
        print(f"成功件数: {success_count}件")
        print(f"完了済みスキップ件数: {skipped_count}件")
        print(f"エラー件数: {error_count}件")
    finally:
        # ブラウザを開いたまま確認したい場合は、次の行をコメントアウトしてください。
        form_filler.close()


if __name__ == "__main__":
    main()
