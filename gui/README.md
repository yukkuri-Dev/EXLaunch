# libexword GUI モック (GTK+ / PyGObject)

## 概要
このフォルダには簡易 UI モックアップと最小限の PyGObject サンプルが入っています。
目的は Windows の開発環境でも簡単に UI を確認できるようにすることです（実際のデバイス連携は未実装）。

Files:
- `mockup.svg` : ワイヤーフレーム（ブラウザで開けます）
- `libexword_gui.ui` : Glade / GtkBuilder UI ファイル（GTK で読み込み可能）
- `sample.py` : PyGObject サンプル。`libexword_gui.ui` を読み込み、ダミーデータを表示します

## サンプルの実行方法（Linux）
1. 依存をインストール（Ubuntu など）:
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```
2. `EXLaunch` ルートで:
   ```bash
   python3 gui/sample.py
   ```

## Windows（開発環境）での確認
- `mockup.svg` をブラウザで開けばモックを見ることができます。
- PyGObject を試す場合は MSYS2 の mingw 環境で `mingw-w64-x86_64-python3-gobject` 等を入れて実行できます。
- **tkinter サンプル（Windowsで手軽に確認したい場合）**:
  - `python gui/tk_sample.py` を実行すると、ブラウザ不要で簡易 UI を確認できます（Python 標準ライブラリのみ使用）。

## 次のステップ
- libexword の C API を ctypes でラップして、デバイス検出 / ファイル一覧を GUI に接続します。
- 操作ボタンに実際の処理を紐付けます。

## 追加された操作（tk サンプル）
- Install ZIP: 辞書データの ZIP を選択して（モック）展開・インストールします。
- File Explorer: 電子辞書内のファイルを閲覧する機能（モック）
- 認証情報: GUI 内で自動生成され、マネージャからインポート/エクスポート可能になりました。
- Link (Auth): ユーザ名／キーを入力して認証リンクのモックを行います。

## メニュー追加
- メニュー「辞書管理」を追加しました。項目:
  - 追加 (From ZIP)...
  - 追加 (From folder)...
  - 追加 (From Github release)...
  - マネージャの一覧を表示
  - マネージャ内の辞書を削除