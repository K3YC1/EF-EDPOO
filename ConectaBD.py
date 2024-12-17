import pyodbc

class RegCursos():
    def __init__(self):
        self.conn=pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server}'
                                 ';SERVER=LAPTOP-K3YC1'
                                 ';DATABASE=GestionCursos'
                                 ';Trusted_Connection=yes')

    def insertar_estudiante(self, dni, nombre, curso, modalidad, turno, costo):
        try:
            cur = self.conn.cursor()
            sql = '''
                INSERT INTO Estudiantes (Dni, Nombre, Curso, Modalidad, Turno, Costo)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cur.execute(sql, (dni, nombre, curso, modalidad, turno, costo))
            self.conn.commit()
            cur.close()
            print("Registro insertado correctamente.")
        except Exception as e:
            print(f"Error al insertar estudiante: {e}")

    
    def listar_estudiantes(self):
        try:
            cur = self.conn.cursor()
            sql = "SELECT * FROM Estudiantes"
            cur.execute(sql)
            registros = cur.fetchall()
            cur.close()
            return registros
        except Exception as e:
            print(f"Error al listar estudiantes: {e}")
            return []
        
    def actualizar_estudiante(self, dni, nombre, curso, modalidad, turno, costo):
        try:
            cur = self.conn.cursor()
            sql = '''
                UPDATE Estudiantes
                SET Nombre = ?, Curso = ?, Modalidad = ?, Turno = ?, Costo = ?
                WHERE Dni = ?
            '''
            cur.execute(sql, (nombre, curso, modalidad, turno, costo, dni))
            self.conn.commit()
            cur.close()
            print("Registro actualizado correctamente.")
        except Exception as e:
            print(f"Error al actualizar estudiante: {e}")

    def eliminar_estudiante(self, dni):
        try:
            cur = self.conn.cursor()
            sql = "DELETE FROM Estudiantes WHERE Dni = ?"
            cur.execute(sql, (dni,))
            self.conn.commit()
            cur.close()
            print("Registro eliminado correctamente.")
        except Exception as e:
            print(f"Error al eliminar estudiante: {e}")