import pyinotify
import monitor_config
import imp
import logging
import os
from sugar import ErrorSugar


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("monitor")

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE  # watched events

class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        logger.debug("Ingreso al manejador del evento")
        
        # Primero identifico el codigo que debo llamar. Para eso recorro la
        # lista monitor_config.PATHS hasta encontrar un patron coincidente.
        for tupla in monitor_config.PATHS:
            logger.debug(monitor_config.DIR_BASE + tupla[0])
            # Si coincide con el patron ejecuto el codigo apropiado
            if event.pathname.startswith(monitor_config.DIR_BASE + tupla[0]):
                # Tengo que importar el modulo dinamicamente
                i_file, i_filename, i_tuple = imp.find_module(tupla[1],
						monitor_config.PLUGIN_DIRS)
                logger.debug("Cargo el modulo correspondiente")
                modulo = imp.load_module(tupla[1], i_file, i_filename, i_tuple)

                # Habiendo importado el modulo, llamo a la funcion que procesa
                # el archivo, pasando su ruta como parametro
                try:
                    logger.debug("Proceso el archivo " + event.pathname)

                    instancia = modulo.obtener_instancia()
                    modulo.procesar(instancia, event.pathname)
                    
                    # Si funciono correctamente, paso por aca. Tengo que borrar
                    # el archivo
                    logger.debug("Borro el archivo " + event.pathname)
                    os.remove(event.pathname)
                    break
                    
                except ErrorSugar, detalle:
                    # Si paso por aca es porque hubo algun problema con la
                    # importacion.
                    
                    # Doy mensaje de error
                    logger.debug("Error en la importacion. "+ str(detalle))
                    
                    # Muevo el archivo a la carpeta de errores
                    logger.debug(event.pathname)
                    logger.debug(monitor_config.DIR_ERR +
                                event.pathname[len(monitor_config.DIR_BASE):])
                    os.rename(event.pathname, monitor_config.DIR_ERR +
                                event.pathname[len(monitor_config.DIR_BASE):])
                    logger.debug("Archivo movido (por error)")
                    break
                
        else:
            # Aviso que ningun patron coincide
            logger.warning("Ningun patron coincide. Moviendo archivo: " +
                            event.pathname)
            # Muevo el archivo a la carpeta de errores
            logger.debug(event.pathname)
            logger.debug(monitor_config.DIR_ERR +
                            event.pathname[len(monitor_config.DIR_BASE):])
            os.rename(event.pathname, monitor_config.DIR_ERR +
                                event.pathname[len(monitor_config.DIR_BASE):])
            logger.debug("Archivo movido (por patron no coincidente)")

    def process_default(self, event):
        # Para el resto de los eventos no quiero que pase nada.
        pass

notifier = pyinotify.Notifier(wm, HandleEvents())

wdd = wm.add_watch(monitor_config.DIR_BASE, mask, rec=True)
try:
    notifier.loop()
except KeyboardInterrupt:
    wm.rm_watch(wdd.values())
    notifier.stop()

    
