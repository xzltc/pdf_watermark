from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.colors import yellow, red, black, white, blue, darkred
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from math import atan, pi, cos
import sys
import os

style_select = 1


def create_watermark(content, width, height):
    diagonal = {
        'x': 1 / 2,
        'y': 1 / 2,
        'angle': atan(height / width) / pi * 180,
        'fontsize': 40
    }
    horizontal = {'x': 1 / 2,
                  'y': 0,
                  'angle': 0,
                  'fontsize': 30
                  }
    style = diagonal if style_select else horizontal

    # 默认大小为21cm*29.7cm
    c = canvas.Canvas("mark.pdf", pagesize=(width * inch, height * inch))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(style['x'] * width * inch, style['y'] * height * inch)
    # 设置字体
    pdfmetrics.registerFont(TTFont('msyh', 'msyhl.ttc'))
    c.setFont("msyh", style['fontsize'])

    # 旋转45度，坐标系被旋转
    # c.rotate(style['angle'])
    c.rotate(45)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.2)
    # 画几个文本，注意坐标系旋转的影响
    # c.drawCentredString(0.1 * inch, 0.1 * inch, content)
    # c.save()

    c.line(- 3.40 * inch, + 3.65 * inch, + 3.40 * inch, + 3.65 * inch)
    c.line(- 3.40 * inch, - 4.90 * inch, + 3.40 * inch, - 4.90 * inch)
    c.line(- 3.323 * inch, -0.625 * inch, + 3.323 * inch, -0.625 * inch)
    c.line(- 3.40 * inch, + 3.65 * inch, - 3.40 * inch, - 4.90 * inch)
    c.line(+ 3.40 * inch, + 3.65 * inch, + 3.40 * inch, - 4.90 * inch)

    c.circle(0, 0, 0.2 * cm, stroke=1, fill=1)
    c.circle(0, -0.625 * inch, 0.2 * cm, stroke=1, fill=1)

    center_x = 0
    center_y = -0.625 * inch
    size = 30
    for item in content:
        c.setFont('msyh', size)
        c.drawCentredString(center_x, center_y, item)
        center_y = center_y - size * 1.2
        print(c.stringWidth(item, 'msyh', size))

    return c.getpdfdata()


def create_watermark2(content, width, height, show):
    diagonal = {
        'x': 1 / 2,
        'y': 1 / 2,
        'angle': atan(height / width) / pi * 180,
        'fontsize': 40
    }

    style = diagonal

    # 默认大小为21cm*29.7cm
    c = canvas.Canvas("mark.pdf", pagesize=(width * inch, height * inch))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(style['x'] * width * inch, style['y'] * height * inch - 0.625 * inch)
    # 设置字体
    pdfmetrics.registerFont(TTFont('msyh', 'msyhl.ttc'))
    c.setFont("msyh", style['fontsize'])

    # 旋转45度，坐标系被旋转
    angle = 50
    c.rotate(angle)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.2)
    # c.save()
    if show:
        c.setStrokeColor(red)  # 设置画笔的颜色
        c.line(- 3.40 * inch, + 4.275 * inch, + 3.40 * inch, + 4.275 * inch)
        c.line(- 3.40 * inch, - 4.275 * inch, + 3.40 * inch, - 4.275 * inch)
        # c.line(- 3.35 * inch, 0, + 3.35 * inch, 0)
        c.line(- 3.40 * inch, + 4.275 * inch, - 3.40 * inch, - 4.275 * inch)
        c.line(+ 3.40 * inch, + 4.275 * inch, + 3.40 * inch, - 4.275 * inch)

    size = get_font_size(c, content, angle, "msyh")
    print(size)

    center_x = 0
    if len(content) == 1:
        center_y = 0
    # elif len(content) == 2 and len(content[0]) > len(content[1]):
    #     center_y = 0
    elif len(content) == 2 and c.stringWidth(content[0], 'msyh', size) > c.stringWidth(content[1], 'msyh', size):
        center_y = 0
    elif len(content) == 2 and text_length(content[0]) == text_length(content[1]):
        center_y = 0 + size / 5
        if size > 55:
            size -= 2
    else:
        center_y = 0 + size * len(content) / 3

    for item in content:
        c.setFont('msyh', size)
        c.drawCentredString(center_x, center_y, item)
        line_witdth = c.stringWidth(item, 'msyh', size)
        print(line_witdth)
        c.setStrokeColor(darkred)
        c.line(center_x - (line_witdth / 2), center_y, + center_x + (line_witdth / 2), center_y)
        center_y = center_y - size * 1

    return c.getpdfdata()


def add_watermark(content, origin, target):
    # Get the watermark file you just created
    # Get our files ready
    output_file = PdfFileWriter()
    input_file = PdfFileReader(open(origin, "rb"), strict=False)

    # Get the outlines
    w = h = 0
    watermark = None
    # 文档中的所有页数
    page_count = input_file.getNumPages()
    # Go through all the input file pages to add a watermark to them
    for page_number in range(page_count):
        # merge the watermark with the page
        input_page = input_file.getPage(page_number)
        # get page size   得到的单位是 1 pt = 1/72 inch 如果页面大于5英寸

        w = input_page.mediaBox[2] / 72
        h = input_page.mediaBox[3] / 72
        # 踩了个大坑，这里取整了，生成的类型是demical类型，转float后和计算
        watermark = PdfFileReader(
            BytesIO(create_watermark2(content, float(w), float(h), False)))  # 直接用IO流写回PdfFileReader中 妙
        bounding_box = PdfFileReader(BytesIO(draw_watermark_box(float(w), float(h))))

        input_page.mergePage(watermark.getPage(0))
        input_page.mergePage(bounding_box.getPage(0))
        # add page from input file to output document
        output_file.addPage(input_page)

    # 最终舒服带水印的pdf文件
    with open(target, "wb") as outputStream:
        output_file.write(outputStream)


def get_font_size(board, content, angle, font_style):
    maxWidth = (6 * inch / 2) / cos(angle * pi / 180)
    font_size = 80
    for text in content:
        temp_size = 1
        while (board.stringWidth(text, font_style, temp_size) / 2) <= maxWidth:
            temp_size += 1
        font_size = temp_size if font_size > temp_size else font_size
    return font_size


def draw_watermark_box(w, h):
    # 默认大小为21cm*29.7cm
    c = canvas.Canvas("box.pdf", pagesize=(w * inch, h * inch))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(1 / 2 * w * inch, 1 / 2 * h * inch)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.5)
    # c.save()

    c.line(- 3.40 * inch, + 3.65 * inch, + 3.40 * inch, + 3.65 * inch)
    c.line(- 3.40 * inch, - 4.90 * inch, + 3.40 * inch, - 4.90 * inch)
    c.line(- 3.323 * inch, -0.625 * inch, + 3.323 * inch, -0.625 * inch)
    c.line(- 3.40 * inch, + 3.65 * inch, - 3.40 * inch, - 4.90 * inch)
    c.line(+ 3.40 * inch, + 3.65 * inch, + 3.40 * inch, - 4.90 * inch)

    c.circle(0, 0, 0.1 * cm, stroke=1, fill=1)
    c.circle(0, -0.625 * inch, 0.2 * cm, stroke=1, fill=1)

    return c.getpdfdata()


def text_length(text):
    return sum(1 for c in text if c != ' ')


def main():
    # texts = ["One WaterMark", "Two WaterMark"]
    # texts = ["One WaterMark", "Two WaterMark"]
    # texts = ["Technology"]
    # texts = ["Arion Technology"]
    # texts = ["中国atan公司", "antan@163.com"]
    # texts = ["Novel-Super TV", "aaa@163.com"]
    # texts = ["中华人民共和国", "某某某某某某某某某公司"]
    # texts = ["中国atan公司", "joan.test@hisight.cn"]
    # texts = ["Arion Technology Inc", "陈某某(joan.test@hisight.cn)"]
    # texts = ["仅供中华人民共和国北京联广视讯有限公司内部使用"]
    # texts = ["陈某某(joan.test@hisight.cn)",
    #          "Arion Technology Inc Company etc Longest Watermark Is On This In The First Line"]
    # texts = ["Arion Technology Inc Company etc Longest Watermark Is On This In The First Line",
    #          "陈某某(joan.test@hisight.cn)"]
    # texts = ["中华人民共和国", "Arion Technology Inc", "陈某某(joan.test@hisight.cn)再加一些文字看看回事什么效果"]
    # texts = ["仅供中华人民共和国北京联广视讯有限公司内部使用", "仅供北京联广视讯有限公司内部使用"]
    # texts = ["Novel-Super TV", "joan.test@hisight.cn"]
    # texts = ["One Line WaterMark In PDF", "Two Line WaterMark In PDF"]
    # texts = ["One Line In WaterMark One One One One One", "Two Line In a a a a WaterMark One One One One One"]
    # texts = ["One Two Line WaterMark aa", "Two Two Line WaterMark Two Two Line WaterMark"]
    # texts = ["资高电子科技(深圳)有限公司北京分公司", "abcdefgjijklm@abcdefg-xy.com"]
    texts = ["Modern Communication and Broadcast Systems Pvt Ltd", "abcdefgjijklm@abcdefg-xy.com"]
    texts = ["长虹keji", "abcdefgjijklm@abcdefg-xy.com"]
    texts = ["VTC", "abcdefgjijklm@abcdefg-xy.com"]
    add_watermark(texts, "./pdf_files/SMC_Userguide_3.pdf", "d4.pdf")
    # add_watermark("陈某某(joan.test@hisight.cn)", "./pdf_files/微农.pdf", "t3.pdf")


if __name__ == '__main__':
    main()
