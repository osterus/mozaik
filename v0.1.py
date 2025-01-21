import os
from PIL import Image
import numpy as np
from tqdm import tqdm
#короче берет и заменяет зоны указаныз рахмеров на изображения позожего цвето если чет не понятно проси чертовы чертежи (файл логики работы) я сам не помню как это работает
def calculate_average_color(image, offset_fraction=1/3):
    """
    Calculate the average color of the central region of an image.

    :param image: PIL.Image object
    :param offset_fraction: Fraction of width and height to offset from edges
    :return: (R, G, B) tuple
    """
    width, height = image.size
    x_offset = int(width * offset_fraction)
    y_offset = int(height * offset_fraction)
    
    cropped_image = image.crop((x_offset, y_offset, width - x_offset, height - y_offset))
    np_image = np.array(cropped_image)
    
    # Compute mean color
    average_color = np_image.mean(axis=(0, 1))[:3]  # Ignore alpha channel if present
    return tuple(map(int, average_color))

def generate_color_map(source_folder):
    color_map = []
    files = os.listdir(source_folder)
    
    for file_name in tqdm(files, desc="Processing images for color map"):
        file_path = os.path.join(source_folder, file_name)
        if not os.path.isfile(file_path):  # Пропускаем директории
            continue
        try:
            with Image.open(file_path) as img:
                avg_color = calculate_average_color(img)
                color_map.append((avg_color, file_path))
        except Exception as e:
            print(f"проверь ззараза:Skipping {file_path}: {e}")
    return color_map

def find_closest_match(color, color_map):
    """
    Find the image from the color map whose average color is closest to the given color.

    :param color: (R, G, B) tuple of the target color
    :param color_map: List of (average_color, file_path) tuples
    :return: Path to the best match image
    """
    def color_distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))

    closest_match = min(color_map, key=lambda entry: color_distance(color, entry[0]))
    return closest_match[1]

def create_mosaic(source_image_path, color_map, tile_size, output_path):
    """
    Create a mosaic based on a source image and a color map.

    :param source_image_path: Path to the source image
    :param color_map: List of (average_color, file_path) tuples
    :param tile_size: Size of each mosaic tile (width, height)
    :param output_path: Path to save the output image
    """
    with Image.open(source_image_path) as source_img:
        source_img = source_img.convert("RGB")
        width, height = source_img.size

        # Resize source image to make it evenly divisible by the tile size
        mosaic_width = (width // tile_size[0]) * tile_size[0]
        mosaic_height = (height // tile_size[1]) * tile_size[1]
        source_img = source_img.resize((mosaic_width, mosaic_height))

        # Prepare the output image
        output_img = Image.new("RGB", (mosaic_width, mosaic_height))

        for y in tqdm(range(0, mosaic_height, tile_size[1]), desc="Building mosaic"):
            for x in range(0, mosaic_width, tile_size[0]):
                tile = source_img.crop((x, y, x + tile_size[0], y + tile_size[1]))
                avg_color = calculate_average_color(tile, offset_fraction=0)
                match_path = find_closest_match(avg_color, color_map)
                with Image.open(match_path) as match_img:
                    match_img = match_img.resize(tile.size)
                    output_img.paste(match_img, (x, y))

        output_img.save(output_path)

if __name__ == "__main__":
    source_folder = input("путь для папки с изображениями : ")
    source_image_path = input("путь до изначального файла: ")
    output_path = input("куда созранять мозайку (файл): ")
    tile_width = int(input("Enter the width of each tile: "))
    tile_height = int(input("Enter the height of each tile: "))

    print("создание карты цветов...")
    color_map = generate_color_map(source_folder)

    print("создание калаша...")
    create_mosaic(source_image_path, color_map, (tile_width, tile_height), output_path)

    print(f"мозайка созранена в{output_path}")
