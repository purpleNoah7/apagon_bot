# Apagones

Apagones es un bot de telegram que te permite con una base de datos sqlite guardar horarios de apagones 
se pensó en un inicio para mantener al pueblo cubano informado de los apagones que tiene nuestro país.

## Instalación

Para instalar Apagones, primero debes clonar el repositorio en tu computadora. Luego, debes crear una base de datos en tu computadora con el siguiente comando:

```bash
python3 create_database.py
```

Una vez que hayas creado la base de datos, puedes instalar el bot con el siguiente comando:

```bash
python3 -m pip install -r requirements.txt
```

## Configuración

Para configurar Apagones, primero debes crear un bot de telegram en el [BotFather](https://t.me/BotFather). Luego, debes copiar el token de tu bot y pegarlo en el archivo `.env`. También debes configurar tus datos de usuario en la base de datos. Para hacerlo, ejecuta el siguiente comando:

```bash
python3 create_user.py
```

## Ejecución

Para ejecutar Apagones, debes ejecutar el siguiente comando:

```bash
python3 main.py
```

## Contribuciones

Si deseas contribuir a Apagones, puedes hacerlo de varias maneras:

- Reportando errores o sugiriendo mejoras en el código.
- Haciendo Pull Requests con correcciones o mejoras.
- Escribiendo artículos o tutoriales sobre Apagones.

## Licencia

Este proyecto está bajo la Licencia GNU General Public License (GPL) - consulta el archivo [LICENSE](LICENSE.txt) para más detalles.
