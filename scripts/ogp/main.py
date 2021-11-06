import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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

    wrap_list = textwrap.wrap(text, 30)
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


if __name__ == '__main__':
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

    date = '2021-04-30T03:03:17+09:00'
    splited_date = date.split('T')[0]
    display_date = splited_date.replace('-', '/')
    output_filename = splited_date.replace('-', '')
    text = "振り返り"
    # 40 文字までは表示することが可能である。
    text = "Hugo で Markdown が上手く Parse されない原因を調査してみた"
    text = "自作 OS のリポジトリの README.md を自動更新する"
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
    base_img.save(f'./images/{output_filename}.png')
