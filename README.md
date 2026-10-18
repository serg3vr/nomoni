# Nomoni

Nomoni es una aplicación web para registrar gastos personales. Su premisa es que anotar un gasto no debería costar nada de esfuerzo: solo escribes el monto y listo. La categoría y el monedero puedes asignarlos después, y el dashboard te muestra cómo va tu mes.

## Instalación

Necesitas Docker y PostgreSQL instalado en tu máquina (la base de datos no va en un contenedor), con una base de datos `nomoni` ya creada y vacía.

Primero copia las plantillas de configuración:

```bash
cp back/api/.env.dist back/api/.env
cp docker-compose.yml.dist docker-compose.yml
cp docker/Dockerfile.dist docker/Dockerfile
```

Los archivos resultantes están en `.gitignore`: ahí van tus datos reales, las plantillas `.dist` solo llevan ejemplos.

En `back/api/.env` llena tres valores:

```env
JWT_SECRET=una_cadena_larga_y_aleatoria
APP_RUNTIME_DB_USER=nombre_usuario_runtime
DATABASE_URL=postgresql+asyncpg://USUARIO:CONTRASENA@host.docker.internal:5432/nomoni
MIGRATION_DATABASE_URL=postgresql+asyncpg://USUARIO:CONTRASENA@host.docker.internal:5432/nomoni
```

`APP_RUNTIME_DB_USER` debe ser el nombre del usuario runtime tal cual lo crees
en Postgres en el paso siguiente (las migraciones le otorgan sus permisos por
nombre).
```

Son dos cuentas de base de datos distintas: `DATABASE_URL` la usa la API y solo puede leer/escribir datos; `MIGRATION_DATABASE_URL` la usan las migraciones y es dueña de la base de datos. Crea ambos en Postgres y asigna la base al segundo:

```sql
CREATE ROLE nombre_usuario_runtime LOGIN PASSWORD '...';
CREATE ROLE nombre_migraciones LOGIN PASSWORD '...';
ALTER DATABASE nomoni OWNER TO nombre_migraciones;
```

La base de datos `nomoni` debe existir de antemano, sin tablas (las migraciones nunca la crean). En Windows y Mac con Docker Desktop la dirección desde el contenedor es `host.docker.internal`; en un Linux sin Desktop agrega esto al servicio `api` del compose:

```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Después levanta el backend y aplica las migraciones:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Es todo. La migración de seed deja dos usuarios listos: `system@nomoni.com` (dueño del catálogo base) y `sergio@hotmail.com`, ambos con la contraseña `12345678`.

Con el backend corriendo en `http://localhost:8000`, arranca el frontend:

```bash
cd front/web
npm install
npm run dev
```

y abre http://localhost:9000.

## Uso

Entra con cualquiera de los usuarios del seed o registra una cuenta nueva (registros nuevos empiezan con las categorías y monederos del catálogo base).

Dentro: escribe un monto y guarda. Si no eliges categoría o monedero, el gasto queda como "pendiente de clasificar" y puedes resolverlo después desde la lista. El dashboard muestra el total del mes, el saldo de tus monederos y lo que falta por clasificar.
