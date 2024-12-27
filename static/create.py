from PIL import Image, ImageDraw, ImageFont

# Canvas size
img_size = (256, 256)
img = Image.new("RGBA", img_size, color=(255, 255, 255, 0))  # transparent background

draw = ImageDraw.Draw(img)

# 1) Draw a circle to represent a light bulb.
circle_bounds = (60, 60, 196, 196)
draw.ellipse(circle_bounds, fill=(255, 204, 0, 255))  # bright yellow

# 2) Draw a small black rectangle as a stylized "Apple TV" box at the bottom.
tv_bounds = (85, 160, 171, 200)
draw.rectangle(tv_bounds, fill=(0, 0, 0, 255))

# 3) Add "TV" text on top of the black box.
try:
    font = ImageFont.truetype("arial.ttf", size=24)
except IOError:
    font = ImageFont.load_default()

text = "TV"

# Use a try/except to handle different Pillow versions:
try:
    # Old method (Pillow <10)
    text_width, text_height = draw.textsize(text, font=font)
except AttributeError:
    # Newer method (Pillow >=10)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

text_x = tv_bounds[0] + (tv_bounds[2] - tv_bounds[0] - text_width) / 2
text_y = tv_bounds[1] + (tv_bounds[3] - tv_bounds[1] - text_height) / 2
draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

# 4) Save as an ICO with multiple resolutions.
img.save("favicon.ico", format="ICO", sizes=[
    (16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)
])
