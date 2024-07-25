from requests import get, post


base_url = 'http://localhost:80'
user = 'u1'

with open('Dati/Carla.csv') as f:
    for l in f.readlines()[1:]: #salto la prima riga di intestazione
        x,y,z,ora = l.strip().split(';')
        print(x,y,z,ora)
        r = post(f'{base_url}/utenti/{user}',
                 data={'x':x,'y':y,'z':z,'orario':ora})
        #time.sleep(2) ogni 2 secondi fa chiamata post al server
        #se voglio tutti i dati direttamente tolgo il time.sleep


print('done')