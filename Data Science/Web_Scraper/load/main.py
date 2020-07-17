import argparse
import logging
import pandas as pd
from item import Item
from base import Base, Engine, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    # configurar sql
    Base.metadata.create_all(Engine)  # permite generar nuestro scheme en nuestra base de datos
    session = Session()  # Inicializar la sesión
    items = pd.read_csv(filename)  # Leemos nuestros artículos con pandas

    # iterrows : es un método de pandas que permite generar un loop adentro de cada una de nuestras
    # filas de nuestro DataFrame
    for index, row in items.iterrows():
        logger.info("Loading item uid {} into DB".format(row["uid"]))
        item = Item(row["uid"],
                          row["title"],
                          row["brank"],
                          row["price"],
                          row["color"],
                          row["opinions"],
                          row["average_opinions"],
                          row["raw_description"],
                           row["seller"],
                          row["url"],
                          row["newspaper_uid"],
                          row["n_tokens_title"],
                          row["n_tokens_raw_description"])
                          
        session.add(item)  # esto nos mete nuestro artículo dentro de la base de datos

    session.commit()
    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="The file you want to load into the db",
                        type=str)

    args = parser.parse_args()

    main(args.filename)
