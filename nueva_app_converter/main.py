import sys
import multiprocessing
multiprocessing.freeze_support()
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QMessageBox, QGroupBox, QProgressBar, QToolButton, QDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon
from procesado.preprocesado import downsample_point_cloud, remove_outliers
from procesado.reconstruccion import reconstruir_poisson, reconstruir_ball_pivoting, reconstruir_alpha_shape
from procesado.color import transferir_color
from utils.io import leer_nube, guardar_malla
import open3d as o3d
import numpy as np
import time
import tempfile
import os
from worker import conversion_worker, eliminar_componentes_pequenas_worker

class ConversionThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(object, object, str)  # mesh, pcd, error_msg
    def __init__(self, parent, params):
        super().__init__(parent)
        self.params = params
        self._cancel = False
    def run(self):
        try:
            self.status.emit("Cargando nube de puntos...")
            self.progress.emit(5)
            pcd = leer_nube(self.params['input_file'])
            if self._cancel: self._emit_cancel(); return
            self.status.emit("Preprocesando nube...")
            self.progress.emit(20)
            pcd = downsample_point_cloud(pcd, self.params['voxel'])
            if self.params['eliminar_outliers']:
                pcd = remove_outliers(pcd, nb_neighbors=self.params['nb_neighbors'], std_ratio=self.params['std_ratio'])
            if self._cancel: self._emit_cancel(); return
            # --- Preprocesado extra ---
            pcd.remove_duplicated_points()
            import numpy as np
            pts = np.asarray(pcd.points)
            centro = pts.mean(axis=0)
            pcd.points = o3d.utility.Vector3dVector(pts - centro)
            print(f'Nº de puntos tras preprocesado: {len(pcd.points)}')
            print('Mínimo:', pts.min(axis=0))
            print('Máximo:', pts.max(axis=0))
            # --- Fin preprocesado extra ---
            self.status.emit("Calculando normales...")
            self.progress.emit(30)
            pcd.estimate_normals()
            pcd.orient_normals_consistent_tangent_plane(100)
            if self._cancel: self._emit_cancel(); return
            self.status.emit("Reconstruyendo malla...")
            self.progress.emit(50)
            metodo = self.params['metodo']
            if metodo == "poisson":
                mesh = reconstruir_poisson(pcd, depth=self.params['param'], density_percentile=self.params['dens'])
            elif metodo == "ball_pivoting":
                mesh = reconstruir_ball_pivoting(pcd, radio=self.params['param']/100.0)
            elif metodo == "alpha_shape":
                mesh = reconstruir_alpha_shape(pcd, alpha=self.params['param']/100.0)
            else:
                self.finished.emit(None, None, "Método de reconstrucción no soportado."); return
            if self._cancel: self._emit_cancel(); return
            self.status.emit("Transfiriendo color...")
            self.progress.emit(70)
            mesh = transferir_color(mesh, pcd, metodo=self.params['color_method'], k_neighbors=self.params['k'])
            if self._cancel: self._emit_cancel(); return
            if self.params['eliminar_fragmentos']:
                self.status.emit("Eliminando fragmentos pequeños...")
                mesh = MainWindow.eliminar_componentes_pequenas_static(mesh, self.params['min_comp'])
            if self._cancel: self._emit_cancel(); return
            if self.params['suavizar']:
                self.status.emit("Suavizando malla...")
                mesh = mesh.filter_smooth_simple(number_of_iterations=1)
            self.progress.emit(100)
            self.status.emit("Conversión completada.")
            self.finished.emit(mesh, pcd, "")
        except Exception as e:
            self.finished.emit(None, None, str(e))
    def cancel(self):
        self._cancel = True
    def _emit_cancel(self):
        self.status.emit("Conversión cancelada.")
        self.finished.emit(None, None, "Conversión cancelada por el usuario.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Convertidor de Nube de Puntos a Malla 3D - Simple")
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icono.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "icono.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()
        self.input_file = None
        self.pcd = None
        self.mesh = None
        self.proc = None
        self.queue = None
        self.timer = None
        self.mesh_path = None
        self.pcd_path = None
        self.temp_files = []

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Archivo de entrada
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Archivo de nube de puntos: No seleccionado")
        btn_file = QPushButton("Seleccionar archivo")
        btn_file.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(btn_file)
        main_layout.addLayout(file_layout)

        # Tamaño de voxel
        voxel_layout = QHBoxLayout()
        voxel_layout.addWidget(QLabel("Tamaño de voxel:"))
        self.voxel_spin = QDoubleSpinBox()
        self.voxel_spin.setRange(0.0, 1.0)
        self.voxel_spin.setSingleStep(0.01)
        self.voxel_spin.setValue(0.02)
        voxel_layout.addWidget(self.voxel_spin)
        main_layout.addLayout(voxel_layout)

        # Opciones avanzadas
        adv_group = QGroupBox("Opciones avanzadas")
        adv_layout = QVBoxLayout()
        # Eliminar outliers
        outlier_layout = QHBoxLayout()
        self.outlier_check = QCheckBox("Eliminar outliers")
        self.outlier_check.setChecked(True)
        outlier_info = self._add_info_button(
            "Filtrado de outliers",
            "<b>¿Qué es?</b><br>Activa el filtrado de puntos ruidosos (outliers) en la nube.<br><br><b>Recomendación:</b> Déjalo activado salvo que tu nube sea muy limpia."
        )
        outlier_layout.addWidget(self.outlier_check)
        outlier_layout.addWidget(outlier_info)
        adv_layout.addLayout(outlier_layout)
        # Eliminar duplicados
        dup_layout = QHBoxLayout()
        self.dup_check = QCheckBox("Eliminar puntos duplicados")
        self.dup_check.setChecked(True)
        dup_info = self._add_info_button(
            "Eliminar duplicados",
            "<b>¿Qué es?</b><br>Elimina puntos que están exactamente en la misma posición.<br><br><b>Recomendación:</b> Déjalo activado salvo que necesites conservar todos los puntos originales, incluso los repetidos."
        )
        dup_layout.addWidget(self.dup_check)
        dup_layout.addWidget(dup_info)
        adv_layout.addLayout(dup_layout)
        # Parámetros de outliers
        outlier_params_layout = QHBoxLayout()
        outlier_params_layout.addWidget(QLabel("Vecinos outliers:"))
        self.nb_neighbors_spin = QSpinBox()
        self.nb_neighbors_spin.setRange(5, 100)
        self.nb_neighbors_spin.setValue(20)
        nb_neighbors_info = self._add_info_button(
            "Vecinos outliers",
            "<b>¿Qué es?</b><br>Número de vecinos que se consideran para cada punto al detectar y eliminar outliers (ruido).<br><br><b>Recomendación:</b> Prueba con 20-30. Si ves que se eliminan puntos válidos, reduce el valor."
        )
        outlier_params_layout.addWidget(self.nb_neighbors_spin)
        outlier_params_layout.addWidget(nb_neighbors_info)
        outlier_params_layout.addWidget(QLabel("STD ratio:"))
        self.std_ratio_spin = QDoubleSpinBox()
        self.std_ratio_spin.setRange(0.5, 5.0)
        self.std_ratio_spin.setSingleStep(0.1)
        self.std_ratio_spin.setValue(2.0)
        std_ratio_info = self._add_info_button(
            "STD ratio",
            "<b>¿Qué es?</b><br>Umbral de tolerancia al ruido. Cuanto menor, más estricta es la eliminación de puntos atípicos.<br><br><b>Recomendación:</b> Empieza con 2.0. Ajusta según el resultado visual."
        )
        outlier_params_layout.addWidget(self.std_ratio_spin)
        outlier_params_layout.addWidget(std_ratio_info)
        adv_layout.addLayout(outlier_params_layout)
        # Procesamiento paralelo
        parallel_layout = QHBoxLayout()
        self.parallel_check = QCheckBox("Procesamiento paralelo")
        self.parallel_check.setChecked(True)
        parallel_info = self._add_info_button(
            "Procesamiento paralelo",
            "<b>¿Qué es?</b><br>Permite usar varios núcleos del procesador para acelerar el cálculo.<br><br><b>Recomendación:</b> Actívalo salvo que experimentes problemas de memoria."
        )
        parallel_layout.addWidget(self.parallel_check)
        parallel_layout.addWidget(parallel_info)
        adv_layout.addLayout(parallel_layout)
        # Alta precisión
        precision_layout = QHBoxLayout()
        self.precision_check = QCheckBox("Alta precisión (normales)")
        self.precision_check.setChecked(False)
        precision_info = self._add_info_button(
            "Alta precisión",
            "<b>¿Qué es?</b><br>Utiliza parámetros más exigentes en la reconstrucción para obtener una malla más detallada, pero más lenta.<br><br><b>Recomendación:</b> Úsalo solo en nubes limpias y bien alineadas."
        )
        precision_layout.addWidget(self.precision_check)
        precision_layout.addWidget(precision_info)
        adv_layout.addLayout(precision_layout)
        # Optimizar malla
        optimize_layout = QHBoxLayout()
        self.optimize_check = QCheckBox("Optimizar malla")
        self.optimize_check.setChecked(True)
        optimize_info = self._add_info_button(
            "Optimizar malla",
            "<b>¿Qué es?</b><br>Aplica un suavizado y simplificación extra tras la reconstrucción para mejorar la apariencia y reducir el tamaño.<br><br><b>Recomendación:</b> Actívalo si quieres una malla más ligera y suave."
        )
        optimize_layout.addWidget(self.optimize_check)
        optimize_layout.addWidget(optimize_info)
        adv_layout.addLayout(optimize_layout)
        # Percentil densidad
        dens_layout = QHBoxLayout()
        dens_layout.addWidget(QLabel("Percentil densidad:"))
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.0, 0.2)
        self.density_spin.setSingleStep(0.01)
        self.density_spin.setValue(0.01)
        density_info = self._add_info_button(
            "Percentil densidad",
            "<b>¿Qué es?</b><br>Elimina los vértices menos densos tras la reconstrucción (por ejemplo, el 5% más disperso).<br><br><b>Recomendación:</b> Prueba con 5%. Sube si ves mucho ruido residual."
        )
        dens_layout.addWidget(self.density_spin)
        dens_layout.addWidget(density_info)
        adv_layout.addLayout(dens_layout)
        # Suavizar malla
        smooth_layout = QHBoxLayout()
        self.smooth_check = QCheckBox("Suavizar malla")
        self.smooth_check.setChecked(True)
        smooth_info = self._add_info_button(
            "Suavizar malla",
            "<b>¿Qué es?</b><br>Aplica un filtro para suavizar la superficie de la malla, eliminando picos y artefactos.<br><br><b>Recomendación:</b> Actívalo si buscas una superficie más uniforme."
        )
        smooth_layout.addWidget(self.smooth_check)
        smooth_layout.addWidget(smooth_info)
        adv_layout.addLayout(smooth_layout)
        # Eliminar fragmentos pequeños
        frag_layout = QHBoxLayout()
        self.remove_small_comp_check = QCheckBox("Eliminar fragmentos pequeños")
        self.remove_small_comp_check.setChecked(True)
        frag_info = self._add_info_button(
            "Eliminar fragmentos",
            "<b>¿Qué es?</b><br>Elimina trozos de malla muy pequeños que suelen ser ruido tras la reconstrucción.<br><br><b>Recomendación:</b> Actívalo siempre que quieras una malla limpia."
        )
        frag_layout.addWidget(self.remove_small_comp_check)
        frag_layout.addWidget(frag_info)
        frag_layout.addWidget(QLabel("Tamaño mínimo de componente:"))
        self.min_comp_spin = QSpinBox()
        self.min_comp_spin.setRange(10, 10000)
        self.min_comp_spin.setValue(1000)
        min_comp_info = self._add_info_button(
            "Tamaño mínimo de componente",
            "<b>¿Qué es?</b><br>Tamaño mínimo de triángulos para que un fragmento de malla se conserve.<br><br><b>Recomendación:</b> Sube el valor si ves muchos fragmentos pequeños no deseados."
        )
        frag_layout.addWidget(self.min_comp_spin)
        frag_layout.addWidget(min_comp_info)
        adv_layout.addLayout(frag_layout)
        adv_group.setLayout(adv_layout)
        main_layout.addWidget(adv_group)

        # Método de reconstrucción
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Método de reconstrucción:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["poisson", "ball_pivoting", "alpha_shape"])
        # Botón de info para método de reconstrucción
        method_info = self._add_info_button(
            "Método de reconstrucción",
            "<b>¿Qué es?</b><br>Define el algoritmo utilizado para convertir la nube de puntos en una malla 3D.<br><ul><li><b>Poisson:</b> Generalmente da buenos resultados en nubes densas y limpias.</li><li><b>Ball Pivoting:</b> Útil para nubes uniformes y con pocos huecos.</li><li><b>Alpha Shape:</b> Bueno para formas abiertas o con huecos grandes.</li></ul><br><b>Recomendación:</b> Prueba primero con Poisson. Si el resultado no es bueno, experimenta con los otros métodos.")
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(method_info)
        self.param_label = QLabel("Profundidad:")
        # Botón de info para parámetro principal (profundidad/radio/alpha)
        param_info = self._add_info_button(
            "Parámetro principal",
            "<b>¿Qué es?</b><br>Parámetro principal del método de reconstrucción seleccionado:<ul><li><b>Profundidad (Poisson):</b> Controla el nivel de detalle. Valores altos generan mallas más detalladas pero más pesadas.</li><li><b>Radio bola (Ball Pivoting):</b> Define el tamaño de la esfera que conecta los puntos.</li><li><b>Alpha (Alpha Shape):</b> Controla el grado de 'ajuste' de la malla a la nube de puntos.</li></ul><br><b>Recomendación:</b> Usa el valor por defecto y ajústalo si la malla sale demasiado simple o con mucho ruido.")
        method_layout.addWidget(self.param_label)
        self.param_spin = QSpinBox()
        self.param_spin.setRange(5, 15)
        self.param_spin.setValue(9)
        method_layout.addWidget(self.param_spin)
        method_layout.addWidget(param_info)
        main_layout.addLayout(method_layout)
        self.method_combo.currentTextChanged.connect(self.update_param_label)

        # Método de color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Método de color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["nearest", "weighted", "interpolated"])
        # Botón de info para método de color
        color_info = self._add_info_button(
            "Método de color",
            "<b>¿Qué es?</b><br>Selecciona cómo se transfiere el color de la nube de puntos a la malla:<ul><li><b>Nearest:</b> Usa el color del punto más cercano.</li><li><b>Weighted:</b> Promedia los colores de los vecinos más cercanos.</li><li><b>Interpolated:</b> Interpola el color usando varios vecinos.</li></ul><br><b>Recomendación:</b> 'Nearest' es rápido y suele ser suficiente. Usa 'Weighted' o 'Interpolated' si ves artefactos de color.")
        color_layout.addWidget(self.color_combo)
        color_layout.addWidget(color_info)
        color_layout.addWidget(QLabel("Vecinos para color:"))
        self.k_neighbors_spin = QSpinBox()
        self.k_neighbors_spin.setRange(1, 20)
        self.k_neighbors_spin.setValue(10)
        # Botón de info para vecinos de color
        k_info = self._add_info_button(
            "Vecinos para color",
            "<b>¿Qué es?</b><br>Cantidad de puntos vecinos que se consideran al calcular el color de cada vértice de la malla.<br><br><b>Recomendación:</b> Valores entre 5 y 10 suelen funcionar bien. Si el color se ve poco natural, prueba a aumentar el número.")
        color_layout.addWidget(self.k_neighbors_spin)
        color_layout.addWidget(k_info)
        main_layout.addLayout(color_layout)

        # Botones de acción
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("Previsualizar nube")
        self.btn_convert = QPushButton("Convertir a malla 3D")
        self.btn_visualize = QPushButton("Visualizar malla")
        self.btn_save = QPushButton("Guardar malla")
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_convert)
        btn_layout.addWidget(self.btn_visualize)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)
        # Barra de progreso y cancelar
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("")
        progress_layout.addWidget(self.status_label)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancelar_conversion)
        progress_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(progress_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Conectar botones
        self.btn_preview.clicked.connect(self.previsualizar_nube)
        self.btn_convert.clicked.connect(self.convertir_malla)
        self.btn_visualize.clicked.connect(self.visualizar_malla)
        self.btn_save.clicked.connect(self.guardar_malla)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar nube de puntos", "", "Point Cloud Files (*.ply *.pcd *.xyz *.xyzrgb *.las *.laz)")
        if file_path:
            self.file_label.setText(f"Archivo: {file_path}")
            self.input_file = file_path
            self.pcd = None
            self.mesh = None

    def update_param_label(self, method):
        if method == "poisson":
            self.param_label.setText("Profundidad:")
            self.param_spin.setRange(5, 15)
            self.param_spin.setValue(9)
        elif method == "ball_pivoting":
            self.param_label.setText("Radio bola:")
            self.param_spin.setRange(1, 100)
            self.param_spin.setValue(10)
        elif method == "alpha_shape":
            self.param_label.setText("Alpha:")
            self.param_spin.setRange(1, 100)
            self.param_spin.setValue(10)

    def previsualizar_nube(self):
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Selecciona un archivo de nube de puntos.")
            return
        self.pcd = leer_nube(self.input_file)
        # Preprocesado
        voxel = self.voxel_spin.value()
        self.pcd = downsample_point_cloud(self.pcd, voxel)
        if self.outlier_check.isChecked():
            nb = self.nb_neighbors_spin.value()
            std = self.std_ratio_spin.value()
            self.pcd = remove_outliers(self.pcd, nb_neighbors=nb, std_ratio=std)
        # Centrar ventana en pantalla 1920x1080 (ajusta left/top si tu pantalla es diferente)
        width, height = 1200, 800
        left = (1920 - width) // 2  # Centrado horizontal
        top = (1080 - height) // 2  # Centrado vertical
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name="Nube preprocesada", width=width, height=height, left=left, top=top)
        vis.add_geometry(self.pcd)
        vis.run()
        vis.destroy_window()

    def convertir_malla(self):
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Selecciona un archivo de nube de puntos.")
            return
        self.btn_convert.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando conversión...")
        params = {
            'input_file': self.input_file,
            'voxel': self.voxel_spin.value(),
            'eliminar_outliers': self.outlier_check.isChecked(),
            'nb_neighbors': self.nb_neighbors_spin.value(),
            'std_ratio': self.std_ratio_spin.value(),
            'metodo': self.method_combo.currentText(),
            'param': self.param_spin.value(),
            'dens': self.density_spin.value(),
            'color_method': self.color_combo.currentText(),
            'k': self.k_neighbors_spin.value(),
            'eliminar_fragmentos': self.remove_small_comp_check.isChecked(),
            'min_comp': self.min_comp_spin.value(),
            'suavizar': self.smooth_check.isChecked(),
            'eliminar_duplicados': self.dup_check.isChecked()
        }
        self.queue = multiprocessing.Queue()
        self.proc = multiprocessing.Process(target=conversion_worker, args=(params, self.queue))
        self.proc.start()
        self.timer = self.startTimer(100)  # 100 ms

    def closeEvent(self, event):
        try:
            # Limpiar archivos temporales
            for f in self.temp_files:
                try:
                    os.remove(f)
                except Exception:
                    pass
            event.accept()
        except Exception:
            event.accept()

    def timerEvent(self, event):
        try:
            queue = self.queue  # Captura la referencia actual
            if queue is None:
                return
            while not queue.empty():
                msg = queue.get()
                if isinstance(msg, dict):
                    if 'progress' in msg:
                        self.progress_bar.setValue(msg['progress'])
                    if 'status' in msg:
                        self.status_label.setText(msg['status'])
                    if 'result' in msg:
                        mesh_path, pcd_path, error_msg = msg['result']
                        self.killTimer(self.timer)
                        self.timer = None
                        self.proc = None
                        self.queue = None
                        self.btn_convert.setEnabled(True)
                        self.btn_cancel.setEnabled(False)
                        if error_msg:
                            QMessageBox.warning(self, "Error", error_msg)
                            self.status_label.setText(error_msg)
                            self.progress_bar.setValue(0)
                            self.mesh_path = None
                            self.pcd_path = None
                            return
                        self.mesh_path = mesh_path
                        self.pcd_path = pcd_path
                        self.temp_files.extend([mesh_path, pcd_path])
                        self.status_label.setText("Conversión completada.")
                        self.progress_bar.setValue(100)
                        # Mostrar mensaje de éxito SIN cerrar la app
                        QMessageBox.information(self, "Éxito", "Malla generada correctamente.\nAhora puedes visualizar o guardar la malla desde los botones de la interfaz.")
        except Exception as e:
            QMessageBox.critical(self, "Error interno", f"Ocurrió un error inesperado: {str(e)}")

    def cancelar_conversion(self):
        if self.proc is not None and self.proc.is_alive():
            self.proc.terminate()
            self.proc = None
            self.queue = None
            if self.timer:
                self.killTimer(self.timer)
                self.timer = None
            self.status_label.setText("Conversión cancelada.")
            self.btn_cancel.setEnabled(False)
            self.btn_convert.setEnabled(True)

    def visualizar_malla(self):
        if self.mesh_path is not None and os.path.exists(self.mesh_path):
            mesh = o3d.io.read_triangle_mesh(self.mesh_path)
            # Centrar ventana en pantalla 1920x1080 (ajusta left/top si tu pantalla es diferente)
            width, height = 1200, 800
            left = (1920 - width) // 2  # Centrado horizontal
            top = (1080 - height) // 2  # Centrado vertical
            vis = o3d.visualization.Visualizer()
            vis.create_window(window_name="Malla 3D", width=width, height=height, left=left, top=top)
            vis.add_geometry(mesh)
            vis.run()
            vis.destroy_window()
        else:
            QMessageBox.warning(self, "Error", "Primero genera una malla.")

    def guardar_malla(self):
        if self.mesh_path is None or not os.path.exists(self.mesh_path):
            QMessageBox.warning(self, "Error", "Primero genera una malla.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar malla 3D", "", "Mesh Files (*.ply *.stl *.obj)")
        if file_path:
            mesh = o3d.io.read_triangle_mesh(self.mesh_path)
            ok = o3d.io.write_triangle_mesh(file_path, mesh)
            if ok:
                QMessageBox.information(self, "Éxito", "Malla guardada correctamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar la malla.")

    def _add_info_button(self, tooltip_corto, texto_largo_html):
        btn = QToolButton()
        btn.setText("i")
        btn.setFixedSize(24, 24)
        # No setToolTip, solo popup al hacer clic
        btn.clicked.connect(lambda: QMessageBox.information(self, "Ayuda", texto_largo_html))
        return btn

    @staticmethod
    def eliminar_componentes_pequenas_static(mesh, min_triangles=1000):
        mesh = mesh.remove_unreferenced_vertices()
        triangle_clusters, cluster_n_triangles, _ = mesh.cluster_connected_triangles()
        triangle_clusters = np.asarray(triangle_clusters)
        cluster_n_triangles = np.asarray(cluster_n_triangles)
        large_clusters = [i for i, n in enumerate(cluster_n_triangles) if n > min_triangles]
        triangles_to_remove = [i for i, c in enumerate(triangle_clusters) if c not in large_clusters]
        mesh.remove_triangles_by_index(triangles_to_remove)
        mesh.remove_unreferenced_vertices()
        return mesh

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Estilo global para tooltips cuadrados
    app.setStyleSheet("""
    QToolTip {
        min-width: 120px;
        min-height: 120px;
        max-width: 120px;
        max-height: 120px;
        color: #ffffff;
        background-color: #353535;
        border: 1px solid white;
        font-size: 12pt;
    }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 