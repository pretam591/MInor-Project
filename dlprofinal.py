from PIL import Image, ImageDraw

image = Image.open("/home/oem/Downloads/cancer.jpg")
print(image.size)
skImg = image.resize((512, 512))
print(skImg.size)
skImg.show()
sk = ImageDraw.Draw(skImg)
s = (100,100)
e = (250,250)
sk.rectangle([s,e],outline="white")
skImg.show()