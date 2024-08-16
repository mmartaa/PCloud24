from flask import Flask, request, redirect, url_for, render_template, session, jsonify, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
import json
from secret import secret_key
from google.cloud import firestore
from google.cloud import storage
import pandas as pd
import os
import io


db = 'livelyageing'
coll = 'utenti'

#creo client per accedere a database firestore
db = firestore.Client.from_service_account_json('credentials.json', database=db)
#client per accedere a cloud storage
#storage_client = storage.Client.from_service_account_json('credentials.json')


class User(UserMixin): #classe utente che rappresenta gli utenti del sistema
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username
        self.par = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

login = LoginManager(app)
login.login_view = '/static/login.html'


usersdb = {
    'marta':'gabbi'
}


@app.route('/')
def root():
    #return redirect('/static/index.html')
    return redirect(url_for('static', filename='index.html'))


@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/static/grafico.html'))

    username = request.values['u']
    password = request.values['p']

    if username in usersdb and password == usersdb[username]['p']: #va bene ['p']??????
        login_user(User(username), remember=True)
        return redirect('/grafico')

    flash('Nome utente o password non validi', 'error')
    return redirect('/static/login.html')


@app.route('/logout', methods=["POST"])
def logout():
    logout_user()
    return redirect('/')


@app.route('/grafico', methods=['GET'])
@login_required
def grafico():
    #prendi i dati dal file giusto
    user_id = request.args.get('user_id') #????
    collection_ref = db.collection(user_id)
    docs = collection_ref.stream()
    dati = [doc.to_dict() for doc in docs]

    return redirect(url_for('static', filename='grafico.html')), jsonify(dati)


def get_data_from_gcstorage():
    nome_utente = "Carla"
    BucketName = "pcloud24_1"         #definisco il bucket di salvataggio in clooud
    dumpPath = f"/tmp/{nome_utente}.csv"  # definisco il path di salvataggio locale del modello
    blobName = f"Dati/{nome_utente}.csv"       #definisco il nome del file di salvataggio sul cloud

    #accedo al cloud storage
    storage_client = storage.Client.from_service_account_json('credentials.json')

    bucket = storage_client.bucket(BucketName)  #scelgo il bucket
    blob = bucket.blob(blobName)                #assegno il nome del file di destinazione
    blob.download_to_filename(dumpPath)         #scarico il file dal cloud




'''
# Funzione per caricare CSV dal cloud storage e inserire i dati in Firestore
def upload_csv_to_firestore(bucket_name, files):
    bucket = storage_client.bucket(bucket_name)

    for file_name in files:
        blob = bucket.blob(file_name)

        #scarica il contenuto come linea di testo
        content = blob.download_as_text()

        testo = io.StringIO(content)

        df = pd.read_csv(testo)

        # Nome della collection basato sul nome del file
        collection_name = os.path.splitext(file_name)[0]
        collection_ref = db.collection(db).document(collection_name)

        for index, row in df.iterrows():
            collection_ref.collection('data').add(row.to_dict())
'''


if __name__ == 'main':
    app.run(host='0.0.0.0', port=80, debug=True)


'''
    # Specifica il nome del bucket e la lista dei file CSV da caricare
    bucket_name = 'pcloud24_1'
    files = ['Carla.csv', 'Francesco.csv', 'Lalla.csv', 'Luciano.csv']

    # Chiamata manuale alla funzione per caricare i file in Firestore
    upload_csv_to_firestore(bucket_name, files)
'''