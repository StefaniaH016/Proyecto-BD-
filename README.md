# 🏆 Sistema de Gestión Mundial de Fútbol 2026

Este es un sistema de escritorio desarrollado en **Python** para la gestión integral de una base de datos de un torneo mundial de fútbol, utilizando **Oracle Database** como motor de persistencia.

## 🚀 Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
1.  **Python 3.10+**
2.  **Oracle Database** (XE o superior) configurado en `localhost/xe`.
3.  **Librerías de Python** necesarias.

## 📦 Instalación

1.  Clona o descarga este repositorio en tu máquina local.
2.  Abre una terminal en la carpeta raíz del proyecto e instala las dependencias:

```powershell
pip install oracledb pandas fpdf2 openpyxl
```

## 🛠️ Configuración de la Base de Datos

El sistema incluye un script automatizado para crear el esquema y cargar datos iniciales siguiendo el diagrama ER oficial.

1.  Verifica tus credenciales de Oracle en `database/db.py`.
2.  Ejecuta el script de inicialización:

```powershell
python database/init_db.py
```
*Este comando borrará cualquier versión anterior de las tablas y creará una base de datos limpia con 100 registros de prueba.*

## 🏃 Ejecución

Para iniciar la aplicación, ejecuta el archivo principal:

```powershell
python main.py
```

## 🔐 Credenciales de Acceso

Puedes ingresar con los siguientes perfiles predeterminados:

| Rol | Usuario | Contraseña |
| :--- | :--- | :--- |
| **Administrador** | admin | admin123 |
| **Tradicional** | user | user123 |
| **Esporádico** | invitado | invitado123 |

## 🛠️ Solución de Problemas (Base de Datos)

Si tienes problemas de conexión o tus credenciales de Oracle son diferentes:

### Cambiar contraseña de SYSTEM
Si no conoces la contraseña o quieres cambiarla a `ORLO` para que coincida con el código:
1. Abre una terminal (CMD o PowerShell) como **Administrador**.
2. Ejecuta el siguiente comando para entrar a Oracle sin contraseña:
   ```powershell
   sqlplus / as sysdba
   ```
3. Una vez dentro (`SQL>`), cambia la contraseña con:
   ```sql
   ALTER USER SYSTEM IDENTIFIED BY ORLO;
   ```
4. Si el usuario está bloqueado, desbloquéalo:
   ```sql
   ALTER USER SYSTEM ACCOUNT UNLOCK;
   ```
5. Sal con `exit`.

---

## ✨ Características Principales

---
*Desarrollado como parte del Proyecto de Base de Datos - 2026*
