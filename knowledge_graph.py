import networkx, streamlit
import matplotlib.pyplot as pyplot
from database_manager import DatabaseManager
# import matplotlib.cm as colourmaps
# import matplotlib.colors as mplotcolours

class KnowledgeGrapher:
    def __init__(self):
        self.graph = networkx.Graph()
        self.db_manager = DatabaseManager()
    
    def populate_graph(self, entities: list, relationships: list):
        for entity in entities:
            self.graph.add_node(entity.name, entity_type=entity.type)
        for relationship in relationships:
            self.graph.add_edge(self.db_manager.search_entities(entityID=relationship.sourceID)[0].name, 
                                self.db_manager.search_entities(entityID=relationship.targetID)[0].name, 
                                relationship_type=self.db_manager.search_relationship_types(typeID=relationship.typeID)[0].type_name
                                )
    
    def draw_graph(self):
        pyplot.figure(figsize=(18, 8))

        # Set a fixed layout for consistency, adjust k parameter to spread nodes more
        pos = networkx.spring_layout(self.graph, k=1.5, iterations=100, seed=42)

        entity_types = set()
        for node in self.graph.nodes():
            entity_type = self.graph.nodes[node].get('entity_type')
            if entity_type not in entity_types:
                entity_types.add(entity_type)
        
        # Define a single color for all entity types and relationship types
        single_color = 'black'
        
        # Assign the same color to all nodes
        node_colors = [single_color] * len(self.graph.nodes())
        
        # Increase node size for better visibility
        networkx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=900, alpha=0.8)

        # Assign the same color to all edges
        edge_colors = [single_color] * len(self.graph.edges())
        
        # Improve edge visualization
        networkx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors, width=2, alpha=0.7)

        # Draw edge labels with relationship types - make them smaller and position them better
        edge_labels = networkx.get_edge_attributes(self.graph, 'relationship_type')
        networkx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=7, font_color='darkblue', bbox=dict(facecolor='white', alpha=0.7), rotate=False)
                            
        # Draw node labels with better visibility
        networkx.draw_networkx_labels(self.graph, pos, font_weight='bold', font_size=10, font_color='black', bbox=dict(facecolor='white', alpha=0.7, pad=3))

        # Adjust plot margins to ensure everything fits
        pyplot.tight_layout()
        
        # Turn off axis
        pyplot.axis('off')

        # Add a small margin around the graph
        pyplot.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        streamlit.pyplot(pyplot)
