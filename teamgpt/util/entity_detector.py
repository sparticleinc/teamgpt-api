import uuid
import re


# import en_core_web_trf
# import zh_core_web_trf
# import ja_core_news_trf
#
# nlpENTRF = en_core_web_trf.load()
# nlpZHTRF = zh_core_web_trf.load()
# nlpJATRF = ja_core_news_trf.load()


def is_contain_chinese(string):
    """判断字符串是否包含中文字符集"""
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return pattern.search(string) is not None


def is_contain_japanese(string):
    """判断字符串是否包含日文字符集"""
    pattern = re.compile(r'[\u3040-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF]')
    return pattern.search(string) is not None


def nlp(txt: str):
    if is_contain_chinese(txt) is True:
        return nlpZHTRF(txt)
    elif is_contain_japanese(txt) is True:
        return nlpJATRF(txt)
    else:
        return nlpENTRF(txt)


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
            if (ent.text in self.entity_registry_names):
                continue
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
            item_uuid = '☀' + str(uuid.uuid4()) + '☀'
            # Add the mapped item to the dictionary
            self.entity_name_map[item_uuid] = item_name
            self.entity_type_map[item_uuid] = item_type
            self.full_uuid_map[item_name] = item_uuid
            # + \ " ( " + item_type + " ) "

    def redact(self, content: str):

        for entity, uuidstr in self.full_uuid_map.items():
            pattern = re.compile(
                r'(?<!☀)[^☀\n]*(?:\n[^☀\n]*)*(?![^☀\n]*☀)')

            # 定义替换函数

            def replace(match):
                return match.group().replace(entity, uuidstr)

            content = re.sub(pattern, replace, content)
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
