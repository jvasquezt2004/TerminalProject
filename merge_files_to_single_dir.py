#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import time

def create_directory(directory):
    """Se crea el directorio si no existe."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directorio creado: {directory}")

def merge_files_to_single_dir(source_dataset, target_dataset):
    """
    Reorganiza los archivos para tener imágenes y etiquetas en un solo directorio.
    
    Args:
        source_dataset: Ruta al dataset fuente (con estructura train/images, train/labels, etc.)
        target_dataset: Ruta al dataset destino (con estructura train/, valid/)
    """
    # Crear directorio principal si no existe
    create_directory(target_dataset)
    
    # Crear  directorios de destino
    create_directory(os.path.join(target_dataset, "train"))
    create_directory(os.path.join(target_dataset, "valid"))
    
    # Copiar data.yaml si existe
    if os.path.exists(os.path.join(source_dataset, "data.yaml")):
        shutil.copy2(
            os.path.join(source_dataset, "data.yaml"),
            os.path.join(target_dataset, "data.yaml")
        )
        print(f"Copiado: data.yaml")
    
    # Contador total de archivos
    total_files = 0
    start_time = time.time()
    
    # Directorios a procesar
    dirs_to_process = [
        ("train/images", "train"),
        ("train/labels", "train"),
        ("valid/images", "valid"),
        ("valid/labels", "valid")
    ]
    
    # Para cada directorio a procesar
    for source_subdir, target_subdir in dirs_to_process:
        source_dir = os.path.join(source_dataset, source_subdir)
        target_dir = os.path.join(target_dataset, target_subdir)
        
        # Si el directorio fuente existe
        if os.path.exists(source_dir):
            files = os.listdir(source_dir)
            file_count = len(files)
            total_files += file_count
            
            print(f"Copiando {file_count} archivos de {source_subdir} a {target_subdir}")
            
            # Copiar cada archivo
            for i, filename in enumerate(files):
                source_file = os.path.join(source_dir, filename)
                target_file = os.path.join(target_dir, filename)
                
                # Solo muestra progreso cada 100 archivos para no saturar la salida
                if i % 100 == 0:
                    print(f"  Progreso: {i}/{file_count} archivos")
                
                # Copiar el archivo
                shutil.copy2(source_file, target_file)
    
    # Mostrar estadísticas
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nReorganización completada. Se copiaron {total_files} archivos en {duration:.1f} segundos.")

if __name__ == "__main__":
    # Directorio base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directorio fuente (cityscapes_yolo que ya creamos)
    source_dataset = os.path.join(base_dir, "cityscapes_yolo")
    
    # Directorio destino
    target_dataset = os.path.join(base_dir, "cityscapes_yolo_flat")
    
    # Verificar que exista el directorio fuente
    if not os.path.exists(source_dataset):
        print(f"Error: No se encontró el directorio fuente {source_dataset}.")
        exit(1)
    
    print(f"Fuente: {source_dataset}")
    print(f"Destino: {target_dataset}")
    
    # Confirmar antes de proceder
    confirm = input("¿Deseas continuar? (s/n): ")
    if confirm.lower() != 's':
        print("Operación cancelada.")
        exit(0)
    
    # Ejecutar la reorganización
    merge_files_to_single_dir(source_dataset, target_dataset)
