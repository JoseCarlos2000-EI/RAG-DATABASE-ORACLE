import oracledb as orcl
from sentence_transformers import SentenceTransformer
import array
import json
import requests


usr = 'sys'
pwd = 'admin'
cs = 'localhost:1521/freepdb1'
mode = orcl.SYSDBA

table_name = 'question_form'

connection = orcl.connect( user = usr, password = pwd, dsn = cs, mode = mode)

def askQuestion( query ):
    #query = 'Dime el numero y serie del documento?'

    model = SentenceTransformer('all-MiniLM-L12-v2')

    query_encode = array.array('f', list(model.encode( query, batch_size = 36, show_progress_bar = True )))

    query_faq = f"""
    SELECT
    FAQ, VECTOR_DISTANCE(VECTOR_FAQ, :v, COSINE) SCORE
    FROM {table_name}
    ORDER BY SCORE
    FETCH APPROX FIRST 200 ROWS ONLY;
    """

    with connection.cursor() as db:
        resp = db.execute(query_faq, v = query_encode)
        resp = resp.fetchall()

    resp_score = [ { 'question': json.loads(question.read())['question'], 'score': score}  for  question, score in resp ]

    return resp_score


