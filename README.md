# teleasistencia
Dado el crecimiento del proyecto y la cantidad de aplicaciones que engloba se ha redicido dividirlo en distintos proyectos GitHub correspondientes con cada aplicación:
1. https://github.com/IES-Valle-Jerte/teleasistencia-servidor-django
2. https://github.com/IES-Valle-Jerte/teleasistencia-cliente-angular
3. https://github.com/IES-Valle-Jerte/teleasistencia-cliente-android
4. https://github.com/IES-Valle-Jerte/teleasistencia-cliente-arduino-raspberrypi

Este proyecto consiste en un desarrollo Web de un servicio de Teleasistencia para que los alumnos del FP de Atención Sociosanitaria puedan realizar prácticas en el aula como si de un entorno real se tratase.

Para probar el proyecto, y antes de realizar la instalación, se recomienda que se sigan los pasos que aparecen en **Pasos para contribuir al proyecto**. 

## Dependencias:
Se gestionan en la instalación, a través del fichero *requerimentos.txt*. Las dejamos aquí apuntadas por si fuese necesario revisarlas:

1. ```pip install Django==3.2.3```
2. ```pip install django-model-utils==4.1.1```
3. ```pip install djangorestframework==3.12.4```
4. ```pip install django-rest-framework-social-oauth2==1.1.0```
5. ```pip install django-extensions==3.1.3```
6. ```pip install Werkzeug==2.0.2```
7. ```pip install pyOpenSSL==21.0.0```
8. ```pip install djangorestframework-simplejwt==5.0.0```


## Pasos para contribuir en el proyecto

Las contribuciones al proyecto se realizarán a través de [forks](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo) y [pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) sobre el proyecto original. Se puede encontrar [más información sobre este flujo de trabajo en la documentación de Github](https://docs.github.com/en/github/collaborating-with-pull-requests).

1. Realizar un **fork** del proyecto pulsando sobre el icono de fork. Cuando se realiza un fork, se crea una copia del repositorio remoto en Github, de tal manera que el usuario que hace fork tiene una copia para poder realizar modificaciones sin que afecte al desarrollo del repositorio principal o de otros forks.

    <img src="https://user-images.githubusercontent.com/3669279/122238595-8c6e1780-cec0-11eb-8388-561c7ad3d250.png" width="150">

2. Clonar el proyecto en local para su instalación y modificación. 

    <img src="https://user-images.githubusercontent.com/3669279/122239016-e242bf80-cec0-11eb-854c-936d8433b8ea.png" width="400">

Existen varias maneras de clonar un proyecto. Para simplificar todas las tareas con Git-Github se recomienda instalar [Github Desktop](https://desktop.github.com/) y trabajar desde su propia interfaz gráfica.

3. Realiza la instalación del proyecto siguiendo los **Pasos para la instalación**.
4. Realiza las modificaciones/mejoras que consideres oportunas. Revisa los [Issues del proyecto original](https://github.com/IES-Valle-Jerte/teleasistencia_navalmoral/issues) para encontrar necesidades donde puedes contribuir.     
5. Una vez has desarrollado tus contribuciones y las has probado, puedes solicitar que los cambios se añadan al repositorio principal mediante un Pull Request:

    ![image](https://user-images.githubusercontent.com/3669279/122243564-824e1800-cec4-11eb-9cd6-e93938341098.png)



## Pasos para la instalación:

1. Instalación de python - https://www.python.org/ . Seleccionar la opción que nos permite añadir python al PATH. 
   Comprobamos la instalación desde cmd: ```python --version```
2. Descargamos e instalamos el Entorno de desarrollo PyCharm - https://www.jetbrains.com/pycharm/
3. Creamos el [entorno virutal](https://docs.python.org/3/library/venv.html) en la ruta Server ```virtualenv venviorment```

    <img src="https://user-images.githubusercontent.com/3669279/122421218-847ba980-cf8c-11eb-829c-2dccf74a3e6d.png" width="400">


5. Ejecutamos el siguiente archivo para seleccionar el entorno virtual ```Server/venviorment/Scripts/activate```. Si tuviésemos problemas de permisos para ejecutar dicho comando, revisar [este enlace](https://tecadmin.net/powershell-running-scripts-is-disabled-system/) y correr el comando que aparece como superadministrador en PowerShell.
6. Hacemos permanente el entorno virtual. Vamos a ```File -> Settings... -> Project --> Python Interpreter``` y seleccionamos el Interprete **ya creado**  ```Server\venviorment\Scripts\python.exe```

    ![image](https://user-images.githubusercontent.com/57873286/122095294-794e3f80-ce0d-11eb-9577-985b2d170102.png)

8. Actualizamos pip ```pip install --upgrade pip```
9. Instalamos los requerimientos ```pip install -r requerimientos.txt```. Es posible que haya errores durante la instalación de los requisitos, si ocurriesen errores del tipo ```  ```, sería necesario instalar algunos componentes para ejecutar C++ como aparece en la respuesta de [esta pregunta de Stackoverflow](https://stackoverflow.com/questions/64261546/python-cant-install-packages) (Descargar vs_buildtools y ejecutar el comando que aparece al final de la respuesta marcada como solución).



## Arrancar el proyecto

Desde Server\teleasistencia ejecutamos ```python manage.py runserver_plus --cert-file cert.pem --key-file key.pem```


## Comprobar las peticiones

Las peticiones de la API-Rest están documentadas en [Postman](https://www.postman.com/cloudy-space-364257/workspace/tla-teleasistencia-development).

## Licencia

El software ha sido desarrollado bajo la licencia GPL3 por el departamento de Informática del IES Valle del Jerte de Plasencia, con la colaboración principal de Fréderic Sánchez, Angel Enrique Pineda y Jesús Redondo.

Los alumnos que han contribuido en el desarrollo de este proyecto y la labor que han realizado son:
- **Lucía González**: Creación de la primera versión del cliente Angular.
- **Javier Fernández**: Inicialización completa de la API-Rest y Postman.

Especial mención al departamento de Atención Sociosanitaria del IES San Martín de Talayuela. Partícipes e impulsores de la plataforma de prácticas de Teleasistencia. 


 

[Sobre el Gitignore](https://djangowaves.com/tips-tricks/gitignore-for-a-django-project/)
