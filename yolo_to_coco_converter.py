#!/usr/bin/env python3
import os
import cv2
import json
import yaml
import numpy as np
from pathlib import Path
import argparse
import imagesize

def get_img_shape(img_path):
    """
    Obtiene el ancho y alto de una imagen sin cargarla completamente en memoria.
    """
    try:
        width, height = imagesize.get(img_path)
        return width, height
    except:
        # Si falla, intentamos con OpenCV
        try:
            img = cv2.imread(img_path)
            height, width = img.shape[:2]
            return width, height
        except:
            print(f"ERROR: No se pudo obtener las dimensiones de {img_path}")
            return 0, 0

def create_category_dict(classes):
    """
    Crea el diccionario de categorías para el formato COCO.
    Elimina duplicados y asegura IDs únicos.
    """
    # Eliminar duplicados manteniendo el orden
    unique_classes = []
    for cls in classes:
        if cls not in unique_classes:
            unique_classes.append(cls)
    
    # Crear la lista de categorías con IDs comenzando en 1 (estándar COCO)
    categories = []
    for i, cls in enumerate(unique_classes, 1):
        categories.append({
            "id": i,
            "name": cls,
            "supercategory": "none"
        })
    
    # Crear un mapeo de nombres de clase a IDs de categoría
    class_to_id = {cls: i for i, cls in enumerate(unique_classes, 1)}
    
    return categories, class_to_id

def yolo_to_coco_format(data_dir, save_path, class_names, split='train'):
    """
    Convierte anotaciones YOLO a formato COCO JSON.
    
    Args:
        data_dir: Directorio con imágenes y anotaciones YOLO (.txt)
        save_path: Ruta donde guardar el archivo JSON resultante
        class_names: Lista de nombres de clases
        split: Sufijo para el archivo JSON (train o valid)
    """
    # Crear la estructura de diccionario COCO
    coco_format = {
        "images": [],
        "categories": [],
        "annotations": []
    }
    
    # Crear las categorías
    categories, class_to_id = create_category_dict(class_names)
    coco_format["categories"] = categories
    
    # Contadores
    image_id = 0
    annotation_id = 0
    
    # Listar todos los archivos de imagen
    image_files = [f for f in os.listdir(data_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"Procesando {len(image_files)} imágenes en {data_dir}...")
    
    # Procesar cada imagen
    for img_file in image_files:
        image_id += 1
        img_path = os.path.join(data_dir, img_file)
        
        # Obtener dimensiones de la imagen
        width, height = get_img_shape(img_path)
        
        if width == 0 or height == 0:
            print(f"Saltando {img_file} debido a problemas con las dimensiones")
            continue
        
        # Añadir información de la imagen
        coco_format["images"].append({
            "id": image_id,
            "file_name": img_file,
            "width": width,
            "height": height,
            "date_captured": "",
            "license": 1,
            "coco_url": "",
            "flickr_url": ""
        })
        
        # Buscar el archivo de anotación correspondiente
        txt_file = os.path.splitext(img_file)[0] + '.txt'
        txt_path = os.path.join(data_dir, txt_file)
        
        if not os.path.exists(txt_path):
            print(f"No se encontró archivo de anotación para {img_file}")
            continue
        
        # Leer las anotaciones YOLO
        with open(txt_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Formato YOLO: <class_id> <x_center> <y_center> <width> <height>
                    parts = line.split()
                    class_id = int(parts[0])
                    
                    # Verificar si el class_id está dentro del rango válido
                    if class_id >= len(class_names):
                        print(f"Saltando anotación con class_id={class_id} fuera de rango en {txt_file}")
                        continue
                    
                    # Convertir coordenadas YOLO (relativas) a COCO (absolutas)
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    box_width = float(parts[3])
                    box_height = float(parts[4])
                    
                    # YOLO da coordenadas normalizadas (0-1), convertir a píxeles
                    x_min = (x_center - box_width/2) * width
                    y_min = (y_center - box_height/2) * height
                    box_width = box_width * width
                    box_height = box_height * height
                    
                    # Añadir anotación
                    annotation_id += 1
                    
                    # Usar el mapeo para obtener el ID correcto de categoría
                    category_id = class_to_id.get(class_names[class_id], -1)
                    if category_id == -1:
                        print(f"Error: No se encontró categoría para class_id={class_id}")
                        continue
                    
                    coco_format["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_id,
                        "bbox": [x_min, y_min, box_width, box_height],
                        "area": box_width * box_height,
                        "segmentation": [],
                        "iscrowd": 0
                    })
                except Exception as e:
                    print(f"Error al procesar anotación en {txt_file}: {e}")
        
        # Mostrar progreso
        if image_id % 100 == 0:
            print(f"Procesadas {image_id} imágenes...")
    
    # Guardar el formato COCO en un archivo JSON
    with open(save_path, 'w') as f:
        json.dump(coco_format, f, indent=2)
    
    print(f"Conversión completada. Archivo guardado en {save_path}")
    print(f"Total de imágenes procesadas: {len(coco_format['images'])}")
    print(f"Total de anotaciones: {len(coco_format['annotations'])}")

def load_yaml(yaml_path):
    """
    Carga el archivo YAML que contiene la información de las clases.
    """
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
    return yaml_data

def main():
    parser = argparse.ArgumentParser(description='Convertir anotaciones YOLO a formato COCO')
    parser.add_argument('--root', type=str, required=True, help='Directorio raíz del dataset')
    parser.add_argument('--yaml', type=str, required=True, help='Ruta al archivo data.yaml')
    args = parser.parse_args()
    
    # Cargar las clases desde el archivo YAML
    yaml_data = load_yaml(args.yaml)
    class_names = yaml_data.get('names', [])
    
    if not class_names:
        print("ERROR: No se encontraron nombres de clases en el archivo YAML")
        return
    
    # Eliminar clases duplicadas manteniendo el orden
    unique_class_names = []
    for cls in class_names:
        if cls not in unique_class_names:
            unique_class_names.append(cls)
    
    print(f"Clases encontradas: {unique_class_names}")
    
    # Directorios para train y valid
    train_dir = os.path.join(args.root, 'train')
    valid_dir = os.path.join(args.root, 'valid')
    
    # Rutas donde guardar los archivos JSON
    train_save_path = os.path.join(train_dir, 'annotations.json')
    valid_save_path = os.path.join(valid_dir, 'annotations.json')
    
    # Convertir conjunto de entrenamiento
    if os.path.exists(train_dir):
        print(f"\nProcesando conjunto de ENTRENAMIENTO...")
        yolo_to_coco_format(train_dir, train_save_path, class_names, split='train')
    else:
        print(f"ADVERTENCIA: El directorio {train_dir} no existe")
    
    # Convertir conjunto de validación
    if os.path.exists(valid_dir):
        print(f"\nProcesando conjunto de VALIDACIÓN...")
        yolo_to_coco_format(valid_dir, valid_save_path, class_names, split='valid')
    else:
        print(f"ADVERTENCIA: El directorio {valid_dir} no existe")
    
    print("\nConversión completa.")

if __name__ == "__main__":
    main()
