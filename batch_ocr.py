#!/usr/bin/env python3
"""
PDFファイルのバッチOCR処理スクリプト

input_files/ ディレクトリ内の全PDFファイルに対してOCR処理を実行し、
結果を output/ ディレクトリに保存します。
"""

import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple
import argparse


def find_pdf_files(input_dir: Path) -> List[Path]:
    """指定ディレクトリ内の全PDFファイルを検索"""
    pdf_files = list(input_dir.glob("*.pdf"))
    pdf_files.sort()  # ファイル名順にソート
    return pdf_files


def merge_and_rename_output_files(
    pdf_path: Path,
    output_dir: Path,
    format: str
) -> bool:
    """
    yomitokuが生成したページごとのファイルを1つにマージし、リネーム

    Args:
        pdf_path: 元のPDFファイルのパス
        output_dir: 出力ディレクトリ
        format: 出力形式 (md, json, html, csv)

    Returns:
        成功フラグ
    """
    try:
        # yomitokuが生成したファイルを検索
        # パターン: input_files_test1_p1.md, input_files_test1_p2.md など
        pattern = f"*{pdf_path.stem}_p*.{format}"
        generated_files = list(output_dir.glob(pattern))

        if not generated_files:
            print(f"  ⚠️  生成ファイルが見つかりません: {pattern}")
            return False

        # ページ番号でソート（_p1, _p2, ...）
        def get_page_number(file_path: Path) -> int:
            # ファイル名から _pN の N を抽出
            stem = file_path.stem
            if '_p' in stem:
                page_str = stem.split('_p')[-1]
                try:
                    return int(page_str)
                except ValueError:
                    return 0
            return 0

        generated_files.sort(key=get_page_number)

        # 全ページのコンテンツを結合
        merged_content = []
        for file_path in generated_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content.append(content)

        # マージしたコンテンツを新しいファイルに保存
        output_file = output_dir / f"{pdf_path.stem}.{format}"

        # CSVの場合はヘッダー行の重複を削除
        if format == 'csv' and merged_content:
            lines_list = [content.split('\n') for content in merged_content]
            # 最初のファイルのヘッダーを保持
            header = lines_list[0][0] if lines_list[0] else ""
            all_lines = [header] if header else []

            # 各ファイルのヘッダー以外の行を追加
            for i, lines in enumerate(lines_list):
                if i == 0:
                    # 最初のファイルは全行追加
                    all_lines.extend(lines[1:])
                else:
                    # 2番目以降はヘッダーをスキップ
                    if lines and lines[0] == header:
                        all_lines.extend(lines[1:])
                    else:
                        all_lines.extend(lines)

            final_content = '\n'.join(all_lines)
        else:
            # MD/JSON/HTMLは単純に結合（改行2つで区切り）
            final_content = '\n\n'.join(merged_content)

        # ファイルに書き込み
        if format == 'csv':
            # CSVはUTF-8 BOM付きで保存
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(final_content)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_content)

        # 元の分割ファイルを削除
        for file_path in generated_files:
            file_path.unlink()

        return True

    except Exception as e:
        print(f"  ⚠️  ファイルマージエラー: {e}")
        return False


def move_processed_file(pdf_path: Path, processed_dir: Path) -> bool:
    """
    処理完了したPDFファイルをprocessed_filesディレクトリに移動

    Args:
        pdf_path: 処理したPDFファイルのパス
        processed_dir: 処理済みファイルの移動先ディレクトリ

    Returns:
        成功フラグ
    """
    try:
        # processed_filesディレクトリが存在しない場合は作成
        processed_dir.mkdir(parents=True, exist_ok=True)

        # ファイルを移動（shutil.moveを使うことでクロスデバイスの移動にも対応）
        destination = processed_dir / pdf_path.name
        shutil.move(str(pdf_path), str(destination))
        return True

    except Exception as e:
        print(f"  ⚠️  ファイル移動エラー: {e}")
        return False


def process_pdf(
    pdf_path: Path,
    output_dir: Path,
    format: str,
    processed_dir: Path,
    max_retries: int = 2
) -> Tuple[bool, str]:
    """
    単一PDFファイルをOCR処理

    Args:
        pdf_path: 処理するPDFファイルのパス
        output_dir: 出力ディレクトリ
        format: 出力形式 (md, json, html, csv)
        processed_dir: 処理済みファイルの移動先ディレクトリ
        max_retries: 最大リトライ回数

    Returns:
        (成功フラグ, エラーメッセージ)
    """
    for attempt in range(max_retries + 1):
        try:
            # yomitoku CLIコマンドを実行
            cmd = [
                'yomitoku',
                str(pdf_path),
                '-f', format,
                '-o', str(output_dir)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分でタイムアウト
            )

            if result.returncode == 0:
                # 生成されたファイルをマージ＆リネーム
                merge_success = merge_and_rename_output_files(pdf_path, output_dir, format)
                if not merge_success:
                    return False, "ファイルのマージに失敗しました"

                # 処理完了したPDFファイルをprocessed_filesに移動
                move_success = move_processed_file(pdf_path, processed_dir)
                if not move_success:
                    print(f"  ⚠️  PDFファイルの移動に失敗しましたが、OCR処理は完了しています")

                return True, ""
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                if attempt < max_retries:
                    print(f"  ⚠️  リトライ {attempt + 1}/{max_retries}: {pdf_path.name}")
                else:
                    return False, error_msg

        except subprocess.TimeoutExpired:
            if attempt < max_retries:
                print(f"  ⚠️  タイムアウト - リトライ {attempt + 1}/{max_retries}: {pdf_path.name}")
            else:
                return False, "処理がタイムアウトしました（10分超過）"
        except Exception as e:
            if attempt < max_retries:
                print(f"  ⚠️  エラー - リトライ {attempt + 1}/{max_retries}: {pdf_path.name}")
            else:
                return False, str(e)

    return False, "不明なエラー"


def main():
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(
        description='input_files/ 内の全PDFファイルをバッチOCR処理'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['md', 'json', 'html', 'csv'],
        default='md',
        help='出力形式 (デフォルト: md)'
    )
    parser.add_argument(
        '-i', '--input',
        default='input_files',
        help='入力ディレクトリ (デフォルト: input_files)'
    )
    parser.add_argument(
        '-o', '--output',
        default='output',
        help='出力ディレクトリ (デフォルト: output)'
    )
    parser.add_argument(
        '-p', '--processed',
        default='processed_files',
        help='処理済みファイルの移動先ディレクトリ (デフォルト: processed_files)'
    )

    args = parser.parse_args()

    # ディレクトリパスの設定
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    processed_dir = Path(args.processed)

    # 入力ディレクトリの存在確認
    if not input_dir.exists():
        print(f"❌ エラー: 入力ディレクトリが見つかりません: {input_dir}")
        sys.exit(1)

    # 出力ディレクトリの作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDFファイルを検索
    pdf_files = find_pdf_files(input_dir)

    if not pdf_files:
        print(f"❌ PDFファイルが見つかりませんでした: {input_dir}")
        sys.exit(1)

    print(f"📁 入力ディレクトリ: {input_dir}")
    print(f"📁 出力ディレクトリ: {output_dir}")
    print(f"📄 出力形式: {args.format}")
    print(f"📚 処理対象: {len(pdf_files)} ファイル")
    print("-" * 60)

    # バッチ処理
    failed_files = []

    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"[{idx}/{len(pdf_files)}] 処理中: {pdf_path.name}")

        success, error_msg = process_pdf(pdf_path, output_dir, args.format, processed_dir)

        if success:
            print(f"  ✅ 完了: {pdf_path.name}")
        else:
            print(f"  ❌ 失敗: {pdf_path.name}")
            failed_files.append((pdf_path.name, error_msg))

    # 結果サマリー
    print("-" * 60)
    print(f"✨ 処理完了!")
    print(f"  成功: {len(pdf_files) - len(failed_files)} / {len(pdf_files)} ファイル")

    if failed_files:
        print(f"  失敗: {len(failed_files)} ファイル")
        print("\n❌ 処理できなかったファイル:")
        for filename, error_msg in failed_files:
            print(f"  - {filename}")
            if error_msg:
                # エラーメッセージの最初の1行のみ表示（長すぎる場合）
                error_lines = error_msg.split('\n')
                print(f"    理由: {error_lines[0][:100]}")
        sys.exit(1)
    else:
        print("  🎉 全てのファイルが正常に処理されました！")


if __name__ == "__main__":
    main()
