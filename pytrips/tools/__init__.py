try:
    import en_core_web_lg as nlp
    nlp = nlp.load()
except ImportError:
    raise ImportError("Install pytrips[tools]")
