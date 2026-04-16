# test_api.py - Version corrigée
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# REMPLACEZ PAR VOS IDENTIFIANTS
USERNAME = "api"  # ← Changez ici
PASSWORD = "1234"  # ← Changez ici

print("=== 1. Obtenir un token ===")
response = requests.post(f"{BASE_URL}/auth/token/", json={
    "username": USERNAME,
    "password": PASSWORD
})

print(f"Status code: {response.status_code}")

if response.status_code != 200:
    print(f"❌ Erreur d'authentification: {response.text}")
    print("\nVérifiez que:")
    print("1. Le serveur Django est lancé (python manage.py runserver)")
    print("2. Vous avez créé un superutilisateur (python manage.py createsuperuser)")
    print("3. Les identifiants sont corrects")
    exit(1)

token_data = response.json()
access_token = token_data.get('access')
print(f"✅ Token obtenu: {access_token[:50]}...")

headers = {"Authorization": f"Bearer {access_token}"}

# 2. Lister les auteurs
print("\n=== 2. Lister les auteurs ===")
response = requests.get(f"{BASE_URL}/auteurs/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Nombre d'auteurs: {data.get('count', 0)}")
    print(json.dumps(data.get('results', [])[:2], indent=2, ensure_ascii=False))

# 3. Créer un auteur (si pas déjà fait)
print("\n=== 3. Créer un auteur ===")
response = requests.post(f"{BASE_URL}/auteurs/", 
    headers={**headers, "Content-Type": "application/json"},
    json={"nom": "Albert Camus", "nationalite": "Française", "biographie": "Écrivain et philosophe français"}
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✅ Auteur créé avec succès")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
elif response.status_code == 400:
    print("ℹ️ Peut-être déjà existant ou erreur de validation")

# 4. Lister les livres
print("\n=== 4. Lister les livres ===")
response = requests.get(f"{BASE_URL}/livres/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Nombre total de livres: {data.get('count', 0)}")

# 5. Créer un livre
print("\n=== 5. Créer un livre ===")

# D'abord, récupérons un ID d'auteur existant
response = requests.get(f"{BASE_URL}/auteurs/", headers=headers)
if response.status_code == 200 and response.json().get('results'):
    auteur_id = response.json()['results'][0]['id']
    
    response = requests.post(f"{BASE_URL}/livres/",
        headers={**headers, "Content-Type": "application/json"},
        json={
            "titre": "L'Étranger",
            "isbn": "9782070360024",
            "annee_publication": 1942,
            "categorie": "roman",
            "auteur": auteur_id
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Livre créé avec succès")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Réponse: {response.text}")
else:
    print("ℹ️ Créez d'abord un auteur via l'interface admin")

# 6. Tester la pagination
print("\n=== 6. Pagination ===")
response = requests.get(f"{BASE_URL}/livres/?page=1&size=5", headers=headers)
print(f"Status: {response.status_code}")

# 7. Tester les filtres
print("\n=== 7. Filtres ===")
response = requests.get(f"{BASE_URL}/livres/?categorie=roman&disponible=true", headers=headers)
print(f"Status: {response.status_code}")

print("\n=== Tests terminés ===")