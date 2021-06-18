from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from math import atan, pi
import sys
import os

style_select = 1


def create_watermark(content, width, height):
    diagonal = {
        'x': 1 / 2,
        'y': 1 / 2,
        'angle': atan(height / width) / pi * 180,
        'fontsize': 60
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
    c.rotate(style['angle'])
    # c.rotate(90)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.2)
    # 画几个文本，注意坐标系旋转的影响
    c.drawCentredString(0.1 * inch, 0.1 * inch, content)
    # c.save()
    return c.getpdfdata()


def add_watermark(content, origin, target):
    # Get the watermark file you just created
    # Get our files ready
    output_file = PdfFileWriter()
    input_file = PdfFileReader(open(origin, "rb"), strict=False)

    if input_file.getIsEncrypted():
        try:
            input_file.decrypt('')
        except:
            input('the PDF is encrypted.')
            return

    # Get the outlines
    w = h = 0
    watermark = None
    # 文档中的所有页数
    page_count = input_file.getNumPages()
    # Go through all the input file pages to add a watermark to them
    for page_number in range(page_count):
        print("Watermarking page {} of {}".format(page_number + 1, page_count))
        # merge the watermark with the page
        input_page = input_file.getPage(page_number)
        # get page size   得到的单位是 1 pt = 1/72 inch 如果页面大于5英寸
        if abs(w - input_page.mediaBox[2] / 72) > 5:
            w = input_page.mediaBox[2] / 72
            h = input_page.mediaBox[3] / 72
            watermark = PdfFileReader(BytesIO(create_watermark(content, int(w), int(h))))  # 直接用IO流写回PdfFileReader中 妙

        input_page.mergePage(watermark.getPage(0))
        # add page from input file to output document
        output_file.addPage(input_page)

    # Remove links and annotations
    # output_file.removeLinks()

    # Copy bookmarks from input file to output file
    # def recursion(parent, outlines):
    #     sub_parent = parent
    #     for destination in outlines:
    #         if hasattr(destination, 'title'):
    #             sub_parent = output_file.addBookmark(destination.title,
    #                                                  input_file.getDestinationPageNumber(
    #                                                      destination),
    #                                                  parent)
    #         else:
    #             recursion(sub_parent, destination)

    # recursion(None, input_file.outlines)

    # 最终舒服带水印的pdf文件
    with open(target, "wb") as outputStream:
        output_file.write(outputStream)


def main():
    add_watermark("陈某某(joan.test@hisight.cn)", "./pdf_files/SMC_Userguide_3.pdf", "t1.pdf")

    # if len(sys.argv[1:]):
    #     if os.path.splitext(sys.argv[1])[1].lower() == '.pdf':
    #         pdf = sys.argv[1]
    #         content = 'Release to %s Under NDA' % input('Rlease to who: ')
    #         add_watermark(content, pdf, os.path.dirname(pdf) + '/MCHP_' + os.path.basename(pdf))


if __name__ == '__main__':
    main()
