from numpy import typename
from sqlalchemy import false
from extractor import Extractor
from knowledge_graph import KnowledgeGrapher
from scraper import Scraper
from database_manager import DatabaseManager

scraper = Scraper()
extractor = Extractor()
db_manager = DatabaseManager()

url = "https://www.w3schools.com/python/python_intro.asp"
# url = "https://stackoverflow.com/questions/70927568/downloading-images-with-selenium-and-requests-why-does-the-get-attribute-met/70962929#70962929"
search_term = "Python"

text = scraper.scrape(url, search_term)
# print("\n\nText: "+str(text))

for instance in text:
    if not db_manager.load_text(text=instance):
        if not instance == '' or not instance == ' ':
            db_manager.add_text(instance)

text_count = 400
text = [textval.body for textval in db_manager.load_text(limit=text_count)]

entities = extractor.extract_entities(text)

for entity in entities:
    if not db_manager.search_entities(name=entity[0], type=entity[1]):
        db_manager.add_entity(entity[0], entity[1])

for val in text:
    db_manager.delete_text(textBody=val)
# print("\n\nEntities: "+str(entities))

relationships = extractor.extract_relationships(text, entities)
for relationship in relationships:
    sourceID = db_manager.search_entities(name=relationship[0])[0].entID
    targetID = db_manager.search_entities(name=relationship[1])[0].entID
    sourceFound = True if len(db_manager.search_relationships(sourceID=sourceID)) > 0 else False
    targetFound = True if len(db_manager.search_relationships(targetID=targetID)) > 0 else False

    # if sourceFound and targetFound:
    #     continue
    
    relationship_type = db_manager.search_relationship_types(type_name=relationship[2])
    if relationship_type:
        relationshipID = relationship_type[0].typeID
    else:
        db_manager.add_relationship_type(relationship[2])
        relationshipID = db_manager.search_relationship_types(type_name=relationship[2])[0].typeID
    
    db_manager.add_relationship(sourceID, targetID, relationshipID)


knowledge_grapher = KnowledgeGrapher()
knowledge_grapher.populate_graph(db_manager.search_entities(), db_manager.search_relationships())
db_manager.close_db()
knowledge_grapher.draw_graph()