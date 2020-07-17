import logging
logging.basicConfig(level=logging.INFO)
import subprocess


logger = logging.getLogger(__name__)
#sites_uidspip  = ['Linio']
sites_uidspip  = ['Linio', 'MercadoLibre','Alkosto']


def main():
    _extract()
    _transform()
    _load()


def _extract():
    logger.info('Starting extract process')
    for site_uid in sites_uidspip :
          # cwd--> que ejecute lo que he exrito antes dentro de la dirección que le mando
        subprocess.run(["python", "main.py", site_uid], cwd=".\\extract")
        # ahora vamos a mover los archivos que se generaron
        # "." --> que queremos que comience a partir de este directorio
        # "-name", "{}*" --> queremos que encuentre algo con un cierto patrón (* el asterisco significa con lo que sea)
        # "-exect" --> que ejecute algo por cada uno de los archivos que encuentre
        # "mv" --> que los mueva
        # "{}" --> el nombre del archivo
        # ";" --> porque find nos obliga a terminar con un ;
        # el siguiente comando es para linux o mac
        # subprocess.run(["find", ".", "-name", "{}*".format(news_sites_uid), "-exec", "mv", "{}",
        #                "../transform/{}_.csv".format(news_sites_uid), ";"], cwd="./extract")
        # Para windwos
        subprocess.run(["copy", "{}_*".format(site_uid),
                        "..\\transform\\{}.csv".format(site_uid)], shell=True,
                       cwd="./extract")


def _transform():
    logger.info('Starting transform process')
    for site_uid in sites_uidspip :
        dirty_data_filename = "{}.csv".format(site_uid)
        clean_data_filename = "cleaned_{}.csv".format(dirty_data_filename[:-4])
        
        subprocess.run(["python", "main.py", dirty_data_filename], cwd=".\\transform")
        subprocess.run(["rm", dirty_data_filename], shell=True, cwd="./transform")
        subprocess.run(["mv", clean_data_filename,"..\\load\\{}.csv".format(site_uid)], shell=True,
                       cwd="./transform")



def _load():
    logger.info("Starting load process")
    for site_uid in sites_uidspip :
        clean_data_filename = "{}.csv".format(site_uid)
        subprocess.run(["python", "main.py", clean_data_filename], cwd=".\\load")
        #subprocess.run(["rm", clean_data_filename], shell=True, cwd="./load")
    print("*" * 50)



if __name__ == '__main__':
    main()
