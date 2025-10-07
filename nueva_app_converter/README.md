# Nueva App Convertidor de Nube de Puntos a Malla 3D

Esta aplicación permite convertir nubes de puntos (.las, .laz, .ply, .pcd, .xyz) en mallas 3D (.ply, .obj, .stl) de forma sencilla y eficiente, con una interfaz gráfica intuitiva.

## Características principales
- Carga y previsualización de nubes de puntos
- Preprocesado: downsampling (tamaño de voxel) y eliminación de outliers
- Métodos de reconstrucción: Poisson, Ball Pivoting, Alpha Shape
- Transferencia de color
- Opciones avanzadas: eliminar outliers, procesamiento paralelo, alta precisión, optimización de malla, percentil densidad, suavizar malla
- Guardado de malla en varios formatos

## Requisitos
- Windows 10/11
- Python 3.8+
- Ver dependencias en `requirements.txt`

## Instalación
```sh
cd nueva_app_converter
pip install -r requirements.txt
```

## Ejecución
```sh
python main.py
``` 