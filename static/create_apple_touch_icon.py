from PIL import Image, ImageDraw, ImageFont

# Apple recommends a 180×180 PNG for newer iPhones (Retina screens).
img_size = (180, 180)
img = Image.new("RGBA", img_size, color=(255, 255, 255, 0))  # transparent background

draw = ImageDraw.Draw(img)

# 1) Draw a circle (light bulb style).
circle_bounds = (30, 30, 150, 150)
draw.ellipse(circle_bounds, fill=(255, 204, 0, 255))  # bright yellow

# 2) Draw a small black rectangle (Apple TV box).
tv_bounds = (50, 110, 130, 140)
draw.rectangle(tv_bounds, fill=(0, 0, 0, 255))

# 3) Add "TV" text on top of the black box.
try:
    font = ImageFont.truetype("arial.ttf", size=24)
except IOError:
    # fallback to default PIL font if arial.ttf isn't found
    font = ImageFont.load_default()

text = "TV"
# Pillow 10+ uses textbbox; older uses textsize
try:
    text_width, text_height = draw.textsize(text, font=font)
except AttributeError:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

text_x = tv_bounds[0] + (tv_bounds[2] - tv_bounds[0] - text_width) / 2
text_y = tv_bounds[1] + (tv_bounds[3] - tv_bounds[1] - text_height) / 2
draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

# 4) Save as a PNG.
img.save("apple-touch-icon.png", format="PNG")
