# file: tests/test_entity_processing.py
import unittest
from unittest.mock import patch, MagicMock
# Adjust the import paths according to your project structure
from src.llm_censor.censor_entity_service import extract_entities, censor_sensitive_information, create_vector_db_with_content_and_entities, create_entity_related_memory

class TestEntityProcessing(unittest.TestCase):
    def test_extract_entities(self):
        """Test entity extraction from a given text."""
        test_text = "Elon Musk founded SpaceX, which is based in California."
        expected_entities = [('Elon Musk', 'PERSON'), ('SpaceX', 'ORG'), ('California', 'GPE')]
        extracted_entities = extract_entities(test_text)
        self.assertEqual(sorted(extracted_entities), sorted(expected_entities))

    @patch('src.llm_censor.censor_entity_service.nlp')
    def test_censor_sensitive_information(self, mocked_nlp):
        """Test censoring of sensitive information using mocked NLP model."""
        # Setup mock for Spacy NLP model
        mocked_doc = MagicMock()
        mocked_doc.ents = [MagicMock(text="John Doe", label_="PERSON"), MagicMock(text="New York", label_="GPE")]
        mocked_nlp.return_value = mocked_doc

        test_text = "John Doe lives in New York."
        censored_text, entities = censor_sensitive_information(test_text)
        
        self.assertIn("<NAME>", censored_text)
        self.assertTrue(any(entity[0] == "John Doe" for entity in entities))

    @patch('src.llm_censor.censor_entity_service.create_vector_db_with_content_and_entities')
    def test_create_vector_db_with_content(self, mocked_db_creation):
        """Test vector database creation with censored content and entities."""
        censored_content = "A famous person founded a big company."
        entities = [('a famous person', 'PERSON'), ('a big company', 'ORG')]
        create_vector_db_with_content_and_entities(censored_content, entities)
        
        mocked_db_creation.assert_called_with(censored_content, entities)

    @patch('src.llm_censor.censor_entity_service.VectorStoreIndex')
    @patch('src.llm_censor.censor_entity_service.QdrantVectorStore')
    @patch('src.llm_censor.censor_entity_service.qdrant_client.QdrantClient')
    def test_create_entity_related_memory(self, mocked_client, mocked_vector_store, mocked_index):
        """Test creation of entity-related memory with mocked vector database."""
        entities = [('SpaceX', 'ORG')]
        mock_index_instance = mocked_index.return_value
        mock_index_instance.as_query_engine.return_value.query.return_value = [
            {"content": "SpaceX", "relation": "similar"}
        ]

        entity_memory = create_entity_related_memory(mock_index_instance, entities)
        
        self.assertIn('relationships', entity_memory)
        self.assertEqual(entity_memory['relationships'][0]['entity'], 'SpaceX')

if __name__ == '__main__':
    unittest.main()
