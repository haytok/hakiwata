import glob
import os
import textwrap
import requests
import logging
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def paste_icon_image(base_img, icon_img):
    # 円形にアイコンを切り出す処理
    mask = Image.new('L', icon_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, icon_img.size[0], icon_img.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    icon_img.putalpha(mask)
    paste_img = Image.new('RGB', icon_img.size, (255, 255, 255))
    paste_img.paste(icon_img, mask=icon_img.convert('RGBA').split()[-1])

    y_pos = 75

    base_img.paste(
        paste_img.resize((150, 150), resample=Image.BICUBIC),
        (int(base_img.size[0] / 2 - 75), y_pos)
    )

    return base_img


def add_centered_text(
    base_img,
    text,
    font_path,
    font_size,
    font_color,
    x_pos=None,
    y_pos=None
):
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(base_img)

    # print(text)
    # wrap_list = text.split('\\n')
    # print(wrap_list, len(wrap_list[0]))
    # if len(wrap_list) > 1:
    #     y_pos -= 35

    if '\\n' in text:
        wrap_list = text.split('\\n')
    else:
        wrap_list = textwrap.wrap(text, 30)
    # print(wrap_list, len(wrap_list[0]))
    if len(wrap_list) > 1:
        y_pos -= 35
    for line in wrap_list:
        x_pos = (base_img.size[0] - draw.textsize(line, font=font)[0]) / 2
        draw.text(
            (x_pos, y_pos),
            line,
            font_color,
            font=font,
        )
        y_pos += 70

    return base_img


def add_author_text(
    base_img,
    text,
    font_path,
    font_size,
    font_color,
    x_pos=None,
    y_pos=None
):
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(base_img)

    if x_pos is None:
        x_pos = (base_img.size[0] - draw.textsize(text, font=font)[0]) / 2

    draw.text((x_pos, y_pos), text, font_color, font=font)

    return base_img


# date のフォーマットは yyyymmdd である。
def create_ogp_image(date, text):
    if not date or not text:
        raise 'Invalid Inputs'
    print('save_filepath')

    ogp_base_img_path = './images/template.png'
    ogp_icon_img_path = './images/kiwata.png'
    font_black_path = './font/NotoSansJP-Medium.otf'
    font_medium_path = './font/NotoSansJP-Medium.otf'

    icon_x_pos, icon_y_pos = 100, 100
    icon_size = 173
    base_img = Image.open(ogp_base_img_path).copy()
    icon_img = Image.open(ogp_icon_img_path).copy()
    icon_img_croped = icon_img.crop(
        (
            icon_x_pos,
            icon_y_pos,
            icon_x_pos + icon_size,
            icon_y_pos + icon_size
        )
    )

    display_date = f'{date[:4]}/{date[4:6]}/{date[6:]}'
    text_y_pos = 300

    base_img = paste_icon_image(base_img, icon_img_croped)
    base_img = add_centered_text(
        base_img,
        text,
        font_black_path,
        48,  # フォントサイズ
        (64, 64, 64),  # フォントカラー
        None,
        text_y_pos,  # y 座標
    )
    base_img = add_author_text(
        base_img,
        display_date,
        font_medium_path,
        32,  # フォントサイズ
        (120, 120, 120),  # フォントカラー
        100,
        435,  # y 座標
    )
    base_img = add_author_text(
        base_img,
        'Created by haKiwata',
        font_medium_path,
        32,  # フォントサイズ
        (120, 120, 120),  # フォントカラー
        600,
        435,  # y 座標
    )

    # base_img.show()
    save_filepath = '../../static/img/images/'
    base_img.save(f'{save_filepath}{date}.png')


BASE_POST_PATH = '../../content/post'


def is_file(target):
    file_data = glob.glob(f'{BASE_POST_PATH}/**', recursive=True)
    for p in file_data:
        if not os.path.isfile(p):
            continue
        if p.split('/')[-1].split('.')[0] == target:
            return p
    else:
        return None


def is_dir(target):
    dir_data = glob.glob(f'{BASE_POST_PATH}/**/')
    for p in dir_data:
        if p.split('/')[-2] == target:
            return p
    else:
        return None


def get_file_path(target):
    file_path = is_file(target)
    dir_path = is_dir(target)
    if file_path is not None:
        return file_path
    elif dir_path is not None:
        return dir_path + 'index.md'
    else:
        return None


def get_file_meta_data(file_path):
    is_started = False
    meta_data = []
    with open(file_path) as f:
        for line in f:
            if line == '---\n':
                if is_started:
                    return meta_data
                is_started = True
            else:
                meta_data.append(line)
    return meta_data


def filter_meta_data(meta_data, key):
    for m_data in meta_data:
        arranged_m_data = m_data.replace('\n', '').split(': ')
        if arranged_m_data[0] == key:
            return arranged_m_data[1]
    else:
        return None


# 既存のエントリ用の OGP を作成するための関数
def update_ogp_image():
    targets = [
        '20210512',
        '20210518',
        '20210529',
        '20210610',
        '20210611',
        '20210613',
        '20210615',
        '20210618',
        '20210622',
        '20210624',
        '20210628',
        '20210830',
        '20210831',
        '20210901',
        '20210911',
        '20211018',
    ]
    for target in targets:
        file_path = get_file_path(target)
        if file_path is None:
            raise 'Invalid Input'

        meta_data = get_file_meta_data(file_path)
        if len(meta_data) == 0:
            raise 'Invalid Input'
        # yyyymmdd のフォーマットで来るように仕様を変更する
        meta_date = target
        meta_title = filter_meta_data(meta_data, 'title').replace("\"", "")
        print(meta_date, meta_title)
        # # 以下の 2 つのデータを取得する必要がある
        # date = '2021-04-30T03:03:17+09:00'
        # # 40 文字までは表示することが可能である。
        # text = "振り返り"
        # text = "Hugo で Markdown が上手く Parse されない原因を調査してみた"
        # text = "自作 OS のリポジトリの README.md を自動更新する"
        create_ogp_image(meta_date, meta_title)


def get_data():
    url = 'https://api.github.com/repos/dilmnqvovpnmlib/hakiwata/commits/main'
    # url = "https://dog.ceo/api/breeds/image/notfound" # 404 を返す API
    fixed_files = []

    try:
        res = requests.get(url)
        res.raise_for_status()
        res_json = res.json()
        access_key = 'files'
        if access_key not in res_json:
            return fixed_files
        files = res_json[access_key]
        if len(files) == 0:
            return fixed_files
        for file in files:
            access_key = 'filename'
            if access_key not in file:
                continue
            filename = file[access_key]
            search_path = 'content/post/'
            if filename.startswith(search_path):
                fixed_files.append(filename)
        return fixed_files
    except RequestException as e:
        logger.exception("request failed. error=(%s)", e.response.text)



def is_valid_date_format(value):
    return True if re.fullmatch('[0-9]{8}', value) else False


# ファイルパスとして存在し得るパターン
# ../../content/post/20210430.md
# ../../content/post/20210624/index.md
# ../../content/post/_index.md
# ../../content/post/goisforlovers.md
# ../../content/post/20210624/01_hakiwata.jp
# ../../content/post/20210830/media/.gitkeep
# ../../content/post/20210830/media/osbook_day01.png
def get_date(filepath):
    splited_filepath = filepath.split('/')
    date = splited_filepath[-1].split('.')[0]
    if splited_filepath[-1] == 'index.md':
        return splited_filepath[-2]
    elif is_valid_date_format(date):
        return date
    else:
        return ''


def main():
    fixed_files = get_data() # GitHub の API 経由で変更されたファイル名を取得する。
    if len(fixed_files) == 0:
        return

    # 複数エントリを同時に push した時にも対応できるが、果たして必要か？
    for fixed_file in fixed_files:
        filepath = f'../../{fixed_file}'
        meta_date = get_date(filepath)  # 返り値は yyyymmdd のフォーマットである。
        if not meta_date:
            continue

        meta_data = get_file_meta_data(filepath)
        if len(meta_data) == 0:
            continue
        meta_title = filter_meta_data(meta_data, 'title').replace("\"", "")

        create_ogp_image(meta_date, meta_title)


if __name__ == '__main__':
    # update_ogp_image()
    main()
