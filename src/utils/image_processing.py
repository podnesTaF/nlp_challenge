from PIL import Image

def process_and_store_image(file):
    """
    Processes an uploaded image file and extracts metadata.

    Args:
        file: The uploaded image file object.

    Returns:
        str: A summary of the image metadata.
    """
    try:
        # Open the image
        image = Image.open(file)

        # Extract metadata
        width, height = image.size
        mode = image.mode  # e.g., "RGB"
        format = image.format  # e.g., "JPEG" or "PNG"

        # Save the image (optional)
        image.save(f"data/images/{file.name}")

        # Return metadata
        return f"Image {file.name} processed: {width}x{height}, {mode}, {format}"
    except Exception as e:
        return f"Error processing image {file.name}: {str(e)}"