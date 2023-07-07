from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
# # 1.創建空白圖片
# img = Image.new(mode="RGB",size=(120, 30),color=(255,255,255))
#
# # 3.創建畫筆，可以在空白圖片上畫任意內容
# draw = ImageDraw.Draw(img,mode='RGB')
# # 5.導入字體文件
# font = ImageFont.truetype(font='Monaco.ttf',size=28)
# # 4.寫入文本
# draw.text((0,0),'python','black',font=font)
#
#
# # 2.保存到本地
# with open('color.png', 'wb')as f:
#     img.save(f, format='png')


def check_code(width=120, height=30, char_length=5, font_file='dept_app/utils/Monaco.ttf', font_size=28):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    def rndChar():
        """
        生成随机字母
        :return:
        """
        return chr(random.randint(65, 90))

    def rndColor():
        """
        生成随机颜色
        :return:
        """
        return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))

    # 写隨機生成的文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h = random.randint(0, 4)
        draw.text((i * width / char_length, h), char, font=font, fill=rndColor())

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())

    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line((x1, y1, x2, y2), fill=rndColor())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # 返回兩個數職：img->圖片對象、''.join(code)->寫在圖片上面的隨機文字(把list轉成字串)
    return img, ''.join(code)


if __name__ == '__main__':
    img, code_str = check_code()
    print(code_str)

    with open('code.png', 'wb') as f:
        img.save(f, format='png')
