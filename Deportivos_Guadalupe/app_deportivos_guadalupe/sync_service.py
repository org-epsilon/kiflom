import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.db import connections, DatabaseError
from .models import Vehiculo, ImagenVehiculo, RegistroAuditoria

logger = logging.getLogger(__name__)


def get_mongo_collection():
    """
    Retorna la colección 'vehiculos' de MongoDB si MONGODB_URI está configurado.
    Retorna None si no está disponible o falla la conexión.
    """
    uri = getattr(settings, 'MONGODB_URI', '')
    if not uri:
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        db_name = getattr(settings, 'MONGODB_NAME', 'deportivos_guadalupe')
        db = client[db_name]
        return db['vehiculos']
    except Exception as err:
        logger.warning(f"No se pudo conectar a MongoDB: {err}")
        return None


def serialize_vehicle(vehicle: Vehiculo) -> Dict[str, Any]:
    """Convierte una instancia de Vehiculo en un diccionario completo serializable."""
    imagenes = [img.url for img in vehicle.imagenes.all().order_by('orden', 'id') if img.url]
    return {
        'uuid': str(vehicle.uuid),
        'marca': vehicle.marca,
        'modelo': vehicle.modelo,
        'precio': float(vehicle.precio),
        'anio': vehicle.anio,
        'stock': vehicle.stock,
        'imagen_archivo': vehicle.imagen_archivo.url if vehicle.imagen_archivo else '',
        'imagen_url': vehicle.imagen_url or '',
        'modelo_3d_archivo': vehicle.modelo_3d_archivo.url if vehicle.modelo_3d_archivo else '',
        'modelo_3d_url': vehicle.modelo_3d_url or '',
        'modelo_3d_embed_html': vehicle.modelo_3d_embed_html or '',
        'combustible': vehicle.combustible or '',
        'motor': vehicle.motor or '',
        'transmision': vehicle.transmision or '',
        'potencia': vehicle.potencia or '',
        'traccion': vehicle.traccion or '',
        'carroceria': vehicle.carroceria or '',
        'sillas': vehicle.sillas,
        'puertas': vehicle.puertas,
        'descripcion': vehicle.descripcion or '',
        'disponible': vehicle.disponible,
        'imagenes': imagenes,
        'fecha_publicacion': vehicle.fecha_publicacion.isoformat() if vehicle.fecha_publicacion else None,
        'fecha_actualizacion': vehicle.fecha_actualizacion.isoformat() if vehicle.fecha_actualizacion else None,
    }


def get_database_status() -> Dict[str, Dict[str, Any]]:
    """
    Verifica qué motores de base de datos están configurados y accesibles.
    """
    status = {
        'default': {
            'name': 'SQLite (Local)',
            'icon': '💾',
            'configured': True,
            'online': True,
            'badge': 'sqlite',
        },
        'postgres': {
            'name': 'PostgreSQL (Neon)',
            'icon': '🐘',
            'configured': 'postgres' in settings.DATABASES,
            'online': False,
            'badge': 'postgres',
        },
        'mysql': {
            'name': 'MySQL (Aiven)',
            'icon': '🐬',
            'configured': 'mysql' in settings.DATABASES,
            'online': False,
            'badge': 'mysql',
        },
        'mongodb': {
            'name': 'MongoDB (Atlas)',
            'icon': '🍃',
            'configured': bool(getattr(settings, 'MONGODB_URI', '')),
            'online': False,
            'badge': 'mongodb',
        },
    }

    # Probar conexión PostgreSQL
    if status['postgres']['configured']:
        try:
            with connections['postgres'].cursor() as cursor:
                cursor.execute('SELECT 1;')
                status['postgres']['online'] = True
        except Exception:
            status['postgres']['online'] = False

    # Probar conexión MySQL
    if status['mysql']['configured']:
        try:
            with connections['mysql'].cursor() as cursor:
                cursor.execute('SELECT 1;')
                status['mysql']['online'] = True
        except Exception:
            status['mysql']['online'] = False

    # Probar conexión MongoDB
    if status['mongodb']['configured']:
        try:
            col = get_mongo_collection()
            if col is not None:
                col.database.command('ping')
                status['mongodb']['online'] = True
        except Exception:
            status['mongodb']['online'] = False

    return status


def sync_vehicle_to_relational_db(vehicle: Vehiculo, db_alias: str) -> bool:
    """Sincroniza un vehículo y sus imágenes a una base de datos relacional (postgres o mysql)."""
    if db_alias not in settings.DATABASES:
        return False

    try:
        # Upsert Vehiculo por UUID
        existing = Vehiculo.objects.using(db_alias).filter(uuid=vehicle.uuid).first()
        if existing:
            target_veh = existing
        else:
            target_veh = Vehiculo(uuid=vehicle.uuid)

        target_veh.marca = vehicle.marca
        target_veh.modelo = vehicle.modelo
        target_veh.precio = vehicle.precio
        target_veh.anio = vehicle.anio
        target_veh.stock = vehicle.stock
        target_veh.imagen_archivo = vehicle.imagen_archivo
        target_veh.imagen_url = vehicle.imagen_url
        target_veh.modelo_3d_archivo = vehicle.modelo_3d_archivo
        target_veh.modelo_3d_url = vehicle.modelo_3d_url
        target_veh.modelo_3d_embed_html = vehicle.modelo_3d_embed_html
        target_veh.combustible = vehicle.combustible
        target_veh.motor = vehicle.motor
        target_veh.transmision = vehicle.transmision
        target_veh.potencia = vehicle.potencia
        target_veh.traccion = vehicle.traccion
        target_veh.carroceria = vehicle.carroceria
        target_veh.sillas = vehicle.sillas
        target_veh.puertas = vehicle.puertas
        target_veh.descripcion = vehicle.descripcion
        target_veh.disponible = vehicle.disponible
        target_veh.save(using=db_alias)

        # Sincronizar imágenes adicionales
        ImagenVehiculo.objects.using(db_alias).filter(vehiculo=target_veh).delete()
        for img in vehicle.imagenes.all().order_by('orden', 'id'):
            ImagenVehiculo.objects.using(db_alias).create(
                vehiculo=target_veh,
                url=img.url,
                orden=img.orden
            )
        return True
    except Exception as err:
        logger.error(f"Error sincronizando vehículo {vehicle.id} a {db_alias}: {err}")
        return False


def sync_vehicle_to_mongo(vehicle: Vehiculo) -> bool:
    """Sincroniza un vehículo y sus imágenes a MongoDB Atlas como documento JSON."""
    col = get_mongo_collection()
    if col is None:
        return False
    try:
        doc = serialize_vehicle(vehicle)
        col.update_one({'uuid': str(vehicle.uuid)}, {'$set': doc}, upsert=True)
        return True
    except Exception as err:
        logger.error(f"Error sincronizando vehículo {vehicle.id} a MongoDB: {err}")
        return False


def replicate_vehicle_to_all(vehicle: Vehiculo, accion: str = 'SINCRONIZAR') -> Dict[str, bool]:
    """
    Sincroniza un vehículo a TODOS los motores disponibles (Postgres, MySQL, Mongo).
    Registra el evento en RegistroAuditoria.
    """
    results = {}

    # Sincronizar a PostgreSQL si está configurado
    if 'postgres' in settings.DATABASES:
        results['PostgreSQL (Neon)'] = sync_vehicle_to_relational_db(vehicle, 'postgres')

    # Sincronizar a MySQL si está configurado
    if 'mysql' in settings.DATABASES:
        results['MySQL (Aiven)'] = sync_vehicle_to_relational_db(vehicle, 'mysql')

    # Sincronizar a MongoDB si está configurado
    if getattr(settings, 'MONGODB_URI', ''):
        results['MongoDB (Atlas)'] = sync_vehicle_to_mongo(vehicle)

    # Determinar estado de auditoría
    exitosos = [k for k, v in results.items() if v]
    fallidos = [k for k, v in results.items() if not v]

    if not results:
        estado = 'LOCAL_SOLO'
        detalles = 'No hay bases de datos remotas configuradas en .env. Guardado en SQLite.'
    elif not fallidos:
        estado = 'EXITOSO'
        detalles = f"Replicado con éxito en: {', '.join(exitosos)}"
    elif exitosos:
        estado = 'PARCIAL'
        detalles = f"Éxito: {', '.join(exitosos)} | Fallos: {', '.join(fallidos)}"
    else:
        estado = 'ERROR'
        detalles = f"Fallaron todos los motores remotos: {', '.join(fallidos)}"

    RegistroAuditoria.objects.create(
        accion=accion,
        vehiculo_uuid=str(vehicle.uuid),
        vehiculo_nombre=f"{vehicle.marca} {vehicle.modelo}",
        motor_origen='SQLite (Local)',
        motor_destino='Todas las bases de datos',
        estado=estado,
        detalles=detalles,
    )

    return results


def save_vehicle_with_route(vehicle: Vehiculo, target_engine: str, action: str = 'CREAR') -> Dict[str, Any]:
    """
    Maneja el guardado de un vehículo según la opción elegida por el usuario:
    'default' (solo SQLite), 'postgres', 'mysql', 'mongodb' o 'all' (Sincronización total).
    """
    vehicle.save(using='default')

    engine_names = {
        'default': 'SQLite (Local)',
        'postgres': 'PostgreSQL (Neon)',
        'mysql': 'MySQL (Aiven)',
        'mongodb': 'MongoDB (Atlas)',
        'all': 'Todas las bases de datos (Sync)',
    }

    nombre_destino = engine_names.get(target_engine, 'SQLite (Local)')

    if target_engine == 'all':
        replicate_results = replicate_vehicle_to_all(vehicle, accion=action)
        return {'status': 'success', 'engine': nombre_destino, 'results': replicate_results}

    if target_engine == 'default':
        RegistroAuditoria.objects.create(
            accion=action,
            vehiculo_uuid=str(vehicle.uuid),
            vehiculo_nombre=f"{vehicle.marca} {vehicle.modelo}",
            motor_origen='SQLite (Local)',
            motor_destino='SQLite (Local)',
            estado='EXITOSO',
            detalles=f"Operación {action} guardada en base de datos local SQLite.",
        )
        return {'status': 'success', 'engine': nombre_destino}

    success = False
    if target_engine == 'postgres':
        success = sync_vehicle_to_relational_db(vehicle, 'postgres')
    elif target_engine == 'mysql':
        success = sync_vehicle_to_relational_db(vehicle, 'mysql')
    elif target_engine == 'mongodb':
        success = sync_vehicle_to_mongo(vehicle)

    if success:
        detalles = f"Operación {action} guardada en SQLite y sincronizada con éxito en {nombre_destino}."
    else:
        detalles = f"Operación {action} guardada en SQLite, pero {nombre_destino} no está conectado o no se configuró en .env."

    RegistroAuditoria.objects.create(
        accion=action,
        vehiculo_uuid=str(vehicle.uuid),
        vehiculo_nombre=f"{vehicle.marca} {vehicle.modelo}",
        motor_origen='SQLite (Local)',
        motor_destino=nombre_destino,
        estado='EXITOSO' if success else 'ERROR',
        detalles=detalles,
    )

    return {'status': 'success' if success else 'error', 'engine': nombre_destino}
