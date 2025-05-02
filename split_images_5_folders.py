#!/usr/bin/env python3
"""
Script para dividir datasets en partes más pequeñas, para preparar datasets antes de fusionarlos con merge.


Script to split the city_images folder into 5 parts, with 1000 images each.
"""

import os
import shutil
import random
from pathlib import Path

def consolidate_images(original_dir, secondary_dir):
    """
    Move all images from secondary_dir back to original_dir
    """
    if not os.path.exists(secondary_dir):
        print(f"Secondary directory {secondary_dir} doesn't exist. No need to consolidate.")
        return
    
    # Get list of all image files in the secondary directory
    image_files = [f for f in os.listdir(secondary_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Move the images back to the original directory
    for image in image_files:
        source_path = os.path.join(secondary_dir, image)
        target_path = os.path.join(original_dir, image)
        shutil.move(source_path, target_path)
    
    print(f"Moved {len(image_files)} images from {secondary_dir} back to {original_dir}")
    
    # Remove the empty secondary directory
    if len(os.listdir(secondary_dir)) == 0:
        os.rmdir(secondary_dir)
        print(f"Removed empty directory: {secondary_dir}")

def split_images_into_folders(source_dir, base_target_dir, num_folders, images_per_folder):
    """
    Split images from source_dir into multiple target folders
    
    Args:
        source_dir: Source directory containing the images
        base_target_dir: Base name for target directories
        num_folders: Number of folders to create
        images_per_folder: Number of images per folder
    """
    # Get list of all image files
    image_files = [f for f in os.listdir(source_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(image_files)
    
    print(f"Found {total_images} images in {source_dir}")
    
    required_images = num_folders * images_per_folder
    if required_images > total_images:
        print(f"Error: Cannot split into {num_folders} folders with {images_per_folder} images each. "
              f"Total required: {required_images}, but only have {total_images} images.")
        return
    
    # Shuffle the images
    random.shuffle(image_files)
    
    # Create folders and move images
    for folder_idx in range(num_folders):
        folder_name = f"{base_target_dir}_{folder_idx + 1}"
        folder_path = os.path.join(os.path.dirname(source_dir), folder_name)
        
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created directory: {folder_path}")
        
        # Select images for this folder
        start_idx = folder_idx * images_per_folder
        end_idx = start_idx + images_per_folder
        folder_images = image_files[start_idx:end_idx]
        
        # Move images to the folder
        for image in folder_images:
            source_path = os.path.join(source_dir, image)
            target_path = os.path.join(folder_path, image)
            shutil.move(source_path, target_path)
        
        print(f"Moved {len(folder_images)} images to {folder_path}")

if __name__ == "__main__":
    # Paths
    current_dir = Path(__file__).parent
    original_dir = os.path.join(current_dir, "city_images")
    secondary_dir = os.path.join(current_dir, "city_images_part2")
    
    # First, consolidate all images back to the original directory
    consolidate_images(original_dir, secondary_dir)
    
    # Then split into 5 folders with 1000 images each
    base_target_dir = "city_images_part"
    split_images_into_folders(original_dir, base_target_dir, 5, 1000)
    
    print("Image splitting complete!")
