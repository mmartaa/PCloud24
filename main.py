from flask import Flask, request, redirect, url_for, render_template, session, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
import json
from secret import secret_key
from google.cloud import firestore
from google.cloud import storage
import pandas as pd
import io

db = 'livelyageing'
coll = 'utente1'

#creo client per accedere a database firestore
db = firestore.Client.from_service_account_json('credentials.json', database=db)
#client per accedere a cloud storage
storage_client = storage.Client.from_service_account_json('credentials.json')


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


@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None


@app.route('/')
def root():
    #return redirect('/static/index.html')
    return redirect(url_for('static', filename='index.html'))

"""
@app.route('/')
def root():
    if 'loggedin' not in session or session["loggedin"] == False:
        return redirect('/static/login.html')
    else:
        return 'Welcome ' + session["name"]


@app.route('/login', methods=['POST'])
def login():
    username = request.values['name']
    password = request.values['password']
    if username in usersdb and usersdb[username] == password:
        session["loggein"] = True
        session["name"] = username
        return redirect('/')
    else:
        return redirect('/static/login.html')

"""


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/static/grafico.html'))
    username = request.values['u']
    password = request.values['p']
    if username in usersdb and password == usersdb[username]:
        login_user(User(username), remember=True)
        return redirect('/grafico')
    return redirect('/static/login.html')


@app.route('/logout')
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


'''
@app.route('/utenti',methods=['GET'])
def utenti():
    u = []
    for entity in db.collection(coll).stream():
        u.append(entity.id)
    return json.dumps(u), 200


#@app.route('/utenti/<u>',methods=['POST'])
def add_data():
    #for u in utenti:
        #coll = 'utente ' + str(u)
        x = float(request.values['x'])
        y = float(request.values['y'])
        z = float(request.values['z'])
        ora = request.values['orario']

        #id = f'{u}'
        doc_ref = db.collection(coll)    #.document(id)
        doc_ref.set({'x': x, 'y': y, 'z': z, 'orario': ora})

'''



def leggi_csv(bucket_name, blob_name):
    """Read a CSV file from Google Cloud Storage and return a DataFrame."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    content = blob.download_as_string().decode('utf-8')
    df = pd.read_csv(io.StringIO(content))
    return df


def upload_to_firestore(collection_name, data):
    """Upload data to Firestore."""
    collection_ref = db.collection(collection_name)
    for record in data.to_dict(orient='records'):
        collection_ref.add(record)
    print(f"Uploaded {len(data)} records to Firestore collection '{collection_name}'")


def main(bucket_name, file_info):
    for blob_name, collection_name in file_info.items():
        # Step 1: Read the CSV file from GCS
        df = leggi_csv(bucket_name, blob_name)

        # Step 2: Upload data to Firestore
        upload_to_firestore(collection_name, df)


'''
    doc_ref = db.collection(coll).document(u)
    if doc_ref.get().exists:
        l = doc_ref.get().to_dict()['values']
        l.append((x,y,z,ora))
        doc_ref.update({'values': l})
    else:
        doc_ref.set({'values':[(x,y,z,ora)]})
    return 'ok',200


@app.route('/utenti/<u>',methods=['GET'])
def get_data():
    doc_ref = db.collection(coll)
    if doc_ref.get().exists:
        r = []
        for i in range(len(db[u])):
            r.append([db[u][i][0],db[u][i][1],db[u][i][2],db[u][i][3]])
        return json.dumps(r),200
    else:
        return 'user not found',404
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

    bucket_name ='pcloud24_1'
    file_info = {
        'Carla.csv': 'carla_collection',
        'Lalla.csv': 'lalla_collection'
    }

    main(bucket_name, file_info)
