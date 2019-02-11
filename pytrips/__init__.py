import logging
logging.getLogger("pytrips")
logging.basicConfig(
    format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


from .ontology import load
