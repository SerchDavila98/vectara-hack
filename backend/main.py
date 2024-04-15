from flask import Flask, request, jsonify
from config import load_config
from vectara_service import query_vectara
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/generate-response', methods=['POST'])
def generate_response():
    try:
        # Load configuration for Vectara and OpenAI
        config = load_config()
        
        # Extract query from the request
        data = request.get_json()
        vectara_query = data.get('query')
        if not vectara_query:
            return jsonify({"error": "No query provided."}), 400
        
        # Query Vectara
        logging.info(f"Querying Vectara with query: '{vectara_query}'")
        vectara_results = query_vectara(vectara_query, config)
        
        if not vectara_results:
            logging.error("No results returned from Vectara. Check your query or configuration.")
            return jsonify({"error": "No results returned from Vectara."}), 500
        
        # Prepare prompt for OpenAI based on Vectara results
        prompt_for_openai = "Based on the following qualities of great accommodations, generate a summary: " + " ".join(vectara_results)
        
        # Generate response using OpenAI
        openai_response = generate_response_with_openai(prompt_for_openai, config)
        
        return jsonify({"response": openai_response}), 200
    
    except Exception as e:
        logging.exception("An error occurred:", exc_info=e)
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)
