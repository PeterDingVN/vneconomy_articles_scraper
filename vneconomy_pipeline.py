import subprocess
from pathlib import Path
import pandas as pd
import os
import signal
import logging

def scrapy_crawl_vnecon():
    # Type
    dict_ = {
        'ov': '-O',
        'ap': '-o'
    }

    type_ = input("ov or ap current scraped articles (overwrite/append)? ")
    if not type_ in dict_.keys():
        raise ValueError('Please type ov or ap')

    # Target folder
    target_folder_name = "vnecon"
    output_file = Path.cwd()/'vnecon_articles.jsonl' # check name of output file

    # Search for folder
    found_path = None
    for path in Path.cwd().rglob(target_folder_name):
        if path.is_dir():
            found_path = path
            break
    if not found_path:
        print(f"No folder: '{target_folder_name}'")
        return

    # Run scrapy
    try:
        subprocess.run(
            ["scrapy", "crawl", "vnecon", f"{dict_[type_]}", str(output_file)],
            cwd=found_path,
            check=True  # Raise error if spider fails
        )
    except subprocess.CalledProcessError as e:
        print(f"SCRAPY ERROR: {e.returncode}")
    except Exception as e:
        print("Unexpected error:", e)


def excel_cleaner():
    try:
        df = pd.read_json('vnecon_articles.jsonl', lines=True)
        if df.empty:
            return 'File vnecon_articles.jsonl is empty'
        else:
            df = df.dropna(subset='Content')
            df = df.drop_duplicates()
            df = df.sort_values(by=['Date'], ascending=False)
            df.to_excel("vnecon_articles.xlsx", index=False)

    except Exception as e:
        return f'ERROR: {e}'


def main():
    try:
        scrapy_crawl_vnecon()
        excel_cleaner()
    except KeyboardInterrupt:
        print('Process interrupted by USER')
    except Exception as e:
        print(f'ERROR: {e}')
    finally:
        excel_cleaner()

if __name__ == "__main__":
    main()