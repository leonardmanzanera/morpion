# Morpion en local et en ligne

Ce projet fournit une impl\u00e9mentation compl\u00e8te du jeu de morpion (Tic-Tac-Toe) en Python.
Il contient un mode local pour deux joueurs dans un m\u00eame terminal, ainsi qu'un serveur et un
client r\u00e9seau pouvant \u00eatre d\u00e9ploy\u00e9s sur [Railway](https://railway.app/) pour jouer \u00e0 distance.

## Structure du projet

```
app/
├── cli/
│   └── main.py          # Mode local dans un terminal
├── game/
│   └── board.py         # Logique m\u00e9tier du morpion
└── network/
    ├── client.py        # Client r\u00e9seau en ligne de commande
    └── server.py        # Serveur TCP asynchrone pour les parties en ligne
```

## Pr\u00e9requis

- Python 3.9 ou plus r\u00e9cent.

Aucune d\u00e9pendance externe n'est n\u00e9cessaire : la biblioth\u00e8que standard suffit.

## Jouer en local dans le terminal

```bash
python -m app.cli.main
```

Les coordonn\u00e9es des coups utilisent les indices 0, 1 et 2. Entrez par exemple `1,2` pour
jouer dans la case au centre-droit.

## Lancer un serveur r\u00e9seau

```bash
python -m app.network.server
```

Par d\u00e9faut, le serveur \u00e9coute sur le port `8000`. Vous pouvez modifier le port en
positionnant la variable d'environnement `PORT`.

Chaque partie commence automatiquement lorsque deux joueurs sont connect\u00e9s. Les coups se
font en saisissant `ligne,colonne`. Il est possible de quitter une partie en tapant `QUIT`.

## Utiliser le client r\u00e9seau

Sur une machine cliente, ex\u00e9cutez :

```bash
python -m app.network.client --host 127.0.0.1 --port 8000
```

Adaptez `--host` et `--port` en fonction de l'adresse de votre serveur.

## D\u00e9ploiement sur Railway

1. Cr\u00e9ez un nouveau projet "Python" sur Railway et connectez ce d\u00e9p\u00f4t.
2. Ajoutez une variable d'environnement `PORT` (Railway fournit g\u00e9n\u00e9ralement cette variable
   automatiquement lors du d\u00e9ploiement).
3. D\u00e9finissez la commande de d\u00e9marrage du service sur `python -m app.network.server`.
4. D\u00e9ployez. Railway exposera un point d'acc\u00e8s TCP sur le port indiqu\u00e9 dans l'interface.

Les joueurs peuvent ensuite utiliser le client fourni ou n'importe quel autre client TCP pour se
connecter \u00e0 l'adresse Railway et jouer \u00e0 distance.

## Tests rapides

Pour v\u00e9rifier la logique du plateau sans passer par l'interface, ex\u00e9cutez ce petit script :

```bash
python - <<'PY'
from app.game.board import Board, Move

board = Board()
for move in [Move(0, 0), Move(1, 1), Move(0, 1), Move(1, 0), Move(0, 2)]:
    board.play(move)

print(board.render())
print("Gagnant:", board.winner)
PY
```

Le script affiche le plateau final et le vainqueur.
