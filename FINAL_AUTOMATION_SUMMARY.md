# Sistema di Automazione Finale

## Workflow Implementati

### 1. `update-submodules.yml` - Motore Principale
- **Frequenza**: Ogni settimana (lunedì alle 06:00 UTC)
- **Funzione**: Controlla le **release ufficiali** di SupersStrings (solo tag vX.Y.Z)
- **Logica**: Solo release stabili, non commit work-in-progress
- **Sicurezza**: Aggiorna solo quando c'è una nuova release pubblicata
- **Output**: Commit automatico con changelog tra release

### 2. `auto-release.yml` - Rilascio Automatico
- **Trigger**: Dopo aggiornamento submodule riuscito
- **Funzione**: Traduzione automatica IT + rilascio GitHub
- **Logica**: Scelte automatiche (Y per sws_strings_en.xml, N per altri)
- **Versioning**: `[nuovo_tag_submodule]-mod_[versione_precedente]` - mantiene la stessa mod_version

## Flusso di Automazione

```
Update Submodules (ogni lunedì 06:00 UTC)
       ↓
   Controlla nuove RELEASE di SupersStrings (tag vX.Y.Z)
       ↓
   Nuova release trovata? → Se NO: Stop
       ↓ (se SÌ)
   Aggiorna submodule alla release specifica + Commit
       ↓
    Auto Release (trigger automatico):
       ↓
   Estrae mod_version dal release precedente
       ↓
   Traduzione IT automatica
       ↓
   Crea release con nuovo tag submodule + stessa mod_version
       ↓
    Completato
```

## Sistema di Versioning

Il sistema implementa una logica di versioning intelligente:

- **Formato**: `[tag_submodule]-mod_[versione_mod]a`
- **Esempio**: `v1.3.5-mod_1.0.0a`
- **Comportamento**: La `versione_mod` rimane costante tra i release
- **Logica**: Solo il `tag_submodule` cambia quando SupersStrings si aggiorna
- **Fallback**: Se non esistono release precedenti, inizia con `1.0.0a`

### Esempi di Versioning:
```
Release 1: v1.3.4-mod_1.0.0a  (primo release)
Release 2: v1.3.5-mod_1.0.0a  (nuovo submodule, stessa mod)
Release 3: v1.4.0-mod_1.0.0a  (nuovo submodule, stessa mod)
```

### File:
- **Automazione**: `.github/workflows/`, `automated_translation.py`, documentazione
- **Esecuzione Manuale**: `main.py`, `translations_*.py`, `utils.py`, `cache_manager.py`
- **Configurazione**: `.gitignore`, `.gitmodules`, `requirements.txt`, `README.md`

## Controllo Manuale

Per eseguire aggiornamenti manuali:

1. **GitHub**: Actions → "Update Submodules" → "Run workflow"
2. **Locale**: 
   ```bash
   git submodule update --remote
   git add input/SupersStrings
   git commit -m "Manual submodule update"
   ```

## Monitoring

- **Actions**: Visualizza esecuzioni in GitHub Actions
- **Commits**: Changelog automatici con dettagli sui cambiamenti tra release
- **Releases**: Pubblicazioni automatiche solo per release stabili SupersStrings
- **Links**: Collegamenti diretti alle release GitHub SupersStrings