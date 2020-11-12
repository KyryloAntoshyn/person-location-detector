import os
import sys
import shutil
import requests
import math
from pycocotools.coco import COCO

DATASET_DIRECTORY_NAME = "dataset"
NUMBER_OF_DECIMALS_TO_LEAVE_IN_ANNOTATIONS = 7


def initialize_coco():
    """
    Initializes COCO object.

    :return: whether COCO object has been initialized and its reference
    """
    annotations_file_path = input("Enter path to the annotations file: ")
    if not os.path.exists(annotations_file_path):
        return False, None

    return True, COCO(annotations_file_path)


def get_category_id_and_images(coco):
    """
    Gets category ID and images for the particular category.

    :param coco: COCO object
    :return: whether category exists, category ID and images for this category
    """
    category_names = [category["name"] for category in coco.loadCats(coco.getCatIds())]
    print("COCO categories:", " ".join(category_names))

    category_name_to_download = input("Enter category name to download: ")
    if category_name_to_download not in category_names:
        return False, None, None

    category_id = coco.getCatIds(catNms=category_name_to_download)[0]

    return True, category_id, coco.loadImgs(coco.getImgIds(catIds=category_id))


def filter_images_to_download(images):
    """
    Filters images to download.

    :param images: images
    :return: whether images to download have been filtered and list of these images
    """
    images_total_number = len(images)
    print("Total number of images:", images_total_number)

    try:
        number_of_images_to_download = int(input("Enter number of images to download: "))
        if number_of_images_to_download <= 0 or number_of_images_to_download > images_total_number:
            return False, None

        return True, images[:number_of_images_to_download]
    except ValueError:
        return False, None


def download_and_save_images(images_to_download):
    """
    Downloads images to the dataset directory.
    
    :param images_to_download: images to download
    """
    if os.path.exists(DATASET_DIRECTORY_NAME):
        shutil.rmtree(DATASET_DIRECTORY_NAME)
    os.makedirs(DATASET_DIRECTORY_NAME)

    for image_to_download in images_to_download:
        print("Downloading and writing:", image_to_download["file_name"])
        with open(os.path.join(DATASET_DIRECTORY_NAME, image_to_download["file_name"]), "wb") as image_file:
            image_file.write(requests.get(image_to_download["coco_url"]).content)


def convert_and_write_annotations(coco, downloaded_images, category_id):
    """
    Converts and writes annotations.

    :param coco: COCO object
    :param downloaded_images: downloaded images
    :param category_id: category ID
    """

    def truncate(number, number_of_decimals=0):
        """
        Truncates number by specific number of decimals.
        :param number: number
        :param number_of_decimals: number of decimals
        :return: truncated number
        """
        factor = 10.0 ** number_of_decimals
        return math.trunc(number * factor) / factor

    for downloaded_image in downloaded_images:
        annotation_file_name = downloaded_image["file_name"].replace(".jpg", ".txt")
        print("Converting and writing:", annotation_file_name)

        with open(os.path.join(DATASET_DIRECTORY_NAME, annotation_file_name), "a") as annotation_file:
            annotations = coco.loadAnns(coco.getAnnIds(imgIds=downloaded_image["id"], catIds=category_id, iscrowd=None))
            image_width = downloaded_image["width"]
            image_height = downloaded_image["height"]

            for annotation in annotations:
                x_min = annotation["bbox"][0]
                y_min = annotation["bbox"][1]
                x_max = annotation["bbox"][0] + annotation["bbox"][2]
                y_max = annotation["bbox"][1] + annotation["bbox"][3]

                x_center = (x_min + x_max) / 2 / image_width
                y_center = (y_min + y_max) / 2 / image_height
                width = (x_max - x_min) / image_width
                height = (y_max - y_min) / image_height

                annotation_file.write(
                    "0 " + str(truncate(x_center, NUMBER_OF_DECIMALS_TO_LEAVE_IN_ANNOTATIONS)) + " " + str(
                        truncate(y_center, NUMBER_OF_DECIMALS_TO_LEAVE_IN_ANNOTATIONS)) + " " + str(
                        truncate(width, NUMBER_OF_DECIMALS_TO_LEAVE_IN_ANNOTATIONS)) + " " + str(
                        truncate(height, NUMBER_OF_DECIMALS_TO_LEAVE_IN_ANNOTATIONS)) + "\n")


def main():
    """
    Script entry point.
    """
    # Initialize COCO object
    is_success, coco = initialize_coco()
    if not is_success:
        print("Annotations file doesn't exist!")
        sys.exit(1)
    print("COCO has been initialized!")

    # Get category ID and images for the particular category name
    is_success, category_id, images = get_category_id_and_images(coco)
    if not is_success:
        print("Such category doesn't exist!")
        sys.exit(1)

    # Filter images to download
    is_success, images_to_download = filter_images_to_download(images)
    if not is_success:
        print("Unable to filter images to download!")
        sys.exit(1)
    print("Images to download have been filtered!")

    # Download and save images
    download_and_save_images(images_to_download)
    print("Images have been downloaded and saved!")

    # Convert and write annotations
    convert_and_write_annotations(coco, images_to_download, category_id)
    print("Annotations have been converted and written!")


if __name__ == "__main__":
    main()
