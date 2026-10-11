import oracledb as orcl
import os
from sentence_transformers import SentenceTransformer
import json
import array


usr = 'sys'
pwd = 'admin'
cs = 'localhost:1521/freepdb1'
mode = orcl.SYSDBA



connection = orcl.connect( user = usr, password = pwd, dsn = cs, mode = mode)
def executeBulk():
    exts = ['txt', 'csv']
    files = {}

    for file in os.listdir():
        ext = file.split('.')[1] if '.' in file else None
        if ext in exts:
            with open(file, 'r', encoding='utf8') as f:
                content = f.read()
                files[file] = [
                    {
                        'file': file,
                        'source': doc.strip(),
                        'type': ext
                    }
                    for doc in content.split('=======')
                    if doc.strip() != ''
                ]

    model = SentenceTransformer('all-MiniLM-L12-v2')


    arrayEncode = [
        faq['source']
        for file in files
        for faq in files[file]
    ]


    dataEncoded = model.encode(
        arrayEncode,
        batch_size=36,
        show_progress_bar=True
    )


    dataEncoded = [array.array('f', vector) for vector in dataEncoded]

 
    files = [
        {
            'source': faq['source'],
            'file': faq['file'],
            'source_transform': encode,
            'source_type': faq['type']
        }
        for file in files
        for faq, encode in zip(files[file], dataEncoded)
    ]

    table_name = 'question_form'

    query_create = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            QUESTION_ID INTEGER PRIMARY KEY,
            FAQ CLOB CHECK (FAQ IS JSON),
            VECTOR_FAQ VECTOR,
            STATE VARCHAR2(10) DEFAULT 'N',
            CREATION_DATE DATE DEFAULT SYSDATE,
            CREATION_BY VARCHAR2(100) NOT NULL,
            LAST_UPDATE_DATE DATE DEFAULT SYSDATE,
            LAST_UPDATE_BY VARCHAR2(100) NOT NULL
        )
    """

    with connection.cursor() as bd:
        bd.execute(query_create)
        connection.commit()

    # 🔹 NO reconvertir el embedding
    dataPrepare = [
        (
            json.dumps({'question': faq['source']}, ensure_ascii=False),
            faq['source_transform'], 
            'Y',
            'CHATBOT_APP',
            'CHATBOT_APP'
        )
        for faq in files
    ]

    with connection.cursor() as db:
        db.execute(f'TRUNCATE TABLE {table_name}')
        connection.commit()

    exec_insert = f"""
        INSERT INTO {table_name} (
            QUESTION_ID,
            FAQ,
            VECTOR_FAQ,
            STATE,
            CREATION_BY,
            LAST_UPDATE_BY
        ) VALUES (
            SQ_CHATBOT_ID.NEXTVAL,
            :1,
            :2,
            :3,
            :4,
            :5
        )
    """

    with connection.cursor() as db:
        db.executemany(exec_insert, dataPrepare)
        connection.commit()
