

def main_loop():
    import pyinotify
    import monitor_config
    import imp
    import logging
    import os
    from sugar import ErrorSugar
    import SOAPpy


    # Configuro el logging
    logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
    logger = logging.getLogger("monitor")

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CLOSE_WRITE  # watched events

    class HandleEvents(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            logger.debug("Ingreso al manejador del evento")

            try:
                os.stat(event.pathname)
            except OSError:
                logger.debug("El archivo ya no existe")
                return
            
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

                        contador = 0
                        while True:
                            try:
                                instancia = modulo.obtener_instancia()
                            except SOAPpy.wstools.TimeoutSocket.TimeoutError:
                                contador += 1
                                if contador > 10:
                                    raise
                            else:
                                break

                        modulo.procesar(instancia, event.pathname)
                    
                        # Si funciono correctamente, paso por aca.
                        # Muevo el archivo a la carpeta de exito
                        logger.debug("Exito. Muevo el archivo " + event.pathname)
                        logger.debug(monitor_config.DIR_EXITO +
                                    event.pathname[len(monitor_config.DIR_BASE):])
                        try:
                            os.rename(event.pathname, monitor_config.DIR_EXITO +
                                    event.pathname[len(monitor_config.DIR_BASE):])
                        except OSError:
                            logger.debug("Algun error ocurrio al renombrar")
                        logger.debug("Archivo movido (por exito)")
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
                        logger.debug("Creo hardlink")
                        try:
                            os.link(event.pathname, monitor_config.DIR_ERR +
                                    event.pathname[len(monitor_config.DIR_BASE):])
                        except OSError:
                            logger.debug("El archivo ya existia")
                        logger.debug("Borro original")
                        os.remove(event.pathname)
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
                logger.debug("Creo hardlink")
                try:
                    os.link(event.pathname, monitor_config.DIR_ERR +
                                    event.pathname[len(monitor_config.DIR_BASE):])
                except OSError:
                    logger.debug("El archivo ya existia")
                logger.debug("Borro original")
                os.remove(event.pathname)
                logger.debug("Archivo movido (por patron no coincidente)")

        def process_default(self, event):
            # Para el resto de los eventos no quiero que pase nada.
            pass

    notifier = pyinotify.Notifier(wm, HandleEvents())

    wdd = wm.add_watch(monitor_config.DIR_BASE, mask, rec=True)
    try:
        notifier.loop()
    except KeyboardInterrupt:
        logger.info("Interrumpido")
        wm.rm_watch(wdd.values())
        notifier.stop()
    

if __name__ == '__main__':
    main_loop()

