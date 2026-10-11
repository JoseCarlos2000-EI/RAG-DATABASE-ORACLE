from flask import Flask, request, jsonify
from bulk_data import executeBulk
from query_data import askQuestion
from flask_cors import CORS

app = Flask( __name__ )
CORS(app)
@app.route('/bulk-data', methods = ['POST'])
def bulk():

    try:
        executeBulk()

        return jsonify({
            'codigo': '0',
            'mensaje': 'Se realizó con éxito la inserción de la información'
        }), 200
    
    except Exception as e:
        return jsonify({
            'codigo': '1',
            'mensaje': f'Error en el llenado de la información a la BD : { e }',
        }), 500

@app.route('/ask-question', methods = ['POST'])
def question():
    try:
        # TODO: Validar la informacion del usuario
        body = request.get_json( silent = True)

        if not 'question' in body:
            raise Exception('No se identificó la pregunta a la solicitud')

        question = body['question']

        faqs_resolved = askQuestion( question )

        return jsonify({
            'codigo': '0',
            'mensaje': 'Se realizó con éxito la respuesta de la información',
            'data': faqs_resolved
        }), 200

    except Exception as e:
        print(e)
        return jsonify({
            'codigo': '1',
            'mensaje': f'Error en la consulta de la información a la BD : { str(e) }',
        }), 500

if __name__ == '__main__':
    app.run( debug = True)