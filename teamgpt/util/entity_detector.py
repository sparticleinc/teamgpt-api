import uuid
import en_core_web_sm
import zh_core_web_sm
import ja_core_news_sm

nlpEN = en_core_web_sm.load()
nlpZH = zh_core_web_sm.load()
nlpJA = ja_core_news_sm.load()


def nlp(txt):
    if txt:
        if txt[0] <= '\u9fff':
            return nlpZH(txt)
        elif txt[0] <= '\u0fff':
            return nlpJA(txt)
        else:
            return nlpEN(txt)
    else:
        return nlpEN(txt)


class EntityDetector:
    def __init__(self):
        self.entity_registry_names = []
        self.entity_registry_types = []
        self.entity_name_map = {}
        self.entity_type_map = {}
        self.full_uuid_map = {}

    def detect_entities(self, txt):
        # Perform NER detection on some text

        doc = nlp(txt)
        # Iterate over the entities in the document
        for ent in doc.ents:
            # Add the entity to the registry
            self.entity_registry_names.append(ent.text)
            # Access the label of the entity to extract its type
            self.entity_registry_types.append(ent.label_)

        for token in doc:
            if token.like_email and token.text not in self.entity_registry_names:
                self.entity_registry_names.append(token.text)
                self.entity_registry_types.append("EMAIL")

        return (self.entity_registry_names, self.entity_registry_types)

    def map_items(self):
        # Iterate over the items in the entity registry
        for item_name, item_type in zip(self.entity_registry_names, self.entity_registry_types):
            # Map the item to a uuid
            item_uuid = str(uuid.uuid4())
            # Add the mapped item to the dictionary
            self.entity_name_map[item_uuid] = item_name
            self.entity_type_map[item_uuid] = item_type
            self.full_uuid_map[item_name] = item_uuid
            # + \ " ( " + item_type + " ) "

    def redact(self, content: str):

        for entity, uuidstr in self.full_uuid_map.items():
            content = content.replace(entity, uuidstr)
        txtprocess = content
        self.txtprocess = txtprocess
        return txtprocess

    def unredact(self, outputtxt):
        for uuidstr, entity in self.entity_name_map.items():
            outputtxt = outputtxt.replace(uuidstr, entity)
        return outputtxt

    def clear_values(self):
        self.entity_registry_names = []
        self.entity_registry_types = []
        self.entity_name_map = {}
        self.entity_type_map = {}
        self.full_uuid_map = {}
        self.txtprocess = None
