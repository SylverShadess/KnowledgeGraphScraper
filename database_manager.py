from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from psycopg2 import sql

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entities'
    
    entID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)

class Relationship(Base):
    __tablename__ = 'relationships'
    
    relationshipID = Column(Integer, primary_key=True, autoincrement=True)
    sourceID = Column(Integer, ForeignKey('entities.entID'), nullable=False)
    targetID = Column(Integer, ForeignKey('entities.entID'), nullable=False)
    typeID = Column(Integer, ForeignKey('relationship_types.typeID'), nullable=False)

class RelationshipType(Base):
    __tablename__ = 'relationship_types'
    
    typeID = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(255), nullable=False)

class Attribute(Base):
    __tablename__ = 'attributes'
    
    attributeID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    entityID = Column(Integer, ForeignKey('entities.entID'), nullable=False)

class Text(Base):
    __tablename__ = 'text'
    
    textID = Column(Integer, primary_key=True, autoincrement=True)
    body = Column(Text, nullable=False)  # Storing the HTML body as text


class DatabaseManager:
    def __init__(self, connection_string=None):
        load_dotenv()
        """Initialize the database manager with the database name and connection parameters."""
        if connection_string is None:
            connection_string = os.getenv('DATABASE_URL')
        
        if not connection_string:
            raise ValueError("DATABASE_URL is not set in the environment variables.")

        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def close_db(self):
        """Close the connection to the PostgreSQL database."""
        self.session.close()

    def create_tables(self):
        """Create the necessary tables in the database."""
        Base.metadata.create_all(self.engine)

    def search_entities(self, entityID: int=None, name: str=None, type: str=None):
        """Search for entities by name or type."""
        query = self.session.query(Entity)
        if entityID:
            query = query.filter(Entity.entID == entityID)
        if name:
            query = query.filter(Entity.name.ilike(f'%{name}%'))
        if type:
            query = query.filter(Entity.type.ilike(f'%{type}%'))
        return query.all()

    def add_entity(self, name, type):
        """Add a new entity to the entities table."""
        entity = Entity(name=name, type=type)
        self.session.add(entity)
        self.session.commit()
        print(f"Entity added with ID: {entity.entID}")

    def delete_entity(self, entID):
        """Delete an entity from the entities table."""
        entity = self.session.query(Entity).filter_by(entID=entID).first()
        if entity:
            self.session.delete(entity)
            self.session.commit()
            print(f"Entity with ID {entID} deleted.")

    def edit_entity(self, entID, new_name, new_type):
        """Edit an existing entity in the entities table."""
        entity = self.session.query(Entity).filter_by(entID=entID).first()
        if entity:
            entity.name = new_name
            entity.type = new_type
            self.session.commit()
            print(f"Entity with ID {entID} updated.")

    # Relationship methods
    def add_relationship(self, sourceID, targetID, typeID):
        relationship = Relationship(sourceID=sourceID, targetID=targetID, typeID=typeID)
        self.session.add(relationship)
        self.session.commit()

    def delete_relationship(self, relationshipID):
        relationship = self.session.query(Relationship).filter_by(relationshipID=relationshipID).first()
        if relationship:
            self.session.delete(relationship)
            self.session.commit()

    def edit_relationship(self, relationshipID, sourceID=None, targetID=None, typeID=None):
        relationship = self.session.query(Relationship).filter_by(relationshipID=relationshipID).first()
        if relationship:
            if sourceID:
                relationship.sourceID = sourceID
            if targetID:
                relationship.targetID = targetID
            if typeID:
                relationship.typeID = typeID
            self.session.commit()

    def search_relationships(self, relationshipID=None, sourceID=None, targetID=None, typeID=None):
        query = self.session.query(Relationship)
        if relationshipID:
            query = query.filter(Relationship.relationshipID == sourceID)
        if sourceID:
            query = query.filter(Relationship.sourceID == sourceID)
        if targetID:
            query = query.filter(Relationship.targetID == targetID)
        if typeID:
            query = query.filter(Relationship.typeID == typeID)
        return query.all()

    # RelationshipType methods
    def add_relationship_type(self, type_name):
        new_type = RelationshipType(type_name=type_name)
        self.session.add(new_type)
        self.session.commit()

    def delete_relationship_type(self, typeID):
        relationship_type = self.session.query(RelationshipType).filter_by(typeID=typeID).first()
        if relationship_type:
            self.session.delete(relationship_type)
            self.session.commit()

    def edit_relationship_type(self, typeID, type_name=None):
        relationship_type = self.session.query(RelationshipType).filter_by(typeID=typeID).first()
        if relationship_type:
            if type_name:
                relationship_type.type_name = type_name
            self.session.commit()

    def search_relationship_types(self, type_name=None, typeID=None):
        query = self.session.query(RelationshipType)
        if type_name:
            query = query.filter(RelationshipType.type_name.like(f'%{type_name}%'))
        if typeID:
            query = query.filter(RelationshipType.typeID == typeID)
        return query.all()

    # Attribute methods
    def add_attribute(self, name, value, entityID):
        new_attribute = Attribute(name=name, value=value, entityID=entityID)
        self.session.add(new_attribute)
        self.session.commit()

    def delete_attribute(self, attributeID):
        attribute = self.session.query(Attribute).filter_by(attributeID=attributeID).first()
        if attribute:
            self.session.delete(attribute)
            self.session.commit()

    def edit_attribute(self, attributeID, name=None, value=None):
        attribute = self.session.query(Attribute).filter_by(attributeID=attributeID).first()
        if attribute:
            if name:
                attribute.name = name
            if value:
                attribute.value = value
            self.session.commit()

    def search_attributes(self, name=None, entityID=None):
        query = self.session.query(Attribute)
        if name:
            query = query.filter(Attribute.name.like(f'%{name}%'))
        if entityID:
            query = query.filter(Attribute.entityID == entityID)
        return query.all()

    # Text methods
    def add_text(self, body):
        """Add a new text entry to the text table."""
        new_text = Text(body=body)
        self.session.add(new_text)
        self.session.commit()
        print(f"Text added with ID: {new_text.textID}")

    def delete_text(self, textID: int=None, textBody: str=None):
        """Delete a text entry from the text table."""
        text_entry = None
        if textBody:
            text_entry = self.session.query(Text).filter(Text.body == textBody)
        if textID:
            text_entry = self.session.query(Text).filter_by(textID=textID).first()
        if text_entry != None:
            text_entry.delete()
            self.session.commit()
            print("Text deleted.")

    def edit_text(self, textID, new_body):
        """Edit an existing text entry in the text table."""
        text_entry = self.session.query(Text).filter_by(textID=textID).first()
        if text_entry:
            text_entry.body = new_body
            self.session.commit()
            print(f"Text with ID {textID} updated.")
        
    
    def load_text(self, text: str=None, offset: int=None, limit: int=None):
        query = self.session.query(Text)
        if text:
            query = query.filter(Text.body == (f'%{text}%'))
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()