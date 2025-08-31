from PIL import Image

# Input image (PNG/JPG)
img_path = r"D:\path\to\logo.png"

# Output icon
ico_path = r"D:\path\to\logo.ico"

# Open and save as .ico
img = Image.open(img_path)
img.save(ico_path, format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])

print(f"ICO file created at {ico_path}")
