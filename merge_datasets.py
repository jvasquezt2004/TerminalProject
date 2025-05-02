#!/usr/bin/env python3

"""
Script para combinar (fusionar) múltiples conjuntos de datos (datasets) en uno solo, 
manteniendo la estructura de directorios original. 
Está específicamente adaptado para datasets en formato YOLO.

Script to merge multiple datasets into a single dataset for YOLOv5.
This script assumes that the datasets are structured in a specific way, with images and labels in separate folders.
"""

import os
import shutil
from pathlib import Path
import time

def create_directory(directory):
    """Crea un directorio si no existe."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directorio creado: {directory}")

def merge_datasets(source_datasets, target_dataset):
    """
    Combina múltiples datasets en uno solo, copiando los archivos (no moviéndolos).
    Mantiene la estructura de directorios original.
    
    Args:
        source_datasets: Lista de rutas a los datasets fuente
        target_dataset: Ruta al dataset destino
    """
    # Crear el directorio principal si no existe
    create_directory(target_dataset)
    
    # Definir las subcarpetas a copiar
    subdirs = ["train/images", "train/labels", "valid/images", "valid/labels"]
    
    # Crear estructura de directorios en el destino
    for subdir in subdirs:
        create_directory(os.path.join(target_dataset, subdir))
    
    # Copiar data.yaml de uno de los datasets (asumimos que son similares)
    if os.path.exists(os.path.join(source_datasets[0], "data.yaml")):
        shutil.copy2(
            os.path.join(source_datasets[0], "data.yaml"),
            os.path.join(target_dataset, "data.yaml")
        )
        print(f"Copiado: data.yaml")
    
    # Contador total de archivos
    total_files = 0
    start_time = time.time()
    
    # Para cada dataset fuente
    for dataset_dir in source_datasets:
        dataset_name = os.path.basename(dataset_dir)
        print(f"\nProcesando {dataset_name}...")
        
        # Para cada subdirectorio que queremos copiar
        for subdir in subdirs:
            source_dir = os.path.join(dataset_dir, subdir)
            target_dir = os.path.join(target_dataset, subdir)
            
            # Si el directorio fuente existe
            if os.path.exists(source_dir):
                files = os.listdir(source_dir)
                file_count = len(files)
                total_files += file_count
                
                print(f"Copiando {file_count} archivos de {dataset_name}/{subdir} a {os.path.basename(target_dataset)}/{subdir}")
                
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
    print(f"\nFusión completada. Se copiaron {total_files} archivos en {duration:.1f} segundos.")

if __name__ == "__main__":
    # Directorio base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directorios fuente (datasets 1 a 5)
    source_datasets = [
        os.path.join(base_dir, f"dataset{i}") 
        for i in range(1, 6)
    ]
    
    # Directorio destino
    target_dataset = os.path.join(base_dir, "cityscapes_yolo")
    
    # Verificar que existan los directorios fuente
    existing_datasets = [d for d in source_datasets if os.path.exists(d)]
    if not existing_datasets:
        print("Error: No se encontraron los directorios de datasets.")
        exit(1)
    
    print(f"Se encontraron {len(existing_datasets)} datasets:")
    for ds in existing_datasets:
        print(f"- {os.path.basename(ds)}")
    print(f"Destino: {target_dataset}")
    
    # Confirmar antes de proceder
    confirm = input("¿Deseas continuar? (s/n): ")
    if confirm.lower() != 's':
        print("Operación cancelada.")
        exit(0)
    
    # Ejecutar la fusión
    merge_datasets(existing_datasets, target_dataset)
