import logging
logging.getLogger("pytrips")
logging.basicConfig(
    format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


from .ontology import load


__VERSION__ = "0.5.20"
