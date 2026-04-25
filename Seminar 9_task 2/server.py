import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024

clienti_conectati = {}

mesaje = []  
id_urmator = 1  

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server."
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == 'DISCONNECT':
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat cu succes. La revedere!"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda == 'PUBLISH':
            # Verificare conexiune
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Nu esti conectat la server. Foloseste CONNECT mai intai."
            # Verificare mesaj gol
            elif not argumente:
                raspuns = "EROARE: Mesajul nu poate fi gol. Foloseste: PUBLISH <text>"
            else:
                # Salvare mesaj cu ID unic
                id_curent = id_urmator
                mesaje.append({
                    'id': id_curent,
                    'text': argumente,
                    'autor': adresa_client
                })
                raspuns = f"OK: Mesaj publicat cu ID={id_curent}"
                id_urmator += 1
                print(f"[SERVER] Mesaj publicat de {adresa_client}: '{argumente}' (ID={id_curent})")

        elif comanda == 'DELETE':
            # Verificare conexiune
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Nu esti conectat la server. Foloseste CONNECT mai intai."
            else:
                # Verificare argument numeric
                try:
                    id_de_sters = int(argumente)
                except ValueError:
                    raspuns = "EROARE: ID invalid. Specifica un numar intreg. Exemplu: DELETE 1"
                else:
                    mesaj_gasit = None
                    for mesaj in mesaje:
                        if mesaj['id'] == id_de_sters:
                            mesaj_gasit = mesaj
                            break
                    
                    if mesaj_gasit is None:
                        raspuns = f"EROARE: Nu exista niciun mesaj cu ID={id_de_sters}."
                    elif mesaj_gasit['autor'] != adresa_client:
                        raspuns = "EROARE: Nu poti sterge un mesaj publicat de alt client."
                    else:
                        mesaje.remove(mesaj_gasit)
                        raspuns = f"OK: Mesajul cu ID={id_de_sters} a fost sters cu succes."
                        print(f"[SERVER] Mesaj ID={id_de_sters} sters de {adresa_client}")

        elif comanda == 'LIST':
            # Verificare conexiune
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Nu esti conectat la server. Foloseste CONNECT mai intai."
            else:
                if not mesaje:
                    raspuns = "Nu exista mesaje publicate momentan."
                else:
                    linii = []
                    for mesaj in mesaje:
                        linii.append(f"ID={mesaj['id']}: {mesaj['text']}")
                    raspuns = "\n".join(linii)

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")
