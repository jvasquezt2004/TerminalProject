#!/usr/bin/env python3
"""
Script to split the city_images folder into two parts, moving half of the images to a new folder.
"""

import os
import shutil
import random
from pathlib import Path

def split_images(source_dir, target_dir, num_images_to_move):
    """
    Split images from source_dir to target_dir
    
    Args:
        source_dir: Source directory containing the images
        target_dir: Target directory to move images to
        num_images_to_move: Number of images to move
    """
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
    
    # Get list of all image files
    image_files = [f for f in os.listdir(source_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(image_files)
    
    print(f"Found {total_images} images in {source_dir}")
    
    if num_images_to_move > total_images:
        print(f"Error: Cannot move {num_images_to_move} images as there are only {total_images} images.")
        return
    
    # Randomly select images to move
    images_to_move = random.sample(image_files, num_images_to_move)
    
    # Move the selected images
    for image in images_to_move:
        source_path = os.path.join(source_dir, image)
        target_path = os.path.join(target_dir, image)
        shutil.move(source_path, target_path)
        
    print(f"Moved {num_images_to_move} images from {source_dir} to {target_dir}")

if __name__ == "__main__":
    # Paths
    current_dir = Path(__file__).parent
    source_dir = os.path.join(current_dir, "city_images")
    target_dir = os.path.join(current_dir, "city_images_part2")
    
    # Move half of the images (2500)
    split_images(source_dir, target_dir, 2500)
