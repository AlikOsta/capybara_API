
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def process_image(image_field, instans_id=None, max_size=(800, 800), format="WEBP", quality=65):
    """
    Process an image by resizing it and converting to WEBP format.
    
    Args:
        image_field: The image field to process
        instance_id: ID of the model instance (optional)
        max_size: Maximum dimensions for the image
        format: Output format (default: WEBP)
        quality: Image quality (0-100)
        
    Returns:
        ContentFile: Processed image as ContentFile
    """

    if not image_field:
        return None
    
    img = Image.open(image_field)

    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size)
    
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    output = BytesIO()
    img.save(output, format=format, quality=quality, optimize=True)
    output.seek(0)
    
    base_name = image_field.name.rsplit(".", 1)[0]
    id_prefix = f"{instans_id}_" if instans_id else ""
    new_name = f"{id_prefix}{base_name}.{format.lower()}"

    return ContentFile(output.read(), name=new_name)

    