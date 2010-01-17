import pyinotify
import monitor_config
import imp
import logging


# Configuro el logging
logging.basicConfig(level=logging.eval('WARNING'))

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE  # watched events

class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        
        # Primero identifico el codigo que debo llamar. Para eso recorro la
        # lista monitor_config.PATHS hasta encontrar un patron coincidente.
        for tupla in monitor_config.PATHS:
            # Si coincide con el patron ejecuto el codigo apropiado
            if event.pathname.startswith(monitor_config.DIR_BASE + tupla[0]):
                # Tengo que importar el modulo dinamicamente
                i_file, i_filename, i_tuple = 
                    imp.find_module(tupla[1], monitor_config.PLUGIN_DIRS)
                modulo = imp.load_module(tupla[1], i_file, i_filename, i_tuple)
                
                # Habiendo importado el modulo, llamo a la funcion que procesa
                # el archivo, pasando su ruta como parametro
                modulo.procesar(event.pathname)
                print "Pase por aca"
                break
        else:
            # Aviso que ningun patron coincide
            print "Ningun Patron Coincide"
            
        # Si todo salio bien, borro el archivo, sino, muevo a carpeta de error
        print "Close_write:", event.pathname

    def process_default(self, event):
        pass

notifier = pyinotify.Notifier(wm, HandleEvents())

wdd = wm.add_watch(monitor_config.DIR_BASE, mask, rec=True)
try:
    notifier.loop()
except KeyboardInterrupt:
    wm.rm_watch(wdd.values())
    notifier.stop()


