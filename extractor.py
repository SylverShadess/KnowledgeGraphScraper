import ast
# from langchain.chains import LLMChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

class Extractor:
    def __init__(self,  model_name: str = "gemma3:4b", base_url: str = "http://192.168.1.76:11434"):
        self.model_name = model_name
        self.base_url = base_url

        self.llm = OllamaLLM(base_url=base_url, model=model_name)

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        # Define extraction prompts
        self.entity_extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            ONLY RETURN THE RESULT OF THE EXTRACTION IN THE FORMAT [("entity name", "entity type")]
            You are an entity extractor. Your task is to identify and extract ALL possible entities from the provided text.
            Extract ANY noun or named entity that appears in the text, being as inclusive as possible.

            First, try to categorize entities into these common types:
            - Person: Any individuals or groups of people, including generic references (e.g., "John Smith", "Dr. Johnson", "teachers", "customers")
            - Organization: Any companies, institutions, groups (e.g., "Apple Inc.", "United Nations", "team", "committee")
            - Location: Any physical places or areas (e.g., "New York", "Mount Everest", "office", "kitchen")
            - Concept: Any ideas, theories, fields, attributes or abstract nouns (e.g., "democracy", "physics", "happiness", "speed")
            - Event: Any occurrences, happenings, or activities (e.g., "World War II", "meeting", "conference", "celebration")
            - Product: Any items, services, or creations (e.g., "iPhone", "books", "software", "table")

            If an entity doesn't fit into one of these categories, you may assign it Miscellaneous.

            For each entity:
            1. Identify ANY noun or named entity in the text, including general categories
            2. First try to assign one of the common entity types
            3. If it doesn't fit, assign Miscellaneous
            4. Be consistent with entity types across similar entities
            5. If an entity has multiple words, it cannot include a verb or verb phase (only nouns)

            RETURN ONLY a valid Python list, no explanations or other text. Use exactly this format:
            [("entity name", "entity type")]

            Separate entities by a comma as they would in a normal Python list

            If no entities can be extracted, return an empty array: []

            Text to analyze:
            {text}
            """
        )

        self.relationship_extraction_prompt = PromptTemplate(
            input_variables=["text", "entities"],
            template="""
            DO NOT COMMENT ABOUT THE LENGTH/SIZE OF THE TEXT. ONLY RETURN THE RESULT OF THE EXTRACTION
            You are a relationship extractor. Your task is to identify ALL possible relationships between entities in the provided text.
            Extract any relationships that might exist between the entities, explicit or implicit.

            Entities detected in the text:
            {entities}

            For each relationship:
            1. Consider ANY possible logical connection between ANY two entities in the list
            2. Use a broad interpretation to identify relationships between entities
            3. Describe the relationship with a short, specific predicate that accurately captures the connection
            4. Be precise with relationship descriptions - use terms that best describes the relationship
            5. Try to be consistent with relationship types for similar relationships
            6. Each and every pair of entities must be checked for a relationship
            7. Use the web to help properly determine the connection between each pair of entities

            RETURN ONLY a valid Python list as plain text, no explanations or other text. Use exactly this format and only three values in the tuple:
            [("source entity", "relationship type", "target entity")]

            where "source entity" is the active doer of the relationship and "target entity" is the receiver
            "relationship type" should be verbs that indicate an action like "helps", "depends_on", "is_a" or anything else you can come up with 

            Do not enclose result in ```python ```. Only return plain text

            If no relationships can be extracted, return an empty string: ""

            Text to analyze:
            {text}

            DO NOT COMMENT ABOUT THE LENGTH/SIZE OF THE TEXT. ONLY RETURN THE RESULT OF THE EXTRACTION
            """
        )

        # self.entity_chain = LLMChain(llm=self.llm, prompt=self.entity_extraction_prompt)
        # self.relationship_chain = LLMChain(llm=self.llm, prompt=self.relationship_extraction_prompt)
        # 1.0 Implementation
        self.entity_chain = self.entity_extraction_prompt | self.llm
        self.relationship_chain = self.relationship_extraction_prompt | self.llm

    def extract_entities(self, text: list) -> list:
        #Extract entities from text using LLM
        if not text or len(text[0]) < 10:
            return []
        
        result = self.entity_chain.invoke({"text": text})

        # print("\n\nEntities Result: "+str(result))

        #Make sure it's a list
        if isinstance(result, dict) and "text" in result:
            response = ast.literal_eval(result.get("text", ""))
        elif isinstance(result, str):
            response = self._custom_parser(result)
        elif isinstance(result, list):
            response = result
        else:
            return []

        if not response:
            return []

        #Validate entities
        valid_entities = []
        seen_entities = set()
    
        for entity in response:
            name = entity[0].strip().lower()
            type = entity[1].strip().lower()
        
            # Skip if incomplete
            if not name or not type:
                continue

            #Check if this entity is not already passed
            if name not in seen_entities:
                seen_entities.add(name)
                valid_entities.append((name, type))

        if not valid_entities:
            return []

        return valid_entities

    def extract_relationships(self, text: str, entities: list) -> list:
        #Extract relationships from text using LLM
        if not entities or len(entities) < 2:
            return []

        valid_entity_names = [entity[0].lower() for entity in entities]
        
        result = self.relationship_chain.invoke({"text": text, "entities": valid_entity_names})

        #Make sure it's a list
        if isinstance(result, dict) and "text" in result:
            response = ast.literal_eval(result.get("text", ""))
        elif isinstance(result, str):
            response = self._custom_parser(result)  
        elif isinstance(result, list):
            response = result
        else:
            return []

        if not response:
            return []
        
        # Validate relationships
        valid_relationships = []
        seen_relationships = set()

        for relationship in response:
            source = relationship[0].strip().lower()    
            target = relationship[2].strip().lower()
            type = ''
        
            if source in valid_entity_names and target in valid_entity_names:
                type = relationship[1].strip().lower()
            

            # To deal with LLM producing more than 3 values
            # if len(relationship) > 3:
            #     if relationship[3] in valid_entity_names and not relationship[2] in valid_entity_names:
            #         target = relationship[3]


            # Create a unique key for this relationship to avoid duplicates
            rel_key = f"{source}|{type}|{target}"

            if rel_key not in seen_relationships and type != '':
                seen_relationships.add(rel_key)
                valid_relationships.append((source,target,type))

        if not valid_relationships:
            return []
        
        return valid_relationships
    
    def _custom_parser(self, input_str):
        try:
            retval = ast.literal_eval(input_str)
            return retval
        except:
            # Remove leading and trailing whitespace
            input_str = input_str.strip()
            
            # Remove leading and trailing brackets if present
            if input_str.startswith('[') and input_str.endswith(']'):
                input_str = input_str[1:-1].strip()
            
            # Split the string by commas to get potential list elements
            elements = input_str.split(',')
            
            # Process each element to handle unclosed string literals
            processed_elements = []
            for element in elements:
                element = element.strip()
                if element.startswith("'") and not element.endswith("'"):
                    element += "'"
                elif element.startswith('"') and not element.endswith('"'):
                    element += '"'
                processed_elements.append(element)
            
            return processed_elements