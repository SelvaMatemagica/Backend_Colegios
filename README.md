# Backend alojado en amazon de la pagina de colegios

Proyecto fullstack basado en React, TypeScript, TailwindCSS y Radix UI, desarrollado en amazon aws.
---
## Cada una de las carpetas que se encuentran aqui, conforman el backend (hasta el dia 03/SEP/2025), las carpetas realizan lo siguiente:

1. BackColegios.
    ```información
    Esta carpeta cuenta con lo relacionado al inicio de sesión, registro, recuperación de cuenta y envio de correo electronico.
    Estas modificaciones son realizadas de forma estatica, puesto que cada acción tiene como consecuencia un cambio de pagina y son independientes a cada usuario registrado a la pagina.
    ```
2. BackColegiosJuan.
    ```información
    Esta carpeta cuenta con las consultas a la base de datos e inserción referente a los cuestionarios a enviar via mensaje por whatsapp.
    Además de contar con el modulo de envio de mensajes por whatsapp, usando la api de 2chat.
    Estas modificaciones son realizadas de forma estatica, puesto que cada acción tiene como consecuencia un cambio de pagina y son independientes a cada usuario registrado a la pagina.
    ```

3. WebSocketBackColegios.
    ```información
    Esta carpeta cuenta con el modulo websocket, que permite realizar actualizaciones de informacion en tiempo real a otros usuarios, esto para que la informacion que se modifica cambien sin la necesidad de realizar actualizaciones constantes a la pagina.
    Este modulo tiene la sección de obtencion de usuarios para las tablas que requieran visualizar esa informacion, ademas de actualizacion de datos y la insersion de usuarios via excel.
    Estas modificaciones son realizadas de forma dinamica, puesto que cada acción requiere que otros usuarios de la plataforma puedan visualizar informacion modificada.
    ```



## 🌐 Deploy AWS

  # Para realizar el deploy de la pagina con estas carpetas respaldadas requiere hacer lo siguiente

  1. Descargar la carpeta correspondiente
  2. Convertirlo a zip
  3. Subir el archivo comprimido a AWS Lambda
  4. Desplegar recursos en API Gateway
     ```información
    Para desplegar recursos en api gateway se requiere seleccionar el tipo de enpoint como REST y obtener los nombre de cada endpoint que se encuentran en el archivo lambda_handler, pues este tiene las rutas establecidas para cada uno de los endpoint
    Esas rutas sirven de referencia para hacer la llamada a la api, solo seria ajustar el tipo de metodo de envio de datos (GET, POST, PUT, etc.) eso si, es necesario activar el apartado de CORS y vincularlo con la funcion lambda

    En el caso de websocket es muy parecido, solamente tenemos que seleccionar el tipo de endpoint como websocket
    ```

## 📝 Notas
- Para que lambda funcione correctamente es necesario tener desplegadas las funciones lambda, asi como los metodos en el APIGateway.
- En cada una de las stages se requiere tener activado el metodo OPTIONS.
- NO activar el VPC a menos que se tenga todo ensamblado desde la misma red, es decir, servidor de archivos, servidor web, base de datos, servidor de correo y el cliente de pruebas.
