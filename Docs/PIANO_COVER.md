# Piano di lavoro: ricostruzione delle cover di Beatch Slash!

File di lavoro per Claude Code e Codex. **Lo elimina solo l'utente**, quando lo dice lui. A differenza di `PROJECT_CONTEXT.md` e `CODE_MAP.md`, questo file **contiene uno storico** (sezione 9), per volontà esplicita dell'utente: non va "ripulito". Si aggiorna a ogni compito concluso: si spunta la casella nella sezione 8 e si aggiunge una riga nello storico.

Prima di lavorare leggi: `AGENTS.md`, `Docs/CODE_MAP.md`, `Docs/PROJECT_CONTEXT.md` (sezione 8), `Docs/GIMP.md`, la guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\gimp.md` e l'intestazione dei moduli in `C:\Users\stefa\.agent-knowledge\game-tools\scripts\gimp\`.

## Indice

1. [Obiettivo](#1-obiettivo)
2. [Decisioni dell'utente](#2-decisioni-dellutente)
3. [Tela e coordinate](#3-tela-e-coordinate)
4. [File prodotti](#4-file-prodotti)
5. [Stile: riferimenti per materiale](#5-stile-riferimenti-per-materiale)
6. [Elementi dell'ambiente](#6-elementi-dellambiente)
7. [Metodo e regole operative](#7-metodo-e-regole-operative)
8. [Fasi e compiti](#8-fasi-e-compiti)
9. [Storico](#9-storico)
10. [Passaggio di consegne](#10-passaggio-di-consegne): stato attuale, lavori in corso, prossimi passi in ordine (**chi riprende il lavoro parte da qui**).

## 1. Obiettivo

Ricostruire in GIMP, a livelli e con sorgenti `.xcf`, le due cover:

- `Assets/Images/beatch-slash-cover-no-logo.png` (1672×941, **riferimento per posizioni, ambiente e personaggi**);
- `Assets/Images/beatch-slash-cover-logo.png` (1672×941, **riferimento di stile per l'ambiente**: colori, saturazione, forme, tratto).

Si parte dalla cover senza logo. Il risultato è un ambiente completo e indipendente, un'estensione della cover no-logo, più i personaggi come PNG separati. Da questi pezzi si compongono in futuro, senza ridisegnare nulla: la cover no-logo, la cover con logo (personaggi spostati come nella cover con logo, più il logo completo già ricreato in `Assets/Images/beatch-slash-logo.png`), icone e immagini quadrate.

## 2. Decisioni dell'utente

1. **Personaggi: ritaglio, non ricalco** (soluzione provvisoria: alla fine si sostituisce con il ricalco, punto 3.10c). Eccezione esplicita alla regola fissa "ricreare, mai ritagliare", valida **solo per i personaggi delle cover e i loro accessori**. Si ritagliano al pixel dalla cover no-logo e si ripara il bordo (niente aloni di cielo, mare o sabbia). Lo stile dei personaggi resta quello della no-logo, identico.
2. **Due progetti personaggi:**
   - **coppia:** ragazza rossa + ragazzo (sono un'unica figura), con la palla di sabbia, le briciole, i segni gialli "!" e le gocce di sudore;
   - **rivale:** ragazza viola, con i cuoricini e la scia rosa.
3. **Accessori nei progetti dei personaggi**, su livelli separati, così si spostano con loro. Cuoricini, "!" e briciole si ritagliano come i personaggi. Le **ombre proiettate sulla sabbia si ridisegnano** come livello semitrasparente (non si ritagliano) e si esportano anche come PNG a parte.
4. **Ambiente ridisegnato da zero**, elemento per elemento: posizioni dalla no-logo; colori, saturazione, forme e tratto dalla cover con logo. Nessun pixel dell'originale copiato.
5. **Tela con margini extra** (sezione 3): le parti oltre i bordi della no-logo si disegnano da zero.
6. **Zone dietro i personaggi**: si disegnano da zero, continuando gli elementi (mare, battigia, sabbia, scogli, isola, sgabelli, cielo).
7. **Sequenza obbligatoria, in quest'ordine:**
   1. **Disegno completo.** Durante la creazione nessun ciclo di confronto e ritocco: si disegna un pezzo alla volta finché l'immagine intera è finita.
   2. **Correzione degli errori fatta dall'agente** (Claude o Codex), di propria iniziativa, sull'immagine intera: confronto con i riferimenti, elenco degli errori, correzioni.
   3. **Rifinitura con verifica dell'utente.** L'utente valuta la prima composizione e indica i pezzi da rifare. Si completa e si mostra un solo pezzo per volta. Ogni consegna si chiude con l'apertura dell'anteprima aggiornata e una pausa fino al riscontro dell'utente. Si passa al pezzo successivo dopo il suo via libera. Vedi fase 3.
9. **Metodo preferito: ricalco dei toni.** Quando esiste un riferimento, ogni elemento si ricalca dalle zone di tono dell'originale (`LIB/tone_trace.py`, vedi 3.5) invece di ricostruirlo a mano con forme proprie, che divergono troppo. Si disegna a mano solo ciò che il riferimento non mostra (parti coperte o fuori cornice), nello stesso stile delle zone ricalcate.
8. **Fedeltà dell'ambiente.** Le forme, gli scorci, i rapporti di scala e le sovrapposizioni seguono la cover senza logo. Luci, colori, materiali e tratto fanno riferimento a entrambe le cover secondo la sezione 5. Ogni pezzo deve avere volume e appoggi credibili nello stile illustrato. La tela estesa deve reggere come composizione autonoma, anche nei margini e nelle zone ricostruite dietro i personaggi.

## 3. Tela e coordinate

- **Tela dell'ambiente: 2172×1222** (16:9, circa +15% per lato).
- **Cornice della no-logo dentro la tela:** origine **(250, 140)**, dimensione 1672×941. Un punto (x, y) della no-logo sta in (x + 250, y + 140) della tela.
- **Convenzione unica:** tutte le misure, ricette e tracciati sono in **coordinate della tela**. Il riferimento no-logo si usa **già spostato** in un PNG 2172×1222 trasparente fuori dalla cornice (`ref_nologo_canvas.png`, vedi fase 0). Nella sezione 6 le coordinate sono invece quelle delle immagini originali, come aiuto per trovare gli elementi.
- **Attenzione:** `trace_reference.py` ricava `opaque` dall'alpha e `vector_art` lo usa per ritagliare i livelli continuati. Con il riferimento riempito di trasparenza, ogni livello verrebbe tagliato alla cornice e le estensioni sparirebbero. **Nelle ricette della cover quel ritaglio va spento** (opzione da aggiungere in fase 0).
- **Margini da inventare:** sinistra (resto del chiosco e del tetto di paglia, foglie), alto (cielo, fronde della palma, tetto), destra (scogliera e isola, mare, cielo, nuvole), basso (sabbia, piante, sassi).
- **Personaggi:** PNG ritagliati stretti attorno alla figura (con accessori), con lo **scostamento** nella tela e nella no-logo registrato nella ricetta e nella sezione 9.

## 4. File prodotti

Tutti i percorsi sono relativi a `C:\Users\stefa\Documents\Progetti\GodotProjects\beatch-slash!\`.

| File | Contenuto |
| --- | --- |
| `Tools/gimp/beatch_slash_cover_background.xcf` | Ambiente 2172×1222, un livello (o più livelli: base, ombre, luci, dettagli) per elemento. Livelli nascosti: `reference` (no-logo nella cornice, sezione 3) e `style_reference` (cover con logo, solo per i confronti di stile). |
| `Tools/gimp/beatch_slash_cover_couple.xcf` | Coppia: livelli `couple` (ragazza rossa + ragazzo con palla e gocce), `ball_crumbs`, `exclaim`, `shadow`; `reference` nascosto. |
| `Tools/gimp/beatch_slash_cover_rival.xcf` | Rivale: livelli `rival`, `hearts`, `shadow`; `reference` nascosto. |
| `Tools/gimp/recipes/cover_couple.json`, `cover_rival.json` | Valori del ritaglio (semi, poligoni, soglie, riparazione del bordo, scostamenti). |
| `Tools/gimp/recipes/cover_couple_shadow.json`, `cover_rival_shadow.json` | Anelli misurati sulla tela, campioni sRGB e valori di riempimento dei livelli ombra. |
| `Tools/gimp/recipes/cover_background/<elemento>.json` | Una ricetta `vector_art` per elemento o gruppo (sezione 6), con l'ordine dei livelli. |
| `Tools/gimp/recipes/cover_background/_palette.json` | Tavolozze per materiale campionate dalla cover con logo (sezione 5). |
| `Assets/Images/beatch-slash-cover-background.png` | Ambiente esportato (2172×1222). |
| `Tools/gimp/parts/beatch-slash-cover-couple.png`, `beatch-slash-cover-couple-shadow.png` | Coppia e sua ombra. |
| `Tools/gimp/parts/beatch-slash-cover-rival.png`, `beatch-slash-cover-rival-shadow.png` | Rivale e sua ombra. |

- `beatch-slash-cover-no-logo.png` e `beatch-slash-cover-logo.png` **non si sovrascrivono** finché l'utente non approva. Dopo la sovrascrittura l'unica copia degli originali è il livello nascosto `reference` degli `.xcf`: non eliminarlo.
- Anteprime di lavoro: nella scratchpad della sessione o in `C:\Users\stefa\AppData\Local\Temp\beatch_cover_preview\`, mai in `Assets/`.
- File intermedi delle analisi (PNG riempiti, tracciati JSON, maschere): fuori dal progetto, nella stessa cartella temporanea.
- Nessun suffisso di versione, nessun file in `Assets/ConceptArt`.

## 5. Stile: riferimenti per materiale

Alcuni elementi della no-logo non esistono nella cover con logo (sgabelli, isolotto centrale, alcuni scogli). Per questo lo stile si prende **per materiale**: ogni elemento usa la tavolozza e il trattamento del suo materiale.

| Materiale | Dove campionarlo nella cover con logo (coordinate 1672×941, da verificare guardando) | Elementi che lo usano |
| --- | --- | --- |
| Cielo | gradiente in alto, colonne x 600–1000 e 1400–1672, y 0–480 | cielo |
| Nuvole | (780–930, 40–90), (1100–1430, 430–500) | nuvole |
| Mare, schiuma | (650–1672, 500–760); onde e schiuma sulla battigia (900–1672, 600–760) | mare, onde, battigia |
| Sabbia | (150–1672, 700–941), con impronte e puntinatura | sabbia, impronte, sassolini |
| Roccia | scoglio (1130–1400, 515–620), masso (1370–1672, 630–790), scogliera (1370–1672, 400–530) | scogli, scogliera, isola, isolotto |
| Vegetazione delle isole | cima della scogliera (1370–1672, 400–470) | vegetazione su isola e isolotto |
| Legno | chiosco (0–300, 100–560), barile (10–150, 560–690) | pali, bancone, mensole, sgabelli, barile |
| Paglia | tetto (0–300, 0–200) | tetto del chiosco |
| Tessuti e vetro | tenda a righe (110–300, 190–280), lanterna (75–135, 230–300), bottiglie | tenda, lanterna, bottiglie, bicchieri |
| Tavola da surf | (0–90, 330–560) | tavola |
| Palma | tronco e fronde (100–580, 0–190) | palma |
| Foglie e fiori | ibisco (0–170, 670–860), foglie (0–60, 520–700), cespugli (1330–1672, 740–941) | ibisco, foglie, piante |
| Conchiglie, stella marina | (1270–1300, 840–860), (1110–1215, 860–930), (1210–1260, 845–870) | conchiglie, stella |

Tratto comune: contorno marrone scuro (spessore e colore da misurare per materiale), riempimenti a campiture con ombre a taglio netto e luci, dettagli a pennellate (venature, fili di paglia, puntini di sabbia).

## 6. Elementi dell'ambiente

Ordine dal basso verso l'alto. Coordinate di posizione nella **no-logo** (1672×941, approssimate: verificare guardando il riferimento). "Da inventare" = parti dietro i personaggi o oltre i bordi.

| # | Gruppo (corsia) | Elementi | Posizione nella no-logo | Da inventare |
| --- | --- | --- | --- | --- |
| 1 | Cielo e nuvole | cielo a gradiente; nuvole in alto al centro, in alto a destra, piccole sopra il mare | tutto l'alto; nuvole (870–1060, 40–140), (1310–1672, 0–200), (930–1060, 230–280) | cielo dietro le teste; margini sopra, a sinistra, a destra |
| 2 | Isole e scogliera | scogliera di destra con vegetazione, isolotto centrale | (1380–1672, 225–415), (920–1050, 290–410) | isolotto dietro i capelli viola; scogliera oltre il bordo destro |
| 3 | Mare e battigia | mare, riflessi, onde, schiuma, linea della battigia | (560–1672, 380–650) | mare e onde dietro la coppia e la rivale; margine destro |
| 4 | Sabbia | sabbia, impronte, sassolini, solchi | (0–1672, 470–941) | sabbia dietro le gambe; margini sotto e ai lati |
| 5 | Scogli | scogli in mare (1400–1672, 440–560), (990–1100, 545–600); massi (1460–1672, 590–760); sassi in basso (180–330, 880–941), (1380–1600, 870–941) | vedi colonna | parti dietro la rivale; massi oltre il bordo destro e in basso |
| 6 | Palma | tronco dietro il tetto, fronde in alto a sinistra | (180–670, 0–200) | fronde oltre il bordo alto e sinistro |
| 7 | Chiosco | tetto di paglia, pali, tenda a righe, lanterna, mensole e bottiglie, bancone, bicchieri, sgabelli | (0–380, 0–640) | sgabelli e bancone dietro i capelli rossi; chiosco oltre il bordo sinistro e alto |
| 8 | Tavola e barile | tavola da surf, barile con corda | (0–110, 265–525), (20–175, 520–665) | parti oltre il bordo sinistro |
| 9 | Conchiglie e stella | conchiglie (380–450, 860–905), (1470–1535, 795–825); stella marina (1195–1280, 860–915) | vedi colonna | nessuna |
| 10 | Piante in primo piano | ibisco e foglie in basso a sinistra; cespugli a destra (1420–1530, 700–760) e in basso a destra (1530–1672, 800–941) | (0–220, 470–941) e vedi colonna | foglie oltre i bordi sinistro, destro e basso |

I personaggi si compongono **sopra** tutti questi gruppi, tranne eventuali elementi in primo piano che nella no-logo li coprono (verificare in fase 0: per ora nessuno).

## 7. Metodo e regole operative

### Strumenti

- MCP **`gimp`** (GIMP 3.2.8, porta 9890): prima di tutto `check_server`. Se non risponde, fermarsi e dirlo all'utente.
- **Regola fissa:** a ogni passo concluso e operazione terminata in GIMP chiudere immagini di prova, script, processi e collegamenti non più necessari (compresi i `gimp-mcp-plugin.exe` di sessioni chiuse e i server MCP lasciati dai client) **prima** di iniziare l'operazione successiva. Procedura in `Docs/GIMP.md`, sezione 1.
- **Criterio di riuscita:** la tela estesa deve poter essere usata da sola. Ogni elemento deve sembrare dipinto come l'originale, non composto da figure geometriche: sagome organiche, prospettiva e scorcio dell'originale, volume, appoggi a terra e ombre di contatto credibili.
- Analisi fuori da GIMP con `uv` (niente installato nel progetto):
  `uv run --with numpy --with scipy --with scikit-image --with pillow python <script> <argomenti>`
- Caricamento della libreria nella console di `call_api`:
  `import sys; sys.path.insert(0, 'C:/Users/stefa/.agent-knowledge/game-tools/scripts/gimp')`, poi `import importlib, layer_ops, vector_art` e `importlib.reload` dei moduli.
- Script sempre generici: logica nella libreria `C:\Users\stefa\.agent-knowledge\game-tools\scripts\gimp\`, valori del progetto solo nelle ricette `Tools/gimp/recipes/`.

### Ritaglio dei personaggi (corsie A e B)

Modulo generico nuovo, eseguito fuori da GIMP (numpy):

1. Regioni non scure racchiuse dal contorno scuro (come `cutout.regions`), assegnate al personaggio con semi e poligoni della ricetta; tutto il resto è sfondo.
2. **Buchi interni trasparenti:** cielo tra braccio e corpo, mare tra le ciocche, sabbia tra le gambe. Si marcano come sfondo con regole di colore e semi.
3. Ciocche senza contorno netto (punte dei capelli): poligoni manuali nella ricetta.
4. **Riparazione del bordo:** l'anello esterno sfumato si ricolora con il colore del contorno vicino, con alpha calcolato dalla distanza dal bordo; niente aloni di sfondo.
5. Uscita: PNG RGBA ritagliato stretto più JSON con lo scostamento. In GIMP si importa nell'`.xcf` del personaggio, con la no-logo come `reference` nascosto.
6. **Primo prodotto della corsia, prima di tutto il resto:** una **maschera grezza** delle sagome (allargata di qualche pixel) in coordinate della tela. Serve alle corsie dell'ambiente per sapere cosa inventare dietro i personaggi.

### Ambiente (corsie C–L, una per gruppo della sezione 6)

1. Contorni e posizioni dalla no-logo riempita (`ref_nologo_canvas.png`): `trace_reference.py` dove il contorno scuro è pulito; dove il disegno è pittorico e il tracciamento esce rumoroso, poligoni scritti a mano guardando ritagli ingranditi.
2. Colori, contorni e trattamento dalla tavolozza del materiale (`_palette.json`, sezione 5).
3. Ricetta `vector_art` per gruppo: forme, riempimenti, ombre in Moltiplica, luci in Scherma, dettagli a pennellate (`stroke` con `taper`).
4. Zone dietro i personaggi e margini: forme proseguite o inventate nello stesso stile.
5. **Unica verifica ammessa durante la creazione:** la ricetta gira senza errori. Niente confronti col riferimento e niente ritocchi: quelli si fanno nella fase 2b, a disegno finito.

### Istruzioni comuni alle corsie dell'ambiente

Percorsi: `PRJ` = `C:/Users/stefa/Documents/Progetti/GodotProjects/beatch-slash!`, `LIB` = `C:/Users/stefa/.agent-knowledge/game-tools/scripts/gimp`, `TMP` = `C:/Users/stefa/AppData/Local/Temp/beatch_cover_preview`.

| Corsia | Ricette (ordine di montaggio = numero) | Prefisso di livelli e tracciati |
| --- | --- | --- |
| C+D | `01_sky.json` (cielo, nuvole), `02_islands.json` (scogliera, isolotto, vegetazione) | `sky_`, `isl_` |
| E | `03_sea.json` (mare, riflessi, onde, schiuma, battigia, sabbia bagnata) | `sea_` |
| F | `04_sand.json` (sabbia asciutta, impronte, sassolini) | `sand_` |
| G | `05_rocks.json` (scogli in mare, massi, sassi) | `rock_` |
| H | `06_palm.json` (tronco, fronde) | `palm_` |
| I | `07_hut.json` (tetto, pali, tenda, lanterna, mensole, bottiglie, bancone, bevande, sgabelli) | `hut_` |
| J+K+L | `08_props.json` (tavola, barile, corda), `09_shells.json` (conchiglie, stella), `10_plants.json` (ibisco, foglie, cespugli) | `prop_`, `shell_`, `plant_` |

1. **Ricette** in `PRJ/Tools/gimp/recipes/cover_background/`. Ognuna contiene tutte le chiavi di `_base.json` (copiate) più `path_prefix` e `draw`. Livelli chiamati `<prefisso><elemento>_<ruolo>` (`_outline`, `_base`, `_shade`, `_light`, `_detail`…), unici in tutto il disegno. Coordinate della tela 2172×1222.
2. **Geometria** dalla no-logo sulla tela (`TMP/ref_nologo_canvas.png`). Le parti tracciate con `LIB/trace_reference.py` hanno un file di tracciamento accanto alla ricetta (`<nn>_<nome>.trace.json`), ricetta di tracciamento in `TMP/lanes/<corsia>/`. Serve sempre una parte di raccolta `_other` come ultima regola. Dove il disegno è pittorico si usano forme `poly` con `smooth`, scritte guardando ritagli ingranditi.
3. **Colori e tratto** da `_palette.json` (ruoli `outline`, `deep`, `shade`, `base`, `light`, `highlight`, `texture`; blocco `style`). Le coordinate `where_*` della tavolozza sono nelle immagini 1672×941. Contorni sottili (circa 2 px, colore del materiale, mai nero), ombre a taglio netto (feather 1–2 px), saturazione della cover con logo. Cielo, nuvole, mare, sabbia, schiuma e chiome delle isole senza contorno.
4. **Personaggi:** gli elementi si disegnano interi anche dove sono coperti dai personaggi, proseguendo le forme. Se esiste `TMP/chars/ROUGH_READY.txt`, `TMP/chars/couple_rough_mask.png` e `rival_rough_mask.png` (coordinate della tela) dicono dove i pixel della no-logo sono personaggi e non vanno tracciati come ambiente.
5. **Margini** (sezione 3) disegnati da zero, nello stesso stile.
6. **Render di lavoro** solo su un `.xcf` proprio: `vector_art.run(ricetta, trace, xcf='TMP/lanes/<corsia>/<corsia>.xcf')`, in **una sola chiamata `call_api`** del tipo `exec(open('<script>.py', encoding='utf-8').read(), {})`. Nello script: `sys.path.insert(0, LIB)`, `import vector_art, layer_ops`, **mai `importlib.reload`**. Anteprima con `layer_ops.export_visible(img, 'TMP/lanes/<corsia>/preview.png')`, poi lettura del PNG. Una chiamata che supera 300 s va spezzata con `only=[...]`. Non si apre, non si salva e non si tocca `beatch_slash_cover_background.xcf` né altre immagini aperte.
7. **Niente cicli di confronto e correzione** (fase 2b): si guarda il proprio render solo per andare avanti col pezzo successivo.
8. Script nuovi solo generici in `LIB`; valori solo nelle ricette.

### Parallelismo sicuro

- GIMP è **una sola istanza** con **una sola console `call_api`**: le variabili globali sono condivise tra chi la usa, e un `importlib.reload` lanciato da un agente rompe il lavoro di un altro.
- **In parallelo (agenti), solo fuori da GIMP:** ritaglio completo dei personaggi, tracciamenti, campionamento delle tavolozze, scrittura delle ricette.
- **In sequenza (thread principale):** tutti i render in GIMP, un gruppo alla volta, nell'ordine della sezione 6.
- Ripiego, solo se servisse: un agente può fare un render in GIMP se lo fa in **una sola chiamata `call_api`**, in un namespace proprio (`exec(codice, {})`), senza `reload` e su un'immagine sua.
- Mai due agenti sullo stesso file.

### Modifiche alla libreria (fase 0, prima di avviare gli agenti)

1. `vector_art.run`: modalità che **sostituisce solo i livelli della ricetta** e lascia gli altri (oggi `clear_except` cancella tutto tranne `reference`). Serve un parametro per la posizione nella pila.
2. `vector_art.target`: tela di dimensione data, riferimento posizionato a uno scostamento, secondo riferimento nascosto (`style_reference`).
3. Opzione per **spegnere il ritaglio a `opaque`** nei livelli continuati (sezione 3).
4. Nuovo modulo generico di ritaglio dei personaggi (sezione 7, corsie A e B), con un piccolo autotest.
5. Docstring aggiornate; uso descritto in `Docs/GIMP.md` e nella guida generica `gimp.md`.

## 8. Fasi e compiti

Legenda: `[ ]` da fare, `[x]` fatto. A ogni compito chiuso: spuntarlo e aggiungere una riga nello storico (sezione 9).

### Fase 0: preparazione (thread principale, in sequenza)

- [x] 0.1 `check_server` di GIMP; lettura delle guide.
- [x] 0.2 Moduli per tela estesa, montaggio e ritaglio verificati. Procedure nelle guide GIMP.
- [x] 0.3 `ref_nologo_canvas.png` (no-logo dentro la tela 2172×1222, scostamento (250, 140)) e copia della cover con logo, nella cartella temporanea.
- [x] 0.4 `beatch_slash_cover_background.xcf` creato con `reference` e `style_reference` nascosti.
- [x] 0.5 Verifica delle posizioni e dei materiali sulle due cover. Gli elementi di primo piano stanno dietro i personaggi nella composizione, con i piccoli ritagli di sabbia ai piedi risolti nella sagoma.

### Fase 1: lavoro in parallelo fuori da GIMP (agenti)

- [x] A.1 Coppia: maschera grezza della sagoma (consegna anticipata per le corsie C–L).
- [x] A.2 Coppia: ritaglio preciso, buchi interni, riparazione del bordo, briciole e segni "!" separati, PNG + scostamento. Le gocce e la palla nella mano restano sulla figura perché si sovrappongono al disegno.
- [x] B.1 Rivale: maschera grezza rigenerata dalla sagoma.
- [x] B.2 Rivale: ritaglio preciso, cuoricini e scia, PNG + scostamento.
- [x] P Tavolozze per materiale dalla cover con logo (`_palette.json`): serve a tutte le corsie C–L.
- [x] C Cielo e nuvole: ricetta.
- [x] D Isole e scogliera: ricetta.
- [x] E Mare e battigia: ricetta.
- [x] F Sabbia: ricetta.
- [x] G Scogli: ricetta.
- [x] H Palma: ricetta.
- [x] I Chiosco: ricetta.
- [x] J Tavola e barile: ricetta.
- [x] K Conchiglie e stella: ricetta.
- [x] L Piante in primo piano: ricetta.

Dipendenze: P prima di C–L; A.1 e B.1 prima delle parti "da inventare" di C–L.

### Fase 2: disegno in GIMP (thread principale, in sequenza)

- [x] 2.1 Render dei gruppi C → L nell'ordine della sezione 6, dentro `beatch_slash_cover_background.xcf`.
- [x] 2.2 `beatch_slash_cover_couple.xcf` e `beatch_slash_cover_rival.xcf`: personaggi, accessori, ombre ridisegnate.
- [x] 2.3 Esportazione dei PNG nuovi (sezione 4).
- [x] 2.4 Anteprima della cover no-logo composta (ambiente + personaggi agli scostamenti originali, ritaglio della cornice) nella cartella temporanea.

### Fase 2b: prima passata di correzioni prima della verifica dell'utente

- [x] 2b.1 Confronto dell'illustrazione intera, delle zone e dei margini con i riferimenti. Verifica ingrandita dei ritagli.
- [x] 2b.2 Correzioni dell'agente e nuova anteprima per la verifica dell'utente.
  - [x] C–D: nuvole a sagoma irregolare, isolotto ampliato e faccette della scogliera.
  - [x] E–G: curva di battigia e sabbia, creste e schiuma, faccette dei massi e gruppi di sassolini.
  - [x] H–I: tetto e sottogronda, fronda a sinistra, tronco più stretto, bordo della tenda e sommità dei pali.
  - [x] J–L: copertura del barile, foglie dei cespugli, conchiglie, stella e ombreggiatura dell'ibisco.
  - [x] Montaggio, confronto finale dei margini e verifica delle ombre sulla sabbia aggiornata.

### Fase 3: rifinitura e approvazione un pezzo alla volta

La prima composizione ha un aspetto troppo geometrico. L'utente è soddisfatto di **cielo, nuvole, mare, rocce in acqua e rocce vicino alla riva**. Questi elementi fanno da riferimento nella composizione e sono fuori dal perimetro delle correzioni elencate qui.

**Procedura per ogni pezzo**

1. **Confronto.** Affiancare un ritaglio della no-logo e lo stesso ritaglio della composizione alla stessa scala. Usare la cover con logo per campionare il trattamento del materiale. Misurare sagoma, inclinazione, scala, sovrapposizioni, punti di appoggio, luci e ombre. Annotare le differenze del pezzo prima di intervenire.
2. **Ricostruzione in GIMP.** Correggere prima sagoma e prospettiva, poi volume, luce, trama e dettagli. Usare tracciati con curve aderenti al riferimento, campiture articolate, passaggi di tono e pennellate dove il materiale li richiede. Regolare i raccordi e gli appoggi nel contesto. I riferimenti restano su livelli nascosti e servono per misure e confronti. Salvare il risultato a livelli e aggiornare la ricetta del pezzo per poterlo rigenerare.
3. **Verifica.** Controllare il confronto a dimensione reale, la cover composta nella cornice originale e la tela estesa. Verificare che il pezzo funzioni alle due inquadrature, soprattutto nei margini inventati e nei raccordi dietro i personaggi. Rifare l'anteprima dopo le correzioni.
4. **Consegna e pausa.** Aprire l'anteprima aggiornata in VS Code o nel visualizzatore disponibile e mostrare il confronto ingrandito. Aggiornare lo storico e il passaggio di consegne con il pezzo, le differenze corrette, le ricette toccate e i percorsi delle anteprime. Chiudere il turno con lo stato **in attesa di verifica**. Se l'utente chiede altri ritocchi, riprendere lo stesso pezzo. Spuntare il compito dopo il suo via libera. GIMP e gli eventuali agenti terminano il lavoro sul pezzo attivo prima della consegna.

**Ordine proposto per la rifinitura**

- [x] **3.1 Ibisco.** Approvato dall'utente. Ricostruire scorcio e orientamento della corolla, petali che si sovrappongono e si ripiegano, pistillo e attacco. Il fiore deve avere lo stesso volume laterale dell'originale, con venature, luci e ombre coerenti con la forma. Estendere i petali tagliati dalla cornice. Ricetta `10_plants.json`.
- [x] **3.2 Fogliame a sinistra.** Approvato dall'utente. Ricostruire il cespo attorno all'ibisco e davanti al barile con un attacco comune, steli e foglie di scorcio. Verificare gli incroci con fiore, barile e roccia. Sviluppare una massa leggibile anche fuori cornice. Ricetta `10_plants.json`.
- [x] **3.3 Cespuglietto destro presso i massi.** Approvato dall'utente. Ricostruire la base sul terreno, la massa retrostante, le foglie sovrapposte e l'ombra di contatto. Ricetta `10_plants.json`.
- [x] **3.4 Cespuglio nell'angolo in basso a destra.** Approvato dall'utente. Dare continuità a base e volume fino al margine della tela estesa, con foglie in profondità e attacchi leggibili. Ricetta `10_plants.json`.
- [x] **3.4b Tutte le altre foglie.** Approvato dall'utente. Fronde di entrambe le palme e ogni altra foglia della tela non coperta da 3.2–3.4. Stesso trattamento dell'originale: foglie con scorcio e piegatura, nervature, passaggi di tono, sovrapposizioni e masse con un corpo, mai foglie singole appese o geometriche. Ricette `06_palm.json` e `10_plants.json`.
- [x] **3.4c Appoggio a terra dei cespugli.** Cespo a sinistra approvato dall'utente; il cespuglio di destra passa alla 3.8. Segnalato dall'utente: il cespo con l'ibisco a sinistra e il cespuglio nell'angolo in basso a destra sembrano incollati sull'immagine, non spuntano dal terreno. Dare a entrambi un attacco nella sabbia: ombra di contatto sotto la massa, base che affonda con sabbia smossa o rilievo attorno e foglie basse che toccano terra. Il cespuglio di destra oggi sta sopra la roccia in primo piano: va spostato o incastrato con la roccia, da risolvere insieme alla 3.8. Ricetta `10_plants.json` (specifiche `foliage/cover_left_bush.json`, `cover_right_corner_bush.json`).
- [x] **3.5 Isolotto in fondo al mare.** Ricalco della parte visibile approvato dall'utente. Resta da fare: allargare l'isolotto nella parte coperta dal ragazzo, disegnandola a mano nello stesso stile delle zone ricalcate, perché nella tela estesa sia un vero isolotto lontano e non si noti che è ricalcata solo la parte a destra. Misurare sagoma e quota sull'orizzonte. Ricostruire pareti, vegetazione a masse e passaggi di tono adatti alla distanza. Ricetta `02_islands.json`. Approvato dall'utente (confronto `TMP/work/s3_final/3.5_isolotto.png`).
- [x] **3.6 Scogliera sullo sfondo a destra.** Ricostruire i piani della parete e la sommità vegetata con volumi continui, spaccature e variazioni di luce. Proseguire il rilievo nel margine destro e controllare il raccordo con l'orizzonte. Ricetta `02_islands.json`. Approvato dall'utente (confronto `TMP/work/s3_final/3.6_scogliera.png`).
- [x] **3.7 Roccia in primo piano a sinistra.** Ricostruire profilo, piani irregolari, spigoli, vena e appoggio nella sabbia. Verificare l'incastro con il fogliame e la continuazione nel margine inferiore. Ricetta `05_rocks.json`, livelli `rock_bottom_*` del lato sinistro. Richiesta dell'utente: sistemata la roccia, rivedere anche la posizione del cespo e dell'ibisco perché risulti corretta e naturale rispetto alla roccia (mantenendo forma, foglie e appoggio approvati). Approvato dall'utente (confronto `TMP/work/s3_final/3.7_roccia_sinistra.png`).
- [x] **3.8 Roccia in primo piano a destra.** Ricostruire la forma della roccia che entra da destra e dal basso, con piani e texture coerenti con il materiale. Verificare incastri con cespuglio e sabbia nella tela estesa. Il cespuglio dell'angolo non deve stare sopra la roccia: roccia e cespuglio si sistemano insieme, dando al cespuglio una posizione naturale e lo stesso appoggio a terra del cespo a sinistra (ombra di contatto, bordo di sabbia). Ricetta `05_rocks.json`, livelli `rock_bottom_*` del lato destro. Approvato dall'utente (confronto `TMP/work/s3_final/3.8_roccia_destra.png`).
- [x] **3.8b Cespo con l'ibisco come un'unica pianta.** Approvato dall'utente (cespo specchiato, confronto `TMP/work/s38b/3.8b_cespo_ibisco.png`). Segnalato dall'utente dopo la 3.7: il fiore è rivolto verso destra, mentre le foglie sotto pendono verso sinistra, quindi fiore e cespo non sembrano un unico corpo. Dare al cespo una direzione coerente con il fiore (o viceversa), mantenendo posizione, appoggio e rapporto con la roccia approvati. Da fare prima della 3.9. Specifica `foliage/cover_left_bush.json`, ricetta `10_plants.json`.
- [x] **3.9 Chiosco.** Approvato dall'utente (chiosco ricalcato ed esteso oltre il bordo sinistro in prospettiva, barile con la corda ricalcato, sgabello destro tolto). Ricostruire le linee prospettiche di tetto, pilastri, pareti e bancone, con profondità, giunzioni e appoggi leggibili. Allineare travi, tenda, mensole, lampada e sgabelli alla stessa struttura. Dare volume alla paglia e al legno. Completare il lato sinistro oltre cornice con la stessa prospettiva. Ricetta `07_hut.json`. Nota dell'utente: nel suo insieme il chiosco oggi sembra privo di prospettiva.
- [x] **3.10 Stella marina e conchiglie.** Approvato dall'utente (confronto `TMP/work/s310/3.10_stella_conchiglie.png`). Stella marina: misurare lo scorcio e le proporzioni dei cinque bracci, ricostruire spessore, pieghe, punte smussate, dettagli della superficie e ombra a terra. Conchiglie sparse sulla sabbia: forma, costolature, volume e ombra a terra. Entrambe con il ricalco dei toni dall'originale, come gli altri pezzi. Ricetta `09_shells.json`.
- [ ] **3.10b Ricalco degli elementi rifatti a mano.** **In sospeso** (indicazione dell'utente: per ora si sistemano solo stella marina e conchiglie).  Dopo i punti principali (3.6–3.10): rifare con il ricalco dei toni gli elementi della fase 3 ricostruiti con forme proprie (ibisco, cespo a sinistra, ciuffo presso i massi, cespuglio d'angolo, palme, tavola da surf; il barile è già ricalcato nella 3.9), mantenendo appoggi e posizioni decisi nel frattempo; le parti nascoste o fuori cornice si disegnano a mano nello stesso stile.
- [x] **3.10c Personaggi ricalcati.** **Non necessario** (l'utente tiene i ritagli dei personaggi). Testo originale: **In sospeso** (indicazione dell'utente: per ora si sistemano solo stella marina e conchiglie).  Alla fine, quando si inseriscono i personaggi: ricreare con il ricalco, come PNG separati, la rivale (ragazza viola) da sola e la coppia (ragazzo e ragazza rossa) insieme, con i loro elementi caratteristici (cuoricini e scia rosa della rivale, segni gialli "!" del ragazzo, granelli di sabbia della ragazza rossa) e le loro ombre. Sostituisce il ritaglio al pixel della decisione 2.1.
- [ ] **3.11 Verifica d'insieme.** **In sospeso** (indicazione dell'utente: per ora si sistemano solo stella marina e conchiglie).  Aprire la composizione e la tela estesa. Ricontrollare anche gli elementi fuori dalla lista rispetto all'originale. Registrare ogni eventuale difetto residuo come correzione distinta e sottoporlo allo stesso ciclo di verifica.
- [ ] **3.12 Approvazione della cover senza logo.** **In sospeso** (indicazione dell'utente: per ora si sistemano solo stella marina e conchiglie).  Dopo il via libera dell'utente, aggiornare `beatch-slash-cover-no-logo.png` e la documentazione.

### Fase 4: cover con logo (dopo l'approvazione della no-logo)

**In sospeso** (indicazione dell'utente: per ora si sistemano solo stella marina e conchiglie).

- [ ] 4.1 Composizione: ambiente + personaggi nelle posizioni della cover con logo + logo completo ricreato.
- [ ] 4.2 Correzioni, approvazione, sovrascrittura di `beatch-slash-cover-logo.png`, documentazione.

## 9. Storico

Una riga per ogni compito concluso: identificativo, cosa è stato fatto, file prodotti, note utili a chi riprende.

- Piano scritto e decisioni dell'utente registrate (sezione 2). Aggiunta su richiesta dell'utente la sequenza disegno completo → correzione dell'agente → verifica dell'utente (sezione 2, punto 7; fase 2b).
- Via dell'utente: fase 0 avviata.
- 0.1: GIMP 3.2.8 collegato, plug-in e server 0.6.0, porta 9890.
- 0.2 (punti 1–3): `vector_art.py` esteso.
  - `target()` accetta `canvas`, `reference_offset`, `style_reference`, `style_reference_layer`, `style_reference_offset`.
  - `run(r, trace=None, only=None, xcf=None)`. Chiave di ricetta `replace_layers`: rifà solo i livelli della ricetta e rimette il blocco al suo posto nella pila (la prima volta in cima). `path_prefix` dà un prefisso ai tracciati. `trace` è facoltativo; `xcf` permette di provare su un file temporaneo.
  - Il ritaglio a `opaque` non richiede modifiche: basta non usare `{"opaque": true}` nelle ricette della cover (scritto nella docstring).
  - Verificato in GIMP su file di prova: dopo una seconda esecuzione l'ordine dei livelli è corretto.
  - Il punto 4 (modulo di ritaglio) è affidato alla corsia dei personaggi; il punto 5 (documentazione) si fa alla fine.
- Nota per le corsie: `cutout.spread` assegna ogni pixel opaco a una parte. Nelle ricette di `trace_reference.py` sulla tela intera serve una parte di raccolta (es. `_other`, ultima regola con un poligono sull'intera tela), altrimenti tutto finisce nelle parti dell'elemento.
- 0.3: riferimenti di lavoro in `C:/Users/stefa/AppData/Local/Temp/beatch_cover_preview/`: `ref_nologo_canvas.png` (2172×1222, con la no-logo in (250, 140)), `ref_nologo.png`, `ref_logo.png`.
- 0.4: creato `Tools/gimp/beatch_slash_cover_background.xcf` (2172×1222, `reference` e `style_reference` nascosti in (250, 140)). Le chiavi comuni a tutte le ricette dell'ambiente sono in `Tools/gimp/recipes/cover_background/_base.json`.
- Corsie avviate in parallelo: personaggi (A+B, con il nuovo modulo `figure_cutout.py`) e tavolozze (P).
- P: tavolozze per materiale in `Tools/gimp/recipes/cover_background/_palette.json` (blocco `style` più un oggetto per materiale con ruoli, contorno, texture, valori della no-logo e `shift` HSV). Script generico `LIB/sample_palette.py`; zone e file grezzi in `TMP/palette/`.
  - Osservazioni: contorno medio dell'ambiente circa 2 px, marrone caldo `#52322c` (mai nero); saturazione media 0,68 nella cover con logo contro 0,52 nella no-logo. Cielo e mare più saturi, fogliame giallo-verde, sabbia più crema; roccia, legno e paglia quasi invariati.
  - Bevande: assenti nella cover con logo, tavolozza proposta e non misurata.
- Istruzioni comuni alle corsie dell'ambiente scritte nella sezione 7. Avviate le 7 corsie C+D, E, F, G, H, I, J+K+L. Le maschere grezze dei personaggi non erano ancora pronte: le corsie le usano se compaiono.
- Errori di rete dell'API hanno interrotto le corsie personaggi, E, G e J+K+L; tutte riprese dal punto in cui si erano fermate.
- H (prima stesura): `06_palm.json`, solo forme scritte a mano (nessun `.trace.json`), 16 livelli `palm_*` (fronde dietro, tronco, noci di cocco, fronde davanti), render circa 7 s. Inventate la corona intera nel margine alto e la parte bassa del tronco dietro il tetto. Richiesti alla corsia i due elementi mancanti: il secondo moncone di tronco (tela circa 450–490, 140–170) e le fronde a sinistra del tetto (tela 250–330, 140–160).
  - Da guardare nella fase 2b: corona più fitta e a ventaglio dell'originale, una fronda gialla che incrocia il tronco, foglioline troppo regolari, posizioni stimate a occhio.
  - La corsia H si è fermata di nuovo per un errore dell'API prima di aggiungere i due elementi mancanti. **Da fare (thread principale): moncone e fronde a sinistra del tetto in `06_palm.json`.**
- C+D: `01_sky.json` (5 livelli `sky_*`: gradiente sull'intera tela con l'orizzonte a y 555, nuvole a cumuli di cerchi in ombra/base/luce/filamenti) e `02_islands.json` (livelli `isl_*`: collina lontana, isolotto, scogliera con roccia e vegetazione). Solo forme scritte a mano, generate da `TMP/lanes/CD/gen_recipes.py`. Render 3,3 s e 8,0 s.
  - Inventati: nuvole nei margini alto e destro, scogliera prolungata da x 1922 a 2172, collina lontana a destra dell'isolotto, isolotto e scogliera interi dietro la rivale.
  - Da guardare nella fase 2b: nuvole più geometriche di quelle della cover con logo; scogliera con meno faccette; isolotto piccolo e poco leggibile; nessuna nuvola in alto a sinistra (dovrebbero coprire quella zona palma e chiosco); scogliera e isolotto senza contorno, come nella cover con logo.
- I: `07_hut.json`, 65 livelli `hut_*` (parete, mensole, bottiglie, pali, bancone, bevande, sgabelli, tenda, lanterna, travi, tetto di paglia), solo forme scritte a mano, render 21 s. Generatore usa e getta in `TMP/lanes/I/gen.py`.
  - Inventati: cima del tetto (apice in (335, 40)), lato sinistro oltre il bordo con palo d'angolo, parete, mensola, bancone e un terzo sgabello; secondo sgabello, bancone, palo e parete dietro i capelli rossi. Il chiosco termina a x ≈ 108 della tela.
  - Da guardare nella fase 2b: il tetto sovrappone il bordo della tenda; riquadro visibile sulla testa del palo principale (tela 296–322, 268–290); puntoni approssimati; margine sinistro 0–108 senza chiosco.
- `vector_art.run`: corretto il caso `replace_layers` + `only`. Prima cancellava anche i livelli della ricetta esclusi da `only`; ora rifà solo quelli in `only` e lascia gli altri.
- Montati nell'`.xcf` dell'ambiente `01_sky` e `02_islands` (script di montaggio `TMP/assemble.py`, parametri `NAMES` e `PREVIEW`).
- F: `04_sand.json`, 18 livelli `sand_*` (base, ondulazioni, conche, ombra del chiosco, bordo umido, solchi, puntinatura, buchetti, 14 sassolini), solo forme scritte a mano, render 44 s. Generatore in `TMP/lanes/F/gen.py`.
  - Inventati: margini, sabbia dietro chiosco, personaggi e rocce, disposizione di ondulazioni, solchi e buchetti.
  - Da guardare nella fase 2b: bordo superiore stimato a occhio (y circa 610 a sinistra, 720–800 al centro, 840 a destra), da far combaciare con la battigia del mare; i sassi medi vicino alla battigia, es. (1265, 796), spettano alla corsia G.
- G: `05_rocks.json`, livelli `rock_*` in cinque gruppi (scogli in mare, scoglio della rivale, massi grandi, sassi in basso, sassi sulla sabbia), ciascuno con corpo, ombra, luce e dettagli, più schiuma per i due gruppi in mare. Solo forme scritte a mano; generatore in `TMP/lanes/G/gen.py`.
  - Inventati: scogli in mare fino a x ≈ 1960, massi fino a x ≈ 2060, sassi in basso fino a y 1222, scoglio della rivale proseguito fino a x 1366.
  - Da guardare nella fase 2b: posizioni approssimate (da ritagli ridotti); solo 5 sassi sulla sabbia; faccette troppo regolari; macchie e crepe appena accennate.
- J+K+L bloccata dopo aver scritto le ricette 08, 09 e 10: ripresa per provarle e chiudere.
- J+K+L: `08_props.json` (livelli `prop_*`: tavola con fiore, barile con ombra a terra, corda; 4,7 s), `09_shells.json` (livelli `shell_*`: conchiglie, stella con ombra; 4,0 s), `10_plants.json` (livelli `plant_*`: gruppi di foglie con contorno, base, ombra e dettagli, ibisco, pistillo; 12,9 s). Solo forme scritte a mano; generatore in `TMP/lanes/JKL/gen.py` (coordinate della cover, +250/+140 nel codice).
  - Inventati: tavola intera (coda sotto il barile e margine), petali dell'ibisco nel margine, 9 foglie nel margine sinistro, 6 foglie dietro il cespuglio in basso a destra, due conchiglie piccole in (332, 919) e (1405, 906).
  - Da guardare nella fase 2b: barile non coperto da foglie e ibisco come nella no-logo; foglie del margine sinistro lunghe e fitte; foglie geometriche con una sola nervatura; cespuglio a destra approssimato con 4 foglie; prima conchiglia più larga del riferimento.
- Personaggi, F e H: un altro errore dell'API.
- E: `03_sea.json`, 19 livelli `sea_*` (mare lontano e vicino a gradiente, fasce, linea dell'orizzonte a y 548, riflessi e scintille, righe d'onda, sabbia bagnata, risacca, 4 file di schiuma), solo forme scritte a mano; disposizione di riflessi e schiuma casuale a seme fisso. Generatore in `TMP/lanes/E/gen.py`.
  - Inventati: mare intero a sinistra di x 810 e dietro i personaggi, margine destro; battigia da (0, 640) a (2172, 828).
  - Da guardare nella fase 2b: battigia stimata, non tracciata; schiuma lontana meno fitta della cover con logo; quota dell'orizzonte rispetto alle isole.
  - Nota: `vector_art.run(..., xcf=...)` non salva il file: il salvataggio lo fa chi chiama (lo fa `TMP/assemble.py`).
- Personaggi: il primo agente si è fermato tre volte per timeout dell'API. Aveva scritto `LIB/figure_cutout.py` (autotest `--selftest` superato) e una bozza della ricetta della coppia in `TMP/work/rc_try.json`, con una falla nel contorno vicino a (542, 811). Affidato a un agente nuovo che riparte da quei file, con l'indicazione di guardare poche immagini piccole.
- 2.1: ambiente montato per intero nell'`.xcf` (ricette 01 → 10, `vector_art` ricaricato in GIMP dopo la fine delle corsie). Prima del salvataggio i livelli erano 246; il montaggio completo richiede circa 100 s.
- H completata dal thread principale: aggiunta la seconda palma (13 livelli `palm2_*`, in fondo a `06_palm.json`, generatore `TMP/lanes/H/gen2.py` che riusa `gen.py`). Il tronco spunta sopra la falda destra del tetto; la corona sta nel margine alto. Le fronde a sinistra (tela 250–330, 140–160) restano coperte dal tetto del chiosco, che sale più in alto che nella no-logo: da guardare nella fase 2b.
- Passaggio di consegne scritto (sezione 10): l'utente sta per esaurire i limiti di utilizzo e passerà il lavoro a Codex.
- Il secondo agente del ritaglio si è fermato per il limite di utilizzo di Claude. Ha lasciato maschere grezze, ricette nel progetto, la correzione di `_save` e prove di coppia e rivale (dettagli nella sezione 10.2, punto 2). Da rieseguire con Codex.
- A.2 (Codex): coppia rigenerata con alpha a 8 bit e verificata su fondo a contrasto. La ricetta ripristina capelli e barba, libera le aperture interne e pulisce piedi e briciole. La chiusura vicino a (542, 811) preserva il piede e separa l'ombra. La palla in mano e le gocce sovrapposte alla guancia restano sulla coppia. Uscite in `TMP/chars/`: figura (441, 183), segni "!" (1020, 175), briciole (490, 407), coordinate della tela.
- Ombra coppia (Codex): `TMP/chars/couple_shadow.json` contiene cinque anelli, incluso un foro, in coordinate della tela. Campioni sRGB: ombra (142, 90, 82), sabbia (252, 196, 124). I raccordi coperti dai piedi sono stimati.
- 2.2 parziale (Codex): salvato `beatch_slash_cover_couple.xcf` con riferimento nascosto, tre livelli visibili di figura/accessori e ombra separata in Moltiplica. Ricetta `cover_couple_shadow.json` con feather 2 px, tinta #563267 e opacità 65%, calcolate sulla sabbia ricostruita. PNG su tela completa in `TMP/chars/`.
- 2.3 parziale (Codex): esportato lo sfondo 2172×1222 da GIMP. Verificate entrambe le palme e i due riferimenti nascosti nel sorgente.
- 0.2 (Codex): confermato in GIMP che `replace_layers` con `only` ricrea il livello selezionato e conserva gli altri livelli e i riferimenti. `vector_art.run` richiede un salvataggio esplicito dell'XCF. Autotest di `figure_cutout.py` superato.
- B.1–B.2 (Codex): maschera rigenerata dalla figura, ripristinato il contorno destro della chioma, verificate le aperture fra ciocche e braccio, isolati cuoricini e scia rosa. Ricostruito il piccolo tratto di ciocca sotto la scia campionando la stessa ciocca con `repairs` di `figure_cutout`. Figura (1251, 213), cuoricini e scia (1201, 264) sulla tela.
- Ombra rivale (Codex): un anello di 76 punti, campioni sRGB (145, 91, 81) e (253, 198, 128). Raccordi sotto i piedi stimati. In GIMP feather 2 px, tinta #5c3e82, opacità 65%, calcolata sulla sabbia ricostruita.
- A–B (Codex): verificati i ritagli e registrati i contorni delle ombre in `TMP/chars/`. Scritto `DONE.txt`.
- 2.2–2.4 (Codex): salvati entrambi gli XCF con figure, accessori e ombre separati. Pubblicati i cinque PNG di composizione in `Assets/Images/`. `TMP/preview_cover_nologo.png` contiene la cover composta nella cornice originale. Scostamenti dei PNG in `TMP/work/offsets_exports.json`.
- 2b (Codex): avviata la correzione dell'ambiente dopo il montaggio della cover completa. Differenze e compiti in sezione 8. Il render di tutte le ricette corrette resta al thread principale.
- 2b H–I (Codex): rimisurati falda e tronco, separate visivamente tenda e paglia, pulita la testata del palo, riempita la sottogronda, aperto lo spazio per una fronda sul margine in alto a sinistra e diradate le foglioline. Controllo GIMP in `TMP/work/qa_hut/`.
- 2b J–L (Codex): foglie davanti al barile e nei cespugli di destra, conchiglie riallineate, stella arrotondata, ombre dell'ibisco attenuate. `09_shells.json` e `10_plants.json` renderizzati e salvati. Il confronto con il riferimento è in `TMP/work/qa_props/`.
- 2b C–G (Codex): nuvole ricostruite con sagome irregolari a due toni, chiusi due vuoti azzurri nella nuvola centrale, ampliato l'isolotto, aggiunte faccette alla scogliera. Mare e sabbia raccordati sulla stessa curva, creste più sottili e 176 forme di schiuma distribuite lungo la costa. Massi con nuove faccette e crepe, sei sassolini aggiunti fra centro e margine destro.
- 2b chiusa (Codex): rendering GIMP salvato, 275 livelli compresi i due riferimenti nascosti. Verificati ritagli, scostamenti, ombre, elementi nei margini e dimensioni di tutti i PNG. Confrontati col riferimento i colori delle ombre sulla sabbia finale. L'ambiente resta più geometrico soprattutto nel fogliame, nella paglia e nelle rocce. Anteprima per la verifica dell'utente in `TMP/preview_cover_nologo.png`.
- Verifica dell'utente: la composizione nel suo insieme risulta artificiale. Cielo, nuvole, mare e rocce in acqua e vicino alla riva sono riusciti. L'utente chiede di rifare ibisco, piante, rilievi lontani, due rocce in primo piano, chiosco e stella marina. La fase 3 ora prevede una correzione per turno, con anteprima aperta e pausa per la verifica. Pronto il piano, grafica in attesa di avvio.
- 3.1 (Codex): ibisco ricostruito; approvato dall'utente. Lenti e disconnessioni dovuti a server MCP orfani (`gimp-mcp-plugin.exe` e altri lasciati dai client) e a immagini accumulate in GIMP: processi chiusi e regola di chiusura dopo ogni passo aggiunta. L'utente chiede di rifare tutte le foglie della tela (nuovo punto 3.4b).
- 3.2 (Claude): cespo a sinistra ricostruito con il nuovo modulo generico `LIB/foliage.py`: foglie larghe a metà in luce e metà in ombra, nervatura, riflesso sulla piega, massa scura interna, attacco comune e ombra di contatto. Sostituiti i livelli `plant_margin_left_*`, `plant_hib_back_*`, `plant_hib_front_*` e `plant_barrel_leaf_*` con `plant_left_contact`, `_back`, `_mid` e `_front`. Il montaggio non elimina dall'XCF i livelli tolti dalla ricetta: rimossi a mano, ora 258 livelli. Cespo alzato di 40 px su richiesta dell'utente, così il fiore sta dentro il fogliame. Poi, per legare fiore e foglie nella stessa pianta: ramo visibile dal fiore alla sabbia, foglie attaccate lungo il ramo e tre foglie che spuntano da dietro i petali. Infine due foglie davanti ai petali bassi (`plant_left_over`, sopra il fiore), ombra del fiore sulle foglie (`plant_left_flowershade`, Moltiplica) e variazione ripetibile di larghezza, piega, punta ritorta, ondulazione e forma (`vary` nella specifica, nuove chiavi `curl`, `wave`, `belly` di `foliage.py`). XCF a 260 livelli. 3.2 approvata dall'utente.
- 3.3–3.4 (Claude): ciuffo di foglie appuntite a ventaglio ai piedi del masso, come nell'originale, e cespuglio d'angolo con foglie lunghe ad arco e punta ricadente, massa interna e ombra di contatto. Sostituiti i livelli `plant_bush_r1_*` e `plant_bush_r2_*` (eliminati anche dall'XCF, ora 237 livelli). Il cespuglio d'angolo poggia in parte sulla roccia in primo piano a destra, da rivedere con la 3.8. 3.3 e 3.4 approvate dall'utente.
- 3.4b (Claude): fronde delle due palme ricostruite con le fronde di `LIB/foliage.py` (nervatura che si alza e ricade, poche foglioline larghe e lunghe che pendono), da `PRJ/Tools/gimp/recipes/foliage/cover_palms.json`. In `06_palm.json` i livelli `palm*_frond_*` e `palm2_left_frond` diventano `palm2_fronds_back`, `palm2_fronds_front`, `palm_fronds_back`, `palm_fronds_front`; tronchi e noci invariati. XCF a 221 livelli; montaggio delle palme circa 160 s. Ricetta precedente in `TMP/work/leaves/06_palm_before.json`.
- 3.4b, verifica dell'utente: palme **respinte**. Colori giusti; resa sbagliata: sembrano foglie comuni attaccate a un fil di ferro (rachide visibile e sottile), partono lontane dal tronco invece che dalla sua cima. La versione vecchia ricalcava meglio l'originale: fronde a ventaglio che nascono dal tronco, foglioline strette e fitte a pettine. L'utente rivede a mano l'elenco dei punti della fase 3 prima della correzione.
- 3.4b, rifacimento (Claude): fronde ricostruite come lame arcuate con un pettine di foglioline (nuovi `blade_geometry`/`blade_ops` e gruppo `blades` in `LIB/foliage.py`; nuovo modificatore `sharpen` in `LIB/vector_art.py`). Specifica `foliage/cover_palms.json` generata da `TMP/work/palms2/make_spec.py`. Durante la verifica l'utente ha chiesto punte più affilate, fronde che nascano dal tronco, il cerchietto della chioma davanti alle fronde anche sulla palma di sinistra e le noci nascoste. Ora: picciolo spesso dentro la cima del tronco, fogliolina finale a punta, cerchietto `palm_crown`/`palm2_crown` sopra le fronde, noci `palm2_crown_nuts` sotto le fronde davanti. XCF a 224 livelli, PNG dell'ambiente esportato. Confronto in `TMP/work/palms2/confronto_palme.png`, cover composta in `TMP/work/palms2/cover_new.png` (`preview_cover_nologo.png` era bloccato da un visualizzatore e non è stato aggiornato). Ricetta precedente in `TMP/work/palms2/06_palm_before.json`.
- 3.4b approvata dall'utente.
- 3.4c (Claude), cespo a sinistra: ombra di contatto più scura con ombre sotto le punte (`plant_left_contact`, Moltiplica 75%) e nuovo bordo di sabbia `plant_left_sand` fra le foglie medie e quelle davanti, nello stesso tono della sabbia in ombra, con linea di cresta e briciole. Corretto l'aggancio dei gruppi della specifica (`before` = `plant_r1_contact`): rigenerandola, il cespo finiva sopra l'ibisco. XCF a 225 livelli, PNG dell'ambiente esportato. Confronto in `TMP/work/bush3/confronto_cespo.png`, cover in `TMP/work/bush3/cover_new.png`; ricetta e specifica precedenti in `TMP/work/bush3/`. Il cespuglio di destra poggia sulla roccia in primo piano (che arriva fino a x 2060 e al bordo inferiore): si sistema con la 3.8.
- 3.4c approvata dall'utente per il cespo a sinistra.
- 3.5 (Claude), isolotto: ricostruito con il generatore `TMP/work/islet/gen.py`, che riscrive in `02_islands.json` i livelli dell'isolotto nella loro posizione. Roccia a lastre spigolose (`isl_islet_rock_base`, `_lit`, `_light`, `_cast`) con la parete destra verticale in luce e il fianco sinistro a gradini fino all'orizzonte (y 549); chioma in un solo livello `isl_islet_veg`: una massa continua scura e 8 lobi irregolari dipinti dal fondo al davanti, ciascuno con quattro toni campionati dal riferimento. Sfocatura 0,6 su tutti i livelli per la distanza. Eliminati dall'XCF `isl_far_hill` e `isl_islet_veg_deep/_mid/_base/_light`; XCF a 222 livelli, PNG dell'ambiente esportato. Confronto in `TMP/work/islet/confronto_isolotto.png`, cover in `TMP/work/islet/cover_new.png`; ricetta precedente in `TMP/work/islet/02_islands_before.json`.
- 3.5, verifica dell'utente: roccia approvata; da correggere la chioma (un grosso blob innaturale), l'ombra sotto la chioma (la faceva sembrare un corpo estraneo appoggiato) e la mancanza di tridimensionalità. Correzione (Claude): tolta l'ombra; roccia alzata a cupola sotto gli alberi; ogni lastra ha il lato sinistro in luce, il piano destro più scuro e una fascia lavanda di fianco, più un'ombra in Moltiplica sul lato destro dell'isola e sulla linea dell'acqua (`isl_islet_rock_shade`); chioma di 14 ciuffi d'albero sovrapposti, ognuno sfumato dal giallo-oliva in alto al verde-azzurro in basso, con macchie di luce sfumate e senza bordi scuri. Provate e scartate: chiome a dischi su colonne a prisma (sembravano galleggiare su scatole) e ciuffi schiacciati con bordo scuro (pile di frittelle). Livelli dell'isolotto: `isl_islet_rock_base`, `_rock_lit`, `_rock_shade`, `isl_islet_veg`; XCF a 221 livelli.
- 3.5, seconda verifica dell'utente: chioma ancora fatta di cerchi e sfere, roccia poco credibile; chiesto di ricalcare l'originale. Ricalco (Claude) con il nuovo modulo generico `LIB/tone_trace.py`: divide il riferimento in nove zone di tono (tre verdi e due verdi-azzurri della chioma; pesca, rosa, lavanda e blu della roccia), esclude i pixel coperti dai personaggi (maschere grezze in `TMP/chars/`), prolunga a specchio le parti nascoste dentro il contorno `extend`, liscia i confini e scrive anelli vettoriali. Ricetta del tracciamento `cover_background/02_islands.tone.json`, uscita `02_islands.trace.json` (letta da `assemble.py`); colori dipinti = campioni con saturazione ×1,12. Livelli: `isl_islet_rock_base` (sagoma intera, sfumata dal verde alla lavanda, più la fascia sotto l'orizzonte) e `isl_islet_tones` (le nove zone, allargate di 0,8 px); sfocatura 0,6. XCF a 219 livelli. Il generatore `TMP/work/islet/gen.py` legge il tracciato; le versioni precedenti sono in `gen_v1.py` e `gen_v2.py`.
- 3.5: ricalco approvato dall'utente, che lo sceglie come metodo per ogni creazione in GIMP con un riferimento (decisione 2.9). Aggiunti i punti 3.10b (ricalco degli elementi rifatti a mano, dopo i punti principali) e 3.10c (personaggi ricalcati, alla fine). Richiesto per la 3.5 l'allargamento a mano della parte dell'isolotto coperta dal ragazzo.
- Aggiunto su richiesta dell'utente il punto 3.4c (appoggio a terra dei cespugli); nota sulla prospettiva del chiosco aggiunta alla 3.9.
- Libreria (Claude): `LIB/tone_trace.py` ora accetta `patch` (PNG dipinto a mano nei toni campionati: riempie solo i pixel nascosti, che vengono ricalcati e lisciati come quelli visibili), `areas` (più soggetti in un solo tracciato), `edge_blend` (le mezze tinte tono-sfondo restano al tono: niente bordi lilla sul fogliame contro il cielo), `open` (assorbe i tratti di 1–2 px che prendono un tono estraneo), `clip` (poligoni fuori dai quali tutto è sfondo: serve dove la sabbia ha gli stessi colori della roccia in luce), `cover` (colori di ciò che sta davanti, trattati come nascosti) ed `exclude` a poligono. `LIB/vector_art.py`: chiave di livello `offset` [dx, dy] (sposta il livello disegnato); `LIB/foliage.py` la copia dai gruppi. Autotest di `tone_trace` superato.
- 3.5 (Claude), isolotto completato: nella fessura fra braccio e busto del ragazzo l'originale mostra una collina lontana azzurra e rocce lavanda alla base, quindi l'isolotto continua a sinistra. Ricalcata anche quella parte (maschera precisa del ragazzo `TMP/chars/couple_fine_mask.png`, ricavata dal ritaglio e allargata di 2 px, al posto di quella grezza); la parte coperta dal braccio e dal busto è dipinta a mano in `02_islands.patch.png` (ciuffi con il cappello in luce fino al bordo, colonne di roccia con la faccia in luce a destra, collina lontana che scende in mare a x ≈ 1004 e dietro la rivale fino a x ≈ 1388). Nuovo livello `isl_far_hill` (tono `isl_far`, sotto l'isolotto). Generatori `TMP/work/s35/make_patch.py` e `TMP/work/s35/gen.py`; versioni precedenti di ricette e tracciato in `TMP/work/s35/`.
- 3.6 (Claude), scogliera ricalcata: seconda area di `02_islands.tone.json` (12 toni da k-means, `edge_blend` 0,5, `open` 1, maschera precisa della rivale `TMP/chars/rival_fine_mask.png`). Patch `02_islands_cliff.patch.png`: pendio sotto il gomito della rivale e promontorio nel margine destro (faccia rosa, colonne viola in ombra, faccia rosa più bassa, scogli fino a x ≈ 2112, chioma che scende). Gli 11 livelli `isl_cliff_*` disegnati a mano sono sostituiti da `isl_cliff_base` e `isl_cliff_tones` ed eliminati dall'XCF. Corretta su segnalazione dell'utente una fessura di cielo fra chioma e roccia all'estremità del promontorio: la roccia della patch ora passa sotto la chioma. Generatori `TMP/work/s36/make_patch.py`, `TMP/work/s36/gen.py`, `TMP/work/s36/drop_layers.py`.
- 3.7–3.8 (Claude), rocce in primo piano: nell'originale sono due massi bassi e larghi con contorno scuro, di cui si vede solo la sommità; ricalcate da `05_rocks.tone.json` (due aree, `clip` sul contorno misurato, `exclude` a poligono sulle foglie) con corpo sotto la cornice dipinto in `05_rocks.patch.png` a grandi piani angolosi. I livelli `rock_bottom_*` sono sostituiti da `rock_left_*` e `rock_right_*` (ombra di contatto, contorno, base, toni) ed eliminati dall'XCF. Prima prova: cespo con l'ibisco abbassato di 32 px (`offset`), scartata perché il fiore si allontanava dalla posizione dell'originale; ora il cespo resta dov'era e il corpo inventato della roccia è schiacciato (base a y 1095–1108), così la base del cespo sta davanti a quella della roccia. Variate anche larghezze e luci delle colonne di roccia alla base sinistra dell'isolotto, che sembravano una staccionata. Cespuglio d'angolo: ombra di contatto e bordo di sabbia come il cespo a sinistra, bordo scurito e allargato fino a coprire la massa scura; ora sta davanti alla roccia, non sopra. XCF a 216 livelli, PNG dell'ambiente esportato. Generatori `TMP/work/s37/make_patch.py`, `TMP/work/s37/gen.py`; ricette e specifiche precedenti in `TMP/work/s37/`.
- Confronti originale / vecchio / nuovo per 3.5–3.8 in `TMP/work/s3_final/` (`3.5_isolotto.png`, `3.6_scogliera.png`, `3.7_roccia_sinistra.png`, `3.8_roccia_destra.png`), cover composta `cover_vecchio.png` / `cover_nuovo.png`, tela estesa `tela_estesa_vecchio.png` / `tela_estesa_nuovo.png`; script `sheets.py`. Stato precedente dell'ambiente in `bg_before.png`.
- 3.5–3.8 approvati dall'utente. Nuovo punto 3.8b (cespo con l'ibisco come un'unica pianta: il fiore guarda a destra, le foglie pendono a sinistra), da fare prima della 3.9.
- 3.8b (Claude), in attesa di verifica: chiarimento dell'utente con uno schizzo. Il corpo del cespo saliva dalla base a destra verso l'alto a sinistra, mentre il fiore parte in basso a sinistra e si apre verso destra: la pianta faceva uno zigzag. Due prove scartate prima del chiarimento: foglie riorientate a una a una verso destra (il cespo diventava una colonna stretta) e fusto inclinato a destra con foglie a ventaglio. Soluzione: specchiato il cespo della versione approvata attorno a x 270 (foglie, fusto, massa scura, bordo di sabbia, ombre di contatto e le due foglie sopra i petali), senza toccare il fiore né `plant_left_flowershade`. Con `lit` "up", `bend` e `curl` non cambiano segno; numero e ordine delle foglie invariati, quindi la variazione `vary` resta la stessa. Script `TMP/work/s38b/mirror_spec.py <src> <dst> 270 plant_left_flowershade`; specifica e ricetta precedenti in `TMP/work/s38b/cover_left_bush_before.json` e `10_plants_before.json`, ambiente precedente `bg_before.png`. XCF a 216 livelli, PNG dell'ambiente esportato. Confronto `TMP/work/s38b/3.8b_cespo_ibisco.png`, cover `TMP/work/s38b/cover_nuovo.png`, tela estesa `tela_estesa_nuovo.png`.
- 3.8b approvata dall'utente ("ora è perfetto"). Avviata la 3.9.
- 3.9 (Claude), in attesa di verifica: chiosco ricalcato con `tone_trace.py` invece che ridisegnato a mano. Il vecchio era frontale. Nell'originale il fronte fugge verso destra (gronda e tenda scendono a destra, il palo sinistro è più largo di quello destro): il ricalco ne riprende la prospettiva. Ricetta di tracciamento `cover_background/07_hut.tone.json` (un'area, 19 toni da k-means sulla zona del chiosco, cielo come sfondo, `edge_blend` 0,5, `clip` sulla sagoma del chiosco anche nei margini, `extend` uguale). Esclusioni: maschera della coppia allargata di 3 px (`TMP/work/s39/couple_mask_grown.png`), briciole (`crumbs_mask.png` più un poligono sulla nuvola di briciole), poligoni di tavola, barile e cespo. Patch `cover_background/07_hut.patch.png`, dipinta nei campioni:
  - parte dietro i capelli rossi: palo d'angolo destro a x 534–559 (oltre si vede il cielo), parete, mensola in ombra, fine del bancone, secondo sgabello, ultima striscia e smerlo rossi della tenda;
  - campata nel margine sinistro: palo d'angolo con testa di trave, saette, parete a tavole con mensola e bottiglie, bancone con bicchiere e barattolo, terzo sgabello;
  - tetto oltre la cornice: falda sinistra, colmo a y ≈ 108 e falda destra fino al tronco della palma, con ciuffi irregolari e fessure scure come la paglia ricalcata.

  Sotto tavola, barile e cespo il riempimento è automatico (`mirror`), perché restano coperti. Livelli: i 66 `hut_*` disegnati a mano sono sostituiti da `hut_contact` (Moltiplica 60%), `hut_base` e `hut_tones` (tono più scuro per ultimo, così i contorni restano). Il blocco resta fra `palm_crown` e le prime prop: prima del montaggio `hut_wall_base` è stato rinominato `hut_contact`, perché `replace_layers` mette in cima i livelli nuovi. Poi i vecchi sono stati eliminati con `drop_layers.py`. XCF a 153 livelli, PNG dell'ambiente esportato. Script in `TMP/work/s39/`: `common.py` (ritaglio, esclusioni), `kmeans.py`, `make_tone.py`, `make_patch.py`, `gen.py`, `quick.py` (anteprima rapida di un tracciato fuori da GIMP). Il legno dipinto nella patch ha bordi leggermente irregolari, tavole di larghezza variabile con venature e nodi, e pali rastremati con luce ondulata. Così la campata nel margine non sembra fatta di rettangoli accanto alla parte ricalcata. L'ombra di contatto arriva fino a x ≈ 605 (fine dello sgabello). Nessun'altra ricetta fa riferimento ai vecchi livelli `hut_*`. Lezione da riportare nelle guide dopo l'approvazione: con `replace_layers` un blocco con nomi tutti nuovi finisce in cima alla pila; per tenerlo al posto del vecchio basta rinominare prima il livello più basso del vecchio blocco con il nome del primo livello nuovo. Precedenti: `07_hut_before.json`, `bg_before.png`, `xcf_before.xcf`. Confronto `TMP/work/s39/3.9_chiosco.png`, cover `cover_nuovo.png`, tela estesa `tela_estesa_nuovo.png`.

- 3.9 seconda versione (Claude), in attesa di verifica. Note dell'utente sulla prima: parte sinistra e tetto in alto a sinistra in uno stile diverso, senza profondità; terzo sgabello con la sola seduta; sgabello a destra fatto a metà; barile poco tridimensionale. Su proposta dell'utente il chiosco ora continua oltre il bordo sinistro della tela, così la sua fine non si vede (anche nella cover con logo prosegue a sinistra del palo). La parte nuova non è più dipinta a mano: `make_patch.py` copia pezzi dell'originale (`ref_nologo_canvas.png`) spostati di una campata (247 px): palo con nodi ripetuti fino a terra, saette e trave in cima, parete a tavole, mensola e bottiglie, bancone, barattolo e bicchiere, fronte del bancone, sgabello centrale (la gamba dietro la corda del barile è lo specchio di quella destra rispetto all'asse x 447; sotto y 745 si copiano solo le gambe, non la sabbia). Bottiglie e bicchieri si incollano con una maschera dei soli oggetti (pixel più chiari della parete, allargati di 2 px). Il tetto ripete le file di paglia visibili: file della gronda in copie alternate specchiate (ogni giunta unisce la stessa colonna), coperte da copie dritte con bordi frastagliati sui ciuffi, così gli assi dello specchio non si vedono; le file alte sono ridotte a 0,8 perché la falda si allontana. Tutto si costruisce frontale e poi va in prospettiva con una trasformazione proiettiva (`common.py`: punto di fuga (1900, 548), perno x 290 dove inizia il palo sinistro originale, scala 1,18 al bordo della tela): travi, gronda, mensola e bancone salgono verso sinistra, la base scende. La striscia originale x 250–289 è esclusa dal ricalco e ricostruita dalla patch deformata, così la piega cade sul palo. Il palo sinistro originale continua fino a terra dietro la tavola (prima si interrompeva a y ≈ 400). Lo sgabello a destra è lo sgabello centrale ridotto a 0,8, con un'esclusione su tutta la sua sagoma: la patch lo possiede intero. A sinistra della cornice il fronte del bancone poggia sulla sabbia (y 760 prima della prospettiva); scendono più in basso solo il palo e le gambe dello sgabello. Una foglia gialla davanti alla parete a x 250 è esclusa. L'ombra di contatto è un poligono che segue la base in prospettiva. Riquadro dell'area [0, 0, 662, 870]. Il barile resta per ora quello della ricetta `08_props.json` e passa alla 3.10b. Versione precedente in `TMP/work/s39/v1_*` (ricetta, tracciato, patch, anteprime), `make_patch_v1.py`, `make_patch_v2.py`, `common_v2.py`. Confronto `TMP/work/s39/3.9_chiosco.png` (originale / nuovo), cover `cover_nuovo.png`, tela estesa `tela_estesa_nuovo.png`.

- 3.9 terza versione (Claude), in attesa di verifica. Note dell'utente sulla seconda: chiosco quasi perfetto; prospettiva scarsa; sabbia separata sotto lo sgabello di sinistra; palo sopra la tavola spezzato; poi ultimo smerlo della tenda con un riquadro rosso e una macchia rossa sulla riga crema, sgabello destro con un pezzo in più e stacco netto con la sabbia, palo destro con sbavature, palo centrale spezzato in orizzontale, barile troppo finto e piatto. Correzioni nella patch e nelle esclusioni (`common.py`, `make_patch.py`):
  - prospettiva: trasformazione proiettiva già descritta nella seconda versione; le file alte del tetto ridotte a 0,8;
  - pali: tutti i pali copiati (nuovo palo a sinistra, continuazione del palo sinistro originale dietro la tavola, palo d'angolo destro) ripetono un solo segmento del palo originale (`[285..326]×[335..378]`, 43 px), così i nodi cadono a passo regolare; il palo destro è lo stesso segmento stretto a 25 px, con un'esclusione su tutta la colonna x 532–561;
  - tenda: tolte la striscia e lo smerlo rossi dipinti a mano; l'ultimo smerlo è color crema con il contorno, come nell'originale; la fascia d'ombra fra l'ultima riga crema e lo smerlo rosso, che il ricalco isolava come macchia, è esclusa e ridipinta nel rosso dello smerlo;
  - sabbia: lungo il piede del bancone (y ≥ 752, x 250–640) e oltre il palo destro (x ≥ 560, y ≥ 398) il ricalco lascia vedere la spiaggia; gli sgabelli centrale e destro sono copie dello sgabello pulito, senza la sabbia fra i piedi; lo sgabello destro è ritagliato per parti (seduta, quattro gambe, traversa) e sta libero davanti alla spiaggia;
  - barile con la corda: ricalcato dall'originale con `make_barrel.py` (ricetta `cover_background/08_props.tone.json`, 14 toni da k-means sul barile visibile, ritaglio sulla sagoma di barile e corda, foglie escluse per colore, fiore con un poligono, patch `08_props.patch.png` con il contorno del fianco sinistro coperto dalle foglie). `gen_props.py` sostituisce in `08_props.json` i 13 livelli disegnati a mano di barile e corda con `prop_barrel_traced_base` e `prop_barrel_traced_tones`; l'ombra a terra resta. Nell'XCF `prop_barrel_outline` è stato rinominato `prop_barrel_traced_base` prima del montaggio e i vecchi livelli tolti con `drop_layers.py`. XCF a 142 livelli, PNG esportato. Precedenti: `TMP/work/s39/08_props_before.json`, `xcf_v2.xcf`.

- 3.9, sgabelli copiati (Claude), in attesa di verifica. Nota dell'utente: sgabello sinistro e destro ancora sbagliati. Causa: nella copia pulita dello sgabello centrale la parte coperta dalla corda era lo specchio della parte destra, quindi la traversa usciva anche a sinistra e la gamba specchiata era chiara. Ora in `clean_stool()` la parte coperta (x < 431, y ≥ 668) ha come fondo una colonna fra due gambe (x 452), con le righe della traversa sfumate fra quelle sopra e sotto, e la gamba posteriore sinistra continua quella visibile, nei suoi colori in ombra, fino a y 764 come l'altra gamba posteriore.

- 3.9, sgabelli ritagliati per parti (Claude), in attesa di verifica. Nota dell'utente: sgabello sinistro e destro ancora con problemi (fondo scuro a blocchi fra le gambe; a destra il piede del palo d'angolo fra le gambe sembrava una quinta gamba). Ora gli sgabelli copiati si incollano con `stool_mask()`: seduta, quattro gambe e traversa a destra, poligoni sullo sgabello centrale allargati di 2 px per il contorno, senza sabbia ai piedi; fra le gambe si vede il bancone della scena. Lo sgabello destro sta all'angolo, subito oltre il palo (seduta da x 563), libero davanti alla spiaggia; esclusione `right_stool` e ritaglio allargati fino a x 662.

- 3.9, sgabello destro tolto (Claude), in attesa di verifica. Su indicazione dell'utente (contorno marrone attorno a ogni parte, non sembrava del chiosco) lo sgabello destro non c'è più: l'esclusione `right_stool` toglie quello originale e oltre il palo d'angolo si vedono mare e sabbia dei livelli sottostanti.

- 3.9 approvata dall'utente ("decisamente meglio"), insieme al barile ricalcato. Guide e file di contesto aggiornati. Prossimo punto: 3.10 stella marina.

- Su indicazione dell'utente il piano si restringe: dopo la 3.9 si sistemano solo stella marina e conchiglie (punto 3.10). 3.10b, 3.10c, 3.11, 3.12 e la fase 4 restano in sospeso.

- 3.10 (Claude), in attesa di verifica: stella marina e conchiglie ricalcate con `tone_trace.py` al posto delle forme disegnate a mano (stella piatta a cinque punte con una riga di puntini per braccio, conchiglie a mezzaluna con righe dritte). Ricetta di tracciamento `cover_background/09_shells.tone.json`, tre aree: stella (`clip` = sagoma del contorno scuro chiuso, riempita e lisciata), conchiglia a sinistra e conchiglia a destra (`clip` a poligono su guscio e buche nella sabbia). Lezioni: (1) con i toni di k-means le mezze tinte di passaggio (marroni fra contorno e arancio, rosati fra righe e crema) diventano macchioline sparse e il render GIMP risulta sporco: si usano 4–5 toni scelti per materiale (contorno, ombra, base, luce, puntini o righe), con le mezze tinte marroni come secondo campione dell'ombra; (2) lo sfondo delle conchiglie va campionato solo sulla sabbia chiara attorno (luminanza > 150), altrimenti il marrone delle buche diventa sfondo e il contorno sparisce; (3) dentro un contorno chiuso lo sfondo è solo un colore fittizio, altrimenti i puntini crema della stella somigliano alla sabbia e diventano buchi; (4) `open` 1 cancella contorni e righe larghe 2 px: su oggetti così piccoli si lascia a 0 e si tolgono i puntini con `sigma` 1,1 e `min_area` 10 (stella: `sigma` 0,75 e `min_area` 3, per tenere i 31 puntini). Ombra a terra della stella: livello Moltiplica dalla sagoma tracciata spostata in basso a sinistra e sfumata. Le due conchiglie piccole inventate (dentro la cornice, non presenti nell'originale) sono copie degli anelli della conchiglia a sinistra ridotte a 0,30 e 0,27, nelle loro posizioni di prima: da togliere se l'utente non le vuole. Gli 11 livelli disegnati a mano (`shell_dent`, `shell_outline`, `shell_base`, `shell_shade`, `shell_stripes`, `shell_star_*`) sono sostituiti da `shell_star_shadow`, `shell_traced_base` e `shell_traced_tones` (prima del montaggio `shell_dent` rinominato `shell_star_shadow`, il vecchio `shell_star_shadow` messo da parte) ed eliminati dall'XCF, ora a 134 livelli; PNG dell'ambiente esportato. Script in `TMP/work/s310/`: `make_tone.py` (ricetta di tracciamento), `gen.py` (conchiglie piccole nel tracciato e livelli di `09_shells.json`), `pv2.py` (anteprima antialiasata fuori da GIMP), `rename.py`, `deliver.py`. Precedenti: `09_shells_before.json`, `bg_before.png`. Confronto `TMP/work/s310/3.10_stella_conchiglie.png` (originale / vecchio / nuovo), cover `cover_nuovo.png`, tela estesa `tela_estesa_nuovo.png`, fascia a grandezza reale `fascia_1a1.png`.

- 3.10 approvata dall'utente ("ora l'immagine è proprio come la volevo"), conchiglie piccole comprese. Nessun punto attivo: 3.10b–3.12 e fase 4 in sospeso.

- L'utente tiene i ritagli dei personaggi (non vanno ricalcati: 3.10c non necessario) e dichiara concluso il piano. Al posto di 3.11, 3.12 e della fase 4 ha chiesto le immagini finite: logo intero, logo solo testo, sfondo vuoto, sfondo con i personaggi, sfondo con personaggi e logo intero, immagine quadrata con il logo in alto e i personaggi sotto.
- Immagini finite (Claude): nuovo modulo generico `LIB/compose_variants.py` (gruppi importati nel progetto principale, varianti con visibilità, scala e spostamento per livello, livelli della scena portati sopra un gruppo, tela e ritagli, esportazioni; gruppi in pass-through, altrimenti le ombre in Moltiplica non si fondono con la sabbia). Ricetta `PRJ/Tools/gimp/recipes/cover_outputs.json`. Nel progetto `beatch_slash_cover_background.xcf` ci sono ora i gruppi `characters` e `logos`; progetti derivati `beatch_slash_cover_logo.xcf` e `beatch_slash_cover_square.xcf`. Esportati in `Assets/Images/` sfondo, cover senza logo e cover con logo (1672×941 e versione ampia), quadrata 1024×1024; sovrascritte le due cover originali, che restano nei livelli nascosti e in `TMP/ref_nologo.png`/`ref_logo.png`. Il PNG della tela estesa dell'ambiente ora si chiama `beatch-slash-cover-background-extended.png`. Correzioni chieste dall'utente: nella cover con logo cespo con l'ibisco e rocce in primo piano sopra i personaggi (il fiore copre la gamba della rossa), rivale più lontana dalla coppia, logo più piccolo nell'angolo in alto a destra, versione ampia ritagliata a [167, 0, 2172, 1128]; nella quadrata logo e personaggi spostati insieme a destra di 430 px, perché il logo stia sul cielo a destra delle palme (il chiosco esce dall'inquadratura). Rivale: contorno della coscia sinistra spezzato dal poligono `envelope` di `cover_rival.json`, allargato e ritaglio rifatto da `TMP/ref_nologo.png`; XCF e PNG della rivale rigenerati. Prove e anteprime in `TMP/work/final/`, ritaglio precedente della rivale in `TMP/work/final/chars_before/`, XCF dell'ambiente prima dei gruppi in `TMP/work/final/background_before.xcf`.
- Cover con logo: rivale riportata 32 px a sinistra (spostamento +28 invece di +60), il minimo perché il piede non stia sopra la stella marina. I PNG dei pezzi (coppia, rivale e loro ombre) spostati da `Assets/Images/` a `PRJ/Tools/gimp/parts/`, su richiesta dell'utente: in `Assets/Images/` restano solo immagini finite.
- **Piano concluso** su indicazione dell'utente.

## 10. Passaggio di consegne

Sezione per chi riprende il lavoro (Codex o una nuova sessione di Claude). Va tenuta aggiornata: a ogni ripresa si corregge lo stato qui sotto e si aggiunge una riga nello storico (sezione 9). Abbreviazioni come nella sezione 7: `PRJ` progetto, `LIB` libreria GIMP della skill, `TMP` = `C:/Users/stefa/AppData/Local/Temp/beatch_cover_preview`.

### 10.1 Stato attuale

- **Piano concluso.** Immagini finite in `Assets/Images/`, generate da `PRJ/Tools/gimp/recipes/cover_outputs.json` con `LIB/compose_variants.py` (vedi `Docs/CODE_MAP.md`). Le voci qui sotto descrivono il materiale di lavoro.

- **Materiale disponibile:** fasi 0–2b. Ritagli verificati e ombre misurate, progetti GIMP, PNG e prima composizione della cover senza logo. La verifica dell'utente ha richiesto una nuova rifinitura dell'ambiente. L'XCF dell'ambiente misura 2172×1222 e contiene 134 livelli, compresi `reference` e `style_reference` nascosti.
- **Ricette dell'ambiente** (fonte di verità; l'`.xcf` si rigenera da queste): `PRJ/Tools/gimp/recipes/cover_background/01_sky.json` … `10_plants.json`, più `_base.json` (chiavi comuni) e `_palette.json` (tavolozze). `02_islands.json` e `05_rocks.json` usano i tracciati `02_islands.trace.json` e `05_rocks.trace.json`, generati da `tone_trace.py` con le ricette `.tone.json` e le patch `.patch.png` accanto; le altre ricette hanno forme scritte a mano.
- **Generatori delle ricette** (usa e getta, fuori dal progetto): `TMP/lanes/<corsia>/gen.py` (corsie `CD`, `E`, `F`, `G`, `H`, `I`, `JKL`), e per la palma anche `TMP/lanes/H/gen2.py`.
  - Rieseguire un `gen.py` **sovrascrive** la sua ricetta.
  - Per la palma va eseguito `gen2.py`, che esegue `gen.py` e poi aggiunge la seconda palma.
  - Correggere direttamente il JSON va bene uguale; in quel caso il generatore resta indietro.
  - **Superati, da non rieseguire:** `TMP/lanes/I/gen.py` (riscriverebbe `07_hut.json` con il vecchio chiosco a 66 livelli; ora lo genera `TMP/work/s39/gen.py`) e, per isolotto e scogliera, `TMP/lanes/CD/gen.py` (sostituito da `TMP/work/s35/gen.py` e `s36/gen.py`).
- **Libreria generica** (`LIB` = `C:/Users/stefa/.agent-knowledge/game-tools/scripts/gimp`): `vector_art.py` esteso (tela allargata, `style_reference`, `replace_layers`, `path_prefix`, `xcf=`, correzione di `only`); nuovi `figure_cutout.py` (ritaglio dei personaggi, `--selftest` superato) e `sample_palette.py` (tavolozze).
- **Montaggio:** `TMP/assemble.py`. Nella console `call_api`, passare `NAMES` e `PREVIEW` nel namespace di `exec`. Rigenera le ricette indicate, salva l'XCF ed esporta il PNG quando `PREVIEW` è un percorso. Per l'ambiente intero usare le ricette da `01_sky.json` a `10_plants.json` in ordine, in più chiamate se necessario. Il PNG completo è `Assets/Images/beatch-slash-cover-background.png`.
- **Sorgenti e uscite:** tre XCF in `Tools/gimp/`, cinque PNG in `Assets/Images/`, anteprima composta in `TMP/preview_cover_nologo.png`. Le due cover originali sono ancora quelle di riferimento. Per rigenerare gli XCF e le esportazioni dei personaggi riusare `TMP/work/render_figures.py` con il namespace di `TMP/work/figure_jobs.json` nella console GIMP. Per ritagliare i PNG esportati e rigenerare l'anteprima, eseguire `TMP/work/compose_exports.py TMP/work/cover_exports.json` con Python e Pillow.
- **Ritaglio completato:** PNG, maschere, scostamenti e contorni ombra in `TMP/chars/`. Per rigenerare anche la ciocca sotto la scia, usare la versione di `figure_cutout.py` con `repairs`. Confronti ingranditi in `TMP/work/couple_codex/` e `TMP/work/rival_codex/`.
- **Ripresa corrente:** 3.5 isolotto, 3.6 scogliera, 3.7 roccia a sinistra e 3.8 roccia a destra approvati. 3.8b cespo con l'ibisco e 3.9 chiosco approvati. **3.10 stella marina e conchiglie approvate** (`09_shells.json`; per rigenerarle `make_tone.py`, `tone_trace.py`, `gen.py` in `TMP/work/s310/`, poi `assemble.py` con `NAMES=['09_shells.json']`); 3.10b–3.12 e fase 4 in sospeso. XCF dell'ambiente a 134 livelli. 3.9 chiosco e barile approvati: per rigenerarli `make_patch.py`, `make_tone.py`, `tone_trace.py`, `gen.py` (chiosco) e `make_barrel.py`, `tone_trace.py`, `gen_props.py` (barile) in `TMP/work/s39/`, poi `assemble.py` con `NAMES=['07_hut.json', '08_props.json']`. Per rigenerarlo: `make_patch.py`, `tone_trace.py`, `gen.py` in `TMP/work/s39/`, poi `assemble.py` con `NAMES=['07_hut.json']`. Metodo: ricalco dei toni con `LIB/tone_trace.py`; le parti nascoste si dipingono in una patch PNG nei toni campionati (vedi storico). Approvati: 3.1–3.4c, 3.4b. Il fogliame si scrive in specifiche `PRJ/Tools/gimp/recipes/foliage/*.json`: dopo averne cambiata una eseguire `python -I LIB/foliage.py <specifica>`, poi `TMP/assemble.py` con `NAMES=['10_plants.json']`. Dopo un nuovo tracciato eseguire il generatore dei livelli del pezzo (`TMP/work/s35|s36|s37/gen.py`) e montare la ricetta; i livelli tolti dalla ricetta si eliminano dall'XCF con `TMP/work/s36/drop_layers.py` (parametri `DROP` e `PREVIEW`). Per ogni pezzo consegnare cover composta e confronto originale / vecchio / nuovo, dopo aver chiuso immagini, script e collegamenti del passo; nominare ogni punto con la sua descrizione.

### 10.2 Agenti interrotti e lavori in corso

1. **Primo agente del ritaglio dei personaggi (corsie A e B): fallito.** Si è fermato tre volte per timeout dell'API, probabilmente per le troppe immagini guardate.
   - **Compito:**
     - modulo generico `LIB/figure_cutout.py`;
     - ricette `PRJ/Tools/gimp/recipes/cover_couple.json` e `cover_rival.json`;
     - maschere grezze `TMP/chars/couple_rough_mask.png` e `rival_rough_mask.png`, più `ROUGH_READY.txt`;
     - PNG ritagliati della coppia (ragazza rossa + ragazzo) e della rivale, con gli accessori separati (`ball_crumbs`, `exclaim`, `sweat`; `hearts`) e i JSON con gli scostamenti;
     - contorni delle ombre (`couple_shadow.json`, `rival_shadow.json`);
     - infine `DONE.txt`.
   - **Fatto:**
     - `LIB/figure_cutout.py` completo, con docstring e autotest (`--selftest` superato);
     - bozza della ricetta della coppia `TMP/work/rc_try.json` (contorno largo `envelope` e linee di chiusura `seal_lines` fra i piedi);
     - risultati di prova in `TMP/work/out_try/` (`couple.png`, `couple_rough_mask.png`, `couple_mask_debug.png`, `couple.json`) e script di visualizzazione in `TMP/work/`.
     - Ultima nota: "falla vicino a (542, 811), allungare la linea di chiusura".
   - **Non fatto:** ricette nel progetto, rivale, accessori, ombre; nulla in `TMP/chars/`.
2. **Secondo agente del ritaglio dei personaggi: interrotto** per il limite di utilizzo di Claude. Il ritaglio è stato completato da Codex. I punti qui sotto descrivono il materiale lasciato al momento dell'interruzione.
   - **Compito:** lo stesso del primo agente (punto 1), ripartendo dai suoi file.
   - **Fatto:**
     - maschere grezze in `TMP/chars/`: `couple_rough_mask.png` (dalla pipeline), `rival_rough_mask.png` (solo un poligono grossolano, da rifare con la pipeline); `ROUGH_READY.txt` scritto;
     - ricette nel progetto: `PRJ/Tools/gimp/recipes/cover_couple.json` e `cover_rival.json`;
     - correzione in `figure_cutout.py`: `_save` ora porta l'alpha da 0–1 a 0–255 (prima i PNG uscivano quasi trasparenti); l'autotest passa ancora;
     - prove della coppia in `TMP/work/out2/` (`couple.png`, `couple_ball_crumbs.png`, `couple_exclaim.png`, `couple.json`, `couple_mask_debug.png`), prodotte **prima** della correzione di `_save`: vanno rigenerate;
     - prove della rivale in `TMP/work/out3/` (`rival.png`, `rival_hearts.png`, `rival.json`, `rival_mask_debug.png`), ultime prodotte, controllo non finito;
     - ritagli di controllo `TMP/work/v1.png` … `v14.png`.
   - **Non fatto:**
     - rigenerare la coppia con `_save` corretto e verificarla (bordi, buchi interni, falla vicino a (542, 811));
     - verificare la rivale;
     - decidere se la goccia di sudore (`sweat`) si stacca dalla faccia;
     - ombre (`couple_shadow.json`, `rival_shadow.json`);
     - copiare le uscite definitive in `TMP/chars/` e scrivere `DONE.txt`.
   - **Esito della ripresa:** `TMP/chars/DONE.txt` presente, vedi storico.
3. **Agente della corsia H (palma): fallito durante una ripresa.**
   - **Compito:** aggiungere a `06_palm.json` il secondo tronco e le fronde a sinistra del tetto.
   - **Fatto:** niente, prima dell'interruzione. Il lavoro l'ha completato il thread principale con `TMP/lanes/H/gen2.py` (seconda palma, livelli `palm2_*`): **nulla da riprendere.**
4. Gli altri agenti (tavolozze P, corsie C+D, E, F, G, I, J+K+L) hanno finito; alcuni dopo una o più riprese per lo stesso errore dell'API.

### 10.3 Prossimi passi, in ordine

1. **Rigenerare il ritaglio** solo se serve ricostruire `TMP/chars/`.
   - Comando: `uv run --with numpy --with scipy --with scikit-image --with pillow python -I LIB/figure_cutout.py <ricetta> PRJ/Assets/Images/beatch-slash-cover-no-logo.png TMP/chars`.
   - Ricette definitive della fase di ritaglio: `PRJ/Tools/gimp/recipes/cover_couple.json` e `cover_rival.json`. L'alpha va da 0 a 255. Per la scia rosa occorre la versione del modulo che legge `repairs`.
   - Uscite attese in `TMP/chars/`:
     - figure e accessori: `couple.png`, `couple_ball_crumbs.png`, `couple_exclaim.png` (`couple_sweat.png` se staccabile), `rival.png`, `rival_hearts.png`;
     - scostamenti: `couple.json`, `rival.json` (`offset_cover`, `offset_canvas`);
     - ombre: `couple_shadow.json`, `rival_shadow.json` (anelli in coordinate della tela, `shadow_rgb`, `sand_rgb`).
   - Le ombre non si ritagliano: se ne misura solo il contorno.
   - Controllo: nessun alone azzurro o color sabbia lungo i bordi; buchi interni trasparenti (tra braccio e corpo, tra le gambe, tra le ciocche); punte dei capelli intere; piedi senza sabbia.
   - Guardare poche immagini piccole alla volta, per non far scadere le richieste.
2. **2.2 Progetti dei personaggi, completati.** `PRJ/Tools/gimp/beatch_slash_cover_couple.xcf` e `beatch_slash_cover_rival.xcf`, sulla tela 2172×1222.
   - Livello `reference` nascosto: la no-logo in (250, 140).
   - Ogni PNG ritagliato come livello, al suo `offset_canvas`: `couple`, `ball_crumbs`, `exclaim`; `rival`, `hearts`. Su `couple` restano le gocce di sudore e la palla in mano.
   - Livello `shadow` ridisegnato dagli anelli del JSON. Si passa a `vector_art.run` un trace `{'parts': {'shadow': {'silhouette': rings}}}` e la forma `{"part": "shadow", "feather": 2}`. Riempimento con `shadow_rgb` su un livello Moltiplica, opacità da tarare finché l'ombra sulla sabbia nuova ha il tono dell'originale.
   - Valori in ricette del progetto (es. `cover_couple_shadow.json`, `cover_rival_shadow.json`).
3. **2.3 Esportazioni, completate.**
   - `Assets/Images/beatch-slash-cover-background.png`: l'ambiente, con `layer_ops.export_visible(img, path)` sull'`.xcf` dell'ambiente.
   - `beatch-slash-cover-couple.png`, `beatch-slash-cover-rival.png`: figura più accessori uniti.
   - `beatch-slash-cover-couple-shadow.png`, `beatch-slash-cover-rival-shadow.png`: le ombre, ritagliate strette.
4. **2.4 Anteprima della cover composta, completata.** Sfondo, ombre in Moltiplica e figure agli `offset_canvas`, rifilati alla cornice originale. Uscita `TMP/preview_cover_nologo.png`, da rigenerare dopo 2b.
5. **Fase 2b, completata.** Confronto con la no-logo (posizioni, forme, presenza degli elementi) e con la cover con logo (colori, tratto). Elenco iniziale dei problemi verificati, con correzioni nello storico:
   - **chiosco:** tetto troppo alto (apice a y 40 della tela) che copre le fronde della seconda palma; tetto sovrapposto al bordo della tenda; riquadro visibile sulla testa del palo principale (tela 296–322, 268–290); puntoni approssimati; margine sinistro 0–108 senza chiosco;
   - **palme:** corone più fitte e a ventaglio dell'originale; una fronda gialla incrocia il tronco; foglioline troppo regolari; posizione e pendenza del tronco principale stimate a occhio (nella no-logo il tronco va da circa (440, 25) a (350, 200) della cover);
   - **cielo e isole:** nuvole geometriche (cumuli di cerchi); scogliera con poche faccette; isolotto piccolo e poco leggibile;
   - **mare:** battigia stimata, non tracciata; schiuma lontana poco fitta; orizzonte a y 548 da confrontare con le isole;
   - **sabbia:** bordo superiore stimato, da far combaciare con la battigia;
   - **scogli:** posizioni approssimate, faccette regolari, pochi sassi sulla sabbia;
   - **oggetti e piante:** il barile non è coperto da foglie e ibisco come nella no-logo; foglie geometriche con una sola nervatura, quelle del margine sinistro lunghe e fitte; cespuglio a destra di sole 4 foglie; prima conchiglia troppo larga.
   - Per ogni errore: correzione nella ricetta (o nel suo `gen.py`), poi `assemble.py` sulle sole ricette toccate. Infine nuova anteprima (passo 4), elenco degli errori corretti nello storico.
6. **Fase 3:** eseguire solo il prossimo pezzo della sezione 8. Salvare confronto e anteprime in `TMP`, aprire la composizione aggiornata e registrare lo stato **in attesa di verifica**. Riprendere dal riscontro dell'utente.
7. **Dopo l'approvazione:**
   - sovrascrittura di `Assets/Images/beatch-slash-cover-no-logo.png`;
   - documentazione, con le regole di `AGENTS.md`:
     - `CODE_MAP.md`: file, livelli, scostamenti;
     - `PROJECT_CONTEXT.md`: il punto passa ad approvato;
     - `GIMP.md` e la guida generica `gimp.md`: le lezioni della sezione 10.4;
   - poi la fase 4 (cover con logo).
8. **Pulizia finale** (solo su indicazione dell'utente): eliminare questo file e la cartella `TMP`.

### 10.4 Note operative per chi riprende

- **GIMP via MCP `gimp`:** `check_server` prima di tutto. Codice Python nella console: strumento `call_api` con `api_path: "exec"` e `args: ["pyGObject-console", [codice]]`. Script lunghi in un file `.py`, eseguiti con `exec(open(path, encoding='utf-8').read(), {})`.
- **Libreria:** dopo aver modificato un modulo di `LIB`, `importlib.reload(modulo)` nella console. Solo se nessun altro sta usando GIMP in quel momento.
- **`vector_art.run(..., xcf=...)` non salva:** chi chiama deve usare `Gimp.file_save` (lo fa già `assemble.py`).
- **Immagini aperte in GIMP:**
  - le immagini create da script non si chiudono via script: restano aperte le prove `va_test.xcf`, `va_test2.xcf` e gli `.xcf` di lavoro delle corsie (`TMP/lanes/*/*.xcf`);
  - per trovare un'immagine usare il percorso del file (`layer_ops.find_image(path)`), non l'indice;
  - se GIMP viene riavviato, `vector_art.target` riapre l'`.xcf` dal percorso della ricetta.
- **Agenti in parallelo:** una sola istanza di GIMP e una sola console condivisa. In parallelo solo il lavoro fuori da GIMP, oppure render in un'unica chiamata `exec` con namespace proprio, senza `reload`.
- **Shell:** nei file scritti con heredoc senza virgolette le barre rovesce vengono interpretate; testi lunghi con apostrofi meglio scriverli con l'editor di file. Un hook a volte rifiuta il primo tentativo di `Bash`: riprovare una volta.
- **Lezioni da riportare nelle guide alla fine:**
  - `replace_layers` per montare un disegno elemento per elemento;
  - la parte di raccolta `_other` in `trace_reference`;
  - le regole sul GIMP condiviso;
  - il limite di `xcf=`;
  - l'indice finale di `reorder_item` (già nella guida di progetto). Riprese le corsie personaggi e F con l'indicazione di lavorare a passi piccoli.
