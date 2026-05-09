# K-Read Coach — Guide d'intégration

Ce document explique comment les modules de nettoyage de données et de reconnaissance vocale Whisper s'intègrent avec le frontend.

---

## Intégration 1 : Équipier chargé du nettoyage des données (Tom)

**Comment tes fichiers de sortie s'articulent avec le frontend**

Les fichiers produits dans la branche `develop-cleaning` sont lus directement par le frontend. **Tu n'as rien à modifier dans ton code.** Assure-toi simplement que les deux points suivants sont respectés lors de la fusion.

### Emplacement des fichiers

```
K-Read-Coach/
├── data/
│   ├── k_read_coach_dataset.csv   ← fichier CSV nettoyé, à placer ici
│   └── clips/
│       ├── 1_0442.wav             ← tous les fichiers audio, à plat ici
│       ├── 3_3106.wav
│       └── ...
```

### Format du CSV (déjà respecté par ta sortie)

| Colonne | Type | Description |
|---------|------|-------------|
| `path` | str | **Nom de fichier uniquement**, ex. `3_3106.wav`, sans préfixe de répertoire |
| `sentence` | str | Phrase originale en coréen |
| `english_translation` | str | Traduction en anglais |
| `categories` | str | Étiquette de catégorie thématique |

Encodage : `UTF-8-SIG` (ta sortie actuelle) est pris en charge nativement, aucune modification nécessaire.

### Vérification

Après la fusion, lance la commande suivante depuis la racine du projet. Si `is_real` affiche `True`, l'intégration est réussie :

```bash
python -c "
from modules.data_loader import load_dataset
df, is_real = load_dataset('data/k_read_coach_dataset.csv')
print('is_real:', is_real)
print('Nombre de lignes:', len(df))
print('Catégories:', df['categories'].unique().tolist())
"
```

---

## Intégration 2 : Équipier chargé du modèle Whisper

**Tu n'as qu'un seul fichier à modifier**

### Fichier concerné

```
modules/asr_interface.py
```

### Contenu actuel (implémentation mock)

```python
def transcribe_audio(audio_path: str) -> str:
    return "안녕하세요"   # ← remplace cette ligne par l'appel Whisper
```

### Ce que tu dois faire

Remplace uniquement le corps de cette fonction. **La signature ne doit pas changer :**

```python
import whisper   # ou faster-whisper, selon ta préférence

def transcribe_audio(audio_path: str) -> str:
    model = whisper.load_model("base")      # ou "small" / "medium"
    result = model.transcribe(audio_path, language="ko")
    return result["text"]
```

### Contraintes

| Élément | Exigence |
|---------|----------|
| Nom de la fonction | `transcribe_audio`, ne pas modifier |
| Paramètre | `audio_path: str`, chemin local vers le fichier audio |
| Valeur de retour | `str`, texte coréen transcrit |
| Périmètre de modification | **Uniquement `modules/asr_interface.py`, aucun autre fichier** |

### Ajout de la dépendance

Ajoute la bibliothèque choisie à la fin de `requirements.txt` :

```
openai-whisper
```

ou :

```
faster-whisper
```

### Test

```python
from modules.asr_interface import transcribe_audio
result = transcribe_audio("chemin/vers/audio_test.wav")
print(result)   # doit afficher du texte en coréen
```
