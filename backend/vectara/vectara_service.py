import requests
import json
import os

def upload_data_to_vectara(document_list):
    """
    Uploads data to Vectara for indexing.
    Each document in the list is expected to be a dict with necessary fields.
    """
    api_endpoint = "https://api.vectara.io/v1/index"
    headers = {
        "x-api-key": os.environ['VECTARA_API_KEY'],
        "customer-id": os.environ['VECTARA_CUSTOMER_ID'],
        "Content-Type": "application/json",
    }

    session = requests.Session()
    for document in document_list:
        payload = {
            "customerId": os.environ['VECTARA_CUSTOMER_ID'],
            "corpusId": os.environ['VECTARA_CORPUS_ID'],
            "document": document
        }

        response = session.post(api_endpoint, headers=headers, data=json.dumps(payload), timeout=250, verify=True)
        if response.status_code != 200:
            print(f"Error uploading document ID {document['documentId']}: {response.text}")
        else:
            print(f"Document ID {document['documentId']} uploaded successfully.")

def index_documents_vectara():
    """
    Function to index documents into Vectara.
    This is more of a conceptual step, assuming documents are indexed upon upload.
    Call upload_data_to_vectara with your documents here.
    """
    # Example document list
    document_list = [
        {
            "documentId": "doc1",
            "title": "Sample Document",
            "content": "This is a sample document for indexing in Vectara."
        },
        # Add more documents as needed
    ]
    upload_data_to_vectara(document_list)

def query_vectara(query):
    """
    Queries Vectara with the provided query string and returns the results.
    """
    api_endpoint = f"https://api.vectara.io/v1/query"
    headers = {
        "x-api-key": os.environ['VECTARA_API_KEY'],
        "customer-id": os.environ['VECTARA_CUSTOMER_ID'],
        "Content-Type": "application/json",
    }

    payload = {
        "customerId": os.environ['VECTARA_CUSTOMER_ID'],
        "corpusId": os.environ['VECTARA_CORPUS_ID'],
        "query": query,
        "page": 1,
        "pageSize": 10
    }

    response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload), timeout=250, verify=True)
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Error querying Vectara: {response.text}")
        return []

# Example usage of the indexing function
# index_documents_vectara()

# Example query
# results = query_vectara("Example query")
# print(results)
