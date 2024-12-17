import sys, os
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem

from CursosProf import *
from ConectaBD import *

class CursosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.formulario = Ui_MainWindow()
        self.formulario.setupUi(self)
        self.MovData = RegCursos()

        self.cargar_cursos()
        
        self.listar()

        self.formulario.tableWidget.itemClicked.connect(self.seleccionar_registro)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        self.formulario.cbxCurso.currentIndexChanged.connect(self.calcular_costo)
        self.formulario.chkbPres.stateChanged.connect(self.calcular_costo)
        self.formulario.chkbOnl.stateChanged.connect(self.calcular_costo)
        self.formulario.chkbSem.stateChanged.connect(self.calcular_costo)
        self.formulario.rbM.toggled.connect(self.calcular_costo)
        self.formulario.rbT.toggled.connect(self.calcular_costo)
        self.formulario.rbN.toggled.connect(self.calcular_costo)

        self.formulario.btnInscribir.clicked.connect(self.inscribir)
        self.formulario.btnEditar.clicked.connect(self.actualizar)
        self.formulario.btnEliminar.clicked.connect(self.eliminar)
        self.formulario.pushButton_2.clicked.connect(self.salir)
        self.formulario.pushButton.clicked.connect(self.minimizar_ventana)

        self.formulario.btnInscribir.setEnabled(True)
        self.formulario.btnEditar.setEnabled(False)
        self.formulario.btnEliminar.setEnabled(False)

        self.start = QPoint(0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.start)
            event.accept()

    def mostrar_mensaje(self, titulo, mensaje, icono=QMessageBox.Information):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(icono)
        msg.exec_()

    def verificar_duplicado_dni(self, dni, exclude_dni=None):
        registros = self.MovData.listar_estudiantes()
        for registro in registros:
            dni_existente = registro[1]
            if dni == dni_existente and dni != exclude_dni:
                return True
        return False
    
    def validar_datos(self, dni, nombre):
        if not dni.isdigit():
            return "El DNI debe contener solo números."
        if len(dni) != 8:
            return "El DNI debe tener exactamente 8 dígitos."
        if not all(char.isalpha() or char.isspace() for char in nombre):
            return "El nombre debe contener solo letras y espacios."
        return None

    def cargar_cursos(self):
        cursos = ["Programación", "Diseño Gráfico", "Marketing Digital"]
        self.formulario.cbxCurso.addItems(cursos)

    def calcular_costo(self):
        curso = self.formulario.cbxCurso.currentText()
        precios_cursos = {
            "Programación": 500,
            "Diseño Gráfico": 400,
            "Marketing Digital": 300
        }
        costo_base = precios_cursos.get(curso, 0)

        modalidad = self.obtener_modalidad()
        if modalidad == "Online":
            costo_base *= 0.90
        elif modalidad == "Semipresencial":
            costo_base *= 0.95

        turno = self.obtener_Turno()
        if turno == "Tarde":
            costo_base *= 1.05
        elif turno == "Noche":
            costo_base *= 1.10

        self.formulario.lneTotal.setText(f"{costo_base:.2f}")

    def inscribir(self):
        dni = self.formulario.lneDni.text()
        nombre = self.formulario.lneNombre.text()
        curso = self.formulario.cbxCurso.currentText()
        modalidad = self.obtener_modalidad()
        turno = self.obtener_Turno()
        costo = self.formulario.lneTotal.text()

        if not (dni and nombre and modalidad and turno and costo):
            self.mostrar_mensaje("Error", "Por favor, complete todos los campos.", QMessageBox.Warning)
            return
        
        error = self.validar_datos(dni, nombre)
        if error:
            self.mostrar_mensaje("Error de Validación", error, QMessageBox.Warning)
            return
        
        if self.verificar_duplicado_dni(dni):
            self.mostrar_mensaje("Duplicado", f"El DNI {dni} ya está registrado.", QMessageBox.Warning)
            return

        self.MovData.insertar_estudiante(dni, nombre, curso, modalidad, turno, float(costo))
        
        self.listar()
        
        self.nuevo() 

    def listar(self):
        registros = self.MovData.listar_estudiantes()
        self.formulario.tableWidget.clearContents()
        self.formulario.tableWidget.setRowCount(len(registros))

        for row_idx, registro in enumerate(registros):
            for col_idx, campo in enumerate(registro[1:]):  # Excluyendo el ID
                self.formulario.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(campo)))

    def eliminar(self):
        selected_row = self.formulario.tableWidget.currentRow()
        if selected_row == -1:
            return

        dni = self.formulario.tableWidget.item(selected_row, 0).text()
        if not dni:
            return

        self.MovData.eliminar_estudiante(dni)

        self.listar()

        self.nuevo() 

    def seleccionar_registro(self, item):
        selected_row = item.row()

        dni = self.formulario.tableWidget.item(selected_row, 0).text()
        nombre = self.formulario.tableWidget.item(selected_row, 1).text()
        curso = self.formulario.tableWidget.item(selected_row, 2).text()
        modalidad = self.formulario.tableWidget.item(selected_row, 3).text()
        turno = self.formulario.tableWidget.item(selected_row, 4).text()
        costo = self.formulario.tableWidget.item(selected_row, 5).text()

        self.formulario.lneDni.setText(dni)
        self.formulario.lneNombre.setText(nombre)
        self.formulario.cbxCurso.setCurrentText(curso)
        self.seleccionar_modalidades(modalidad)
        self.seleccionar_turno(turno)
        self.formulario.lneTotal.setText(costo)

        self.formulario.btnInscribir.setEnabled(False)
        self.formulario.btnEliminar.setEnabled(True)
        self.formulario.btnEditar.setEnabled(True)

    def actualizar(self):
        dni = self.formulario.lneDni.text()
        nombre = self.formulario.lneNombre.text()
        curso = self.formulario.cbxCurso.currentText()
        modalidad = self.obtener_modalidad()
        turno = self.obtener_Turno()
        costo = self.formulario.lneTotal.text()

        if not (dni and nombre and modalidad and turno and costo):
            return

        self.MovData.actualizar_estudiante(dni, nombre, curso, modalidad, turno, float(costo))
        
        self.listar()
        
        self.nuevo()

        self.formulario.btnInscribir.setEnabled(True)
        self.formulario.btnEditar.setEnabled(False)
        self.formulario.btnEliminar.setEnabled(False)

    def obtener_modalidad(self):
        modalidades = []
        if self.formulario.chkbOnl.isChecked():
            modalidades.append("Online")
        if self.formulario.chkbPres.isChecked():
            modalidades.append("Presencial")
        if self.formulario.chkbSem.isChecked():
            modalidades.append("Semipresencial")
        return ", ".join(modalidades)

    def seleccionar_modalidades(self, modalidad):
        self.formulario.chkbOnl.setChecked(False)
        self.formulario.chkbPres.setChecked(False)
        self.formulario.chkbSem.setChecked(False)

        if modalidad == "Online":
            self.formulario.chkbOnl.setChecked(True)
        elif modalidad == "Presencial":
            self.formulario.chkbPres.setChecked(True)
        elif modalidad == "Semipresencial":
            self.formulario.chkbSem.setChecked(True)

    def obtener_Turno(self):
        if self.formulario.rbM.isChecked():
            return "Mañana"
        elif self.formulario.rbT.isChecked():
            return "Tarde"
        elif self.formulario.rbN.isChecked():
            return "Noche"
        return ""

    def seleccionar_turno(self, turno):
        self.formulario.rbM.setChecked(False)
        self.formulario.rbT.setChecked(False)
        self.formulario.rbN.setChecked(False)

        if turno == "Mañana":
            self.formulario.rbM.setChecked(True)
        elif turno == "Tarde":
            self.formulario.rbT.setChecked(True)
        elif turno == "Noche":
            self.formulario.rbN.setChecked(True)

    def nuevo(self):
        self.formulario.lneDni.setText("")
        self.formulario.lneNombre.setText("")
        self.formulario.cbxCurso.setCurrentIndex(0)
        self.formulario.chkbOnl.setChecked(False)
        self.formulario.chkbPres.setChecked(False)
        self.formulario.chkbSem.setChecked(False)
        self.formulario.rbM.setAutoExclusive(False)
        self.formulario.rbM.setChecked(False)
        self.formulario.rbT.setAutoExclusive(False)
        self.formulario.rbT.setChecked(False)
        self.formulario.rbN.setAutoExclusive(False)
        self.formulario.rbN.setChecked(False)
        self.formulario.lneTotal.setText("")
        self.formulario.lneNombre.setFocus()

    def salir(self):
        sys.exit()

    def minimizar_ventana(self):
        self.showMinimized()

os.system("cls") 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = CursosApp()
    myapp.show()
    sys.exit(app.exec_())