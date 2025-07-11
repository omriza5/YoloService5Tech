import io
from PIL import Image, ImageDraw

def create_dummy_image(color, shape=None):
    """
    Creates a dummy image with an optional colored shape for testing purposes.

    Args:
        color (str or tuple): The color to use for the shape (e.g., 'red', (255, 0, 0)).
        shape (str, optional): The shape to draw on the image. Supported values are:
            - 'umbrella': Draws a filled ellipse (umbrella-like shape) in the center.
            - 'donut': Draws four outlined ellipses (donut-like shapes) in a row.
            If None or any other value, returns a blank white image.

    Returns:
        io.BytesIO: A bytes buffer containing the JPEG-encoded image.
    """
    test_image = Image.new('RGB', (100, 100), 'white')
    draw = ImageDraw.Draw(test_image)
    if shape == 'umbrella':
        draw.ellipse((25, 25, 75, 75), fill=color, outline='black')
    elif shape == 'donut':
        radius = 18
        spacing = 8
        y = 50 - radius
        for i in range(4):
            x = 8 + i * (radius * 2 + spacing)
            draw.ellipse((x, y, x + radius * 2, y + radius * 2), outline=color, width=4)
    
    # else: just a blank white image
    image_bytes = io.BytesIO()
    test_image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    return image_bytes
