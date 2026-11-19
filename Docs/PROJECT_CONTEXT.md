# Beatch Slash! — contesto del gioco

## Indice

1. [Regole di questo file](#1-regole-di-questo-file): cosa ci va e cosa no.
2. [Concept del gioco](#2-concept-del-gioco): visione dell'utente, tono, personaggi, idea di fondo.
3. [Come funziona il gioco](#3-come-funziona-il-gioco): comandi, ondate, combattimento, ragazzo, economia, bonus di fine ondata, progressione.
4. [Negozio](#4-negozio): Chiosco da Sandro, categorie, oggetti, prezzi, regole degli acquisti.
5. [Mondo di gioco](#5-mondo-di-gioco): livello tutorial, inquadratura, terreno, elementi di scena.
6. [Personaggi](#6-personaggi): aspetto di protagonista, nemica base, ragazzo, negoziante e chiosco.
7. [Interfaccia](#7-interfaccia): HUD, popup, numeri fluttuanti, menu, tipografia, immagini.
8. [Pipeline grafica e stile visivo](#8-pipeline-grafica-e-stile-visivo): strumenti, metodo di lavoro, regole di stile vincolanti.
9. [Vincoli dell'utente](#9-vincoli-dellutente): regole di lavoro da rispettare sempre.
10. [Stato attuale](#10-stato-attuale): stato di ogni punto di sviluppo.
    - [10.1 Punti approvati](#101-punti-approvati): funzionamenti e comportamenti approvati, riferimento per gli sviluppi futuri.
    - [10.2 Punti in lavorazione](#102-punti-in-lavorazione): sviluppi in corso, in test o in attesa di approvazione.
    - [10.3 Punti aperti](#103-punti-aperti): sviluppi decisi e definiti, non ancora avviati.
11. [Idee future](#11-idee-future): idee e concept su cui ragionare prima di formalizzarli.

## 1. Regole di questo file

Regola categorica dell'utente. Questo file descrive **il gioco com'è adesso**: concept completo, funzionamento, stato dei punti di sviluppo, idee future.

- **Non è uno storico.** Niente date, cronologia, "prima era così", correzioni fatte, tentativi respinti, resoconti di verifica o titoli come "Terreno (17/11)". Ciò che spiega come funziona il gioco va nella sezione apposita; ciò che è solo storia non si scrive.
- **Niente dettagli tecnici.** Nodi, scene, script, file, percorsi, costanti, segnali, collisioni e layout degli atlanti stanno **solo** in `Docs/CODE_MAP.md`. Le procedure degli strumenti stanno nelle guide (`Docs/BLENDER.md`, `Docs/PIXELORAMA.md`, `Docs/GIMP.md`, `Docs/GODOT.md`).
- A ogni intervento riscrivere le voci toccate nella sezione giusta (vedi indice).
- **Ciclo di vita dei punti di sviluppo.** Un punto sta sempre in una sola categoria; appena non rientra più nella sua definizione passa alla categoria successiva o sparisce:
  1. **Idee future** (sezione 11): idee o concept su cui ragionare. Quando l'utente la approva e se ne definisce cosa deve fare, l'idea si sposta in Punti aperti e si cancella da qui.
  2. **Punti aperti** (10.3): sviluppi decisi e definiti, non ancora avviati, che prima o poi si faranno. Quando l'utente decide di realizzarlo, il punto si sposta in Punti in lavorazione.
  3. **Punti in lavorazione** (10.2): sviluppi in corso, in test o in attesa di valutazione e approvazione dell'utente.
  4. **Punti approvati** (10.1): quando il punto è sviluppato, verificato, testato, corretto e funziona come vuole l'utente, si toglie da In lavorazione e si scrive qui come funzionamento approvato, soprattutto se è un riferimento utile per punti aperti o idee future collegati.
- Ciò che un punto approvato cambia nel gioco si descrive anche nella sua sezione (3–7). Ogni dettaglio tecnico utile da conservare va in `Docs/CODE_MAP.md`.

## 2. Concept del gioco
# Beatch Slash! — contesto del gioco

## Indice

1. [Regole di questo file](#1-regole-di-questo-file): cosa ci va e cosa no.
2. [Concept del gioco](#2-concept-del-gioco): visione dell'utente, tono, personaggi, idea di fondo.
3. [Come funziona il gioco](#3-come-funziona-il-gioco): comandi, ondate, combattimento, ragazzo, economia, bonus di fine ondata, progressione.
4. [Negozio](#4-negozio): Chiosco da Sandro, categorie, oggetti, prezzi, regole degli acquisti.
5. [Mondo di gioco](#5-mondo-di-gioco): livello tutorial, inquadratura, terreno, elementi di scena.
6. [Personaggi](#6-personaggi): aspetto di protagonista, nemica base, ragazzo, negoziante e chiosco.
7. [Interfaccia](#7-interfaccia): HUD, popup, numeri fluttuanti, menu, tipografia, immagini.
8. [Pipeline grafica e stile visivo](#8-pipeline-grafica-e-stile-visivo): strumenti, metodo di lavoro, regole di stile vincolanti.
9. [Vincoli dell'utente](#9-vincoli-dellutente): regole di lavoro da rispettare sempre.
10. [Stato attuale](#10-stato-attuale): stato di ogni punto di sviluppo.
    - [10.1 Punti approvati](#101-punti-approvati): funzionamenti e comportamenti approvati, riferimento per gli sviluppi futuri.
    - [10.2 Punti in lavorazione](#102-punti-in-lavorazione): sviluppi in corso, in test o in attesa di approvazione.
    - [10.3 Punti aperti](#103-punti-aperti): sviluppi decisi e definiti, non ancora avviati.
11. [Idee future](#11-idee-future): idee e concept su cui ragionare prima di formalizzarli.

## 1. Regole di questo file

Regola categorica dell'utente. Questo file descrive **il gioco com'è adesso**: concept completo, funzionamento, stato dei punti di sviluppo, idee future.

- **Non è uno storico.** Niente date, cronologia, "prima era così", correzioni fatte, tentativi respinti, resoconti di verifica o titoli come "Terreno (17/11)". Ciò che spiega come funziona il gioco va nella sezione apposita; ciò che è solo storia non si scrive.
- **Niente dettagli tecnici.** Nodi, scene, script, file, percorsi, costanti, segnali, collisioni e layout degli atlanti stanno **solo** in `Docs/CODE_MAP.md`. Le procedure degli strumenti stanno nelle guide (`Docs/BLENDER.md`, `Docs/PIXELORAMA.md`, `Docs/GIMP.md`, `Docs/GODOT.md`).
- A ogni intervento riscrivere le voci toccate nella sezione giusta (vedi indice).
- **Ciclo di vita dei punti di sviluppo.** Un punto sta sempre in una sola categoria; appena non rientra più nella sua definizione passa alla categoria successiva o sparisce:
  1. **Idee future** (sezione 11): idee o concept su cui ragionare. Quando l'utente la approva e se ne definisce cosa deve fare, l'idea si sposta in Punti aperti e si cancella da qui.
  2. **Punti aperti** (10.3): sviluppi decisi e definiti, non ancora avviati, che prima o poi si faranno. Quando l'utente decide di realizzarlo, il punto si sposta in Punti in lavorazione.
  3. **Punti in lavorazione** (10.2): sviluppi in corso, in test o in attesa di valutazione e approvazione dell'utente.
  4. **Punti approvati** (10.1): quando il punto è sviluppato, verificato, testato, corretto e funziona come vuole l'utente, si toglie da In lavorazione e si scrive qui come funzionamento approvato, soprattutto se è un riferimento utile per punti aperti o idee future collegati.
- Ciò che un punto approvato cambia nel gioco si descrive anche nella sua sezione (3–7). Ogni dettaglio tecnico utile da conservare va in `Docs/CODE_MAP.md`.

## 2. Concept del gioco

Tono ironico e leggero. Tower defense a ondate, 2D top-down in pixel art, ambientato per ora in un solo livello: una spiaggia.

- **Protagonista (Player):** una ragazza che difende il fidanzato lanciando palle di sabbia contro le altre ragazze finché non le sconfigge.
- **Il fidanzato (il ragazzo, la "torre"):** un ragazzo bellissimo; per questo le altre ragazze della spiaggia se ne invaghiscono e vogliono portarselo via. Non si muove: è l'oggetto da difendere.
- **Due valori di difesa del ragazzo:**
  - **Moralità** (lo scudo): la sua caratura morale e il rispetto per la fidanzata. Le nemiche intaccano prima questa.
  - **Fedeltà** (la salute): entra in gioco quando la moralità è a zero e cala man mano che le nemiche attaccano.
  - Quando moralità e fedeltà sono a zero il ragazzo non è più fedele e scappa con le altre ragazze: è il game over.
- **Come attaccano le nemiche:** non fanno danno fisico. Fanno pose, avances e movimenti sensuali verso il ragazzo; quando la moralità è a zero arrivano anche a toccarlo.
- **Stile delle avances:** le nemiche restano sempre vestite (costumi da spiaggia), niente nudità. Pose ammiccanti e ironiche, fumettistiche e volutamente esagerate (sguardi, baci, capelli, appoggiarsi, braccio al collo). A moralità zero il contatto è sensuale ma ironico: breve e comico, con cuoricini ed espressioni esagerate. Deve essere sempre evidente che le ragazze ci provano attivamente.
- **Reazioni del ragazzo:** con la moralità attiva guarda le ragazze con curiosità, senza malizia; a moralità zero le guarda con più interesse; infine cede e scappa.
- **Nemiche:** ragazze in spiaggia più belle della protagonista, con la chioma voluminosa e colori variabili di capelli, occhi, costume e pelle. Sono previste diverse "classi": da quelle molto resistenti, con molto danno ma lente (movimento e frequenza di attacco), a quelle fragili e veloci con danno costante, con un ampio range intermedio. Ogni classe può avere un aspetto distinto. Oggi esiste solo la nemica base.
- **Valuta:** le monete sono quelle perse dalle ragazze sconfitte.

## 3. Come funziona il gioco

### Comandi

- Movimento con le frecce (o tasti configurati e gamepad); Spazio tenuto premuto fa correre (velocità doppia).
- Tasto destro del mouse: lancio della palla di sabbia verso il puntatore.
- F: apre il negozio, solo davanti al bancone e durante la pausa tra due ondate.
- Esc: chiude il negozio oppure apre e chiude la pausa.

### Player

- Velocità di movimento a tre livelli; si sale comprando l'Infradito Conchiglia. La corsa raddoppia la velocità del livello attuale.
- La protagonista non può uscire dallo schermo di gioco.
- **Lancio:** la palla parte quando il braccio la lancia; si può lanciare anche camminando e correndo.
- **Velocità di lancio a tre livelli**, si sale solo comprando il Corso di Schiacciata (decisione dell'utente): lenta (come la camminata), media, veloce.
- Non si può lanciare di nuovo finché il gesto precedente non è quasi finito.
- Danno iniziale della palla: 10.
- La palla colpisce una nemica in qualunque punto del corpo e scoppia; scoppia anche contro il chiosco e gli ostacoli. Se non colpisce nulla, ricade sulla sabbia e si disfa.

### Nemiche e ondate

- Le nemiche nascono fuori dall'inquadratura, da tutti i lati tranne il mare, e camminano verso il ragazzo aggirando ostacoli e altre nemiche.
- Ognuna punta a un proprio posto attorno al ragazzo, così non si ammassano; non si urtano tra loro.
- Arrivata al suo posto, la nemica "flirta" e attacca a intervalli regolari.
- Colpita, lampeggia e arretra appena. Sconfitta, cade a sedere e sparisce in uno sbuffo di sabbia.
- Ogni sconfitta dà 10 punti e 18 monete (più l'eventuale bonus sulle monete).
- **Ondata 1:** 3 nemiche con 50 di salute (5 colpi da 10) e 5 di danno per attacco.
- **Progressione senza tetto:** a ogni ondata crescono gradualmente il numero di nemiche, la loro salute e, più piano, il loro danno.
- Le monete per nemica **non crescono** con le ondate: l'unica crescita è il bonus acquistabile.
- Quando cade l'ultima nemica parte una pausa di circa 20 secondi con il conto alla rovescia della prossima ondata; in questa pausa si può usare il negozio.

### Il ragazzo

- Moralità e fedeltà partono da 100. Ogni attacco toglie prima moralità; solo quando è a zero toglie fedeltà. L'eccedenza di un colpo sulla moralità non passa alla fedeltà.
- Fedeltà a zero: game over.
- **Comportamento** (regole dell'utente):
  - nessuna nemica che attacca: fermo al sole, mani sui fianchi, occhi chiusi;
  - moralità sopra zero (qualunque fedeltà): stessa posa, con ogni tanto un'occhiata curiosa verso una nemica;
  - moralità a zero e fedeltà sopra metà: si sporge ad ammirare la nemica più vicina, mano al mento;
  - moralità a zero e fedeltà a metà o meno: si mette in mostra con il doppio bicipite.

### Bonus di fine ondata

Quando cade l'ultima nemica, il gioco premia la difesa con una quota delle monete guadagnate nell'ondata dalle sconfitte (gli acquisti non contano; il bonus del negozio sulle monete è già incluso):

- la fedeltà deve essere al massimo, altrimenti nessun bonus;
- moralità al massimo: +100%;
- moralità sotto il massimo e oltre il 50%: +50%;
- moralità tra 0 (escluso) e il 50% (compreso): +25% (il caso "esattamente 50%" non è stato specificato dall'utente ed è trattato così);
- moralità a 0: nessun bonus.

Il bonus, se maggiore di zero, è annunciato da un popup animato al centro dello schermo con la percentuale e le monete guadagnate; non blocca il gioco.

### Game over e menu

- Al game over il gioco si ferma e compare il pannello con Ricomincia, Torna al Menù, Esci.
- Menu principale con Nuova partita, Opzioni (volume e muto), Tutorial. Pausa con Esc: Riprendi, Ricomincia, Torna al Menù.
- La musica (unico brano, in loop) suona nel menu; in partita non c'è musica.

## 4. Negozio

- Nome ufficiale: **"Chiosco da Sandro"**; il negoziante si chiama Sandro. È un chiosco sulla spiaggia, in alto a sinistra del ragazzo.
- Si apre con F stando davanti al bancone, solo durante la pausa tra le ondate. Mentre il pannello è aperto il Player non si muove e non lancia. Uscire dall'area, premere Esc o la fine della pausa lo chiudono.
- **Pannello:** mostra le monete disponibili e divide gli oggetti in tre gruppi: Giocatore, Partner, Bonus. Ogni oggetto ha icona, nome, descrizione e prezzo, in schede piccole per poterne aggiungere molti (richiesta dell'utente). Partner è diviso in Moralità e Fedeltà; Giocatore e Bonus, per scelta dell'utente, non sono suddivisi finché non ci saranno abbastanza oggetti.
- **Regole d'acquisto:** prezzo fisso; non si può comprare se le monete non bastano, se l'oggetto ha raggiunto il massimo di acquisti o se è inutile (un ripristino con la barra già piena).
- **Categorie** (definizione dell'utente, vincolante per ogni nuovo oggetto):
  - **Giocatore:** potenziamenti della protagonista (danno, rapidità di lancio, movimento e simili).
  - **Partner:** tutto ciò che riguarda il ragazzo: ripristino di moralità e fedeltà, aumento dei loro massimi e altro.
  - **Bonus:** extra che non riguardano né il ragazzo né la ragazza, come il bonus sulle monete; alcuni possono essere temporanei.
- **Oggetti temporanei:** comprati nella pausa, valgono dall'ondata successiva per il numero di ondate indicato. Finché sono attivi non si possono ricomprare, quindi non si sommano.
- **Oggetti attuali** (prezzi provvisori, da tarare con i playtest):

| Oggetto | Categoria | Effetto | Prezzo | Massimo |
| --- | --- | --- | --- | --- |
| Acqua Tonica | Partner / Moralità | ripristina il 25% della moralità | 20¢ | illimitato |
| Granita al Limone | Partner / Moralità | ripristina il 50% | 35¢ | illimitato |
| Frullato ai Frutti di Bosco | Partner / Moralità | ripristina il 100% | 60¢ | illimitato |
| Crema Protezione 50+ | Partner / Moralità | massimo +25% del valore iniziale (riempie la parte aggiunta) | 100¢ | 4 |
| Ombrellone | Partner / Moralità | dimezza la perdita di moralità per 3 ondate | 50¢ | temporaneo |
| Caramelle alla Menta | Partner / Fedeltà | ripristina il 25% della fedeltà | 20¢ | illimitato |
| Patatine al Rosmarino | Partner / Fedeltà | ripristina il 50% | 35¢ | illimitato |
| Milkshake alla Fragola | Partner / Fedeltà | ripristina il 100% | 60¢ | illimitato |
| Braccialetto Portafortuna | Partner / Fedeltà | massimo +25% del valore iniziale | 100¢ | 4 |
| Settimana Enigmistica | Partner / Fedeltà | dimezza la perdita di fedeltà per 3 ondate | 50¢ | temporaneo |
| Barretta Energetica | Giocatore | danno +20% del danno iniziale; in vendita solo ogni 5 ondate | 70¢ | illimitato |
| Corso di Schiacciata | Giocatore | un livello di velocità di lancio in più | 50¢ | 2 |
| Infradito Conchiglia | Giocatore | un livello di velocità di movimento in più | 50¢ | 2 |
| Salvadanaio a Forma di Granchio | Bonus | monete +10% | 80¢ | 5 |
| Gelato Fondente | Bonus | monete raddoppiate nella prossima ondata | 30¢ | temporaneo (1 ondata) |

- **Icone degli oggetti:** illustrate, nello stile di concept e copertine (contorno caldo scuro, colori vivi, cel shading). Il frullato è il riferimento di stile approvato.- **Nuovi oggetti:** se l'utente non li indica, nomi e descrizioni li sceglie l'agente rispettando spiaggia, tono ironico e contesto. Devono essere cose plausibili in un baretto o bancarella di spiaggia o legate agli sport estivi. Gli oggetti acquistabili più volte non devono essere cose che nella realtà si comprano una volta sola (per esempio un anello di fidanzamento).

## 5. Mondo di gioco

- **Livello tutorial:** l'unico livello attuale, con level design semplice per imparare i comandi, ispirato alle copertine. La mappa è più grande dell'inquadratura e le nemiche arrivano da tutti i lati tranne il mare.
- **Inquadratura fissa** (decisione dell'utente): la camera non segue il Player e mostra l'intera spiaggia giocabile. Il ragazzo sta al centro dello schermo, il Player parte davanti a lui.
- **Terreno:** solo sabbia, battigia (con la sabbia bagnata) e mare con le sue profondità. Scogli ed erba non sono terreno (scartati dall'utente: "vanno bene per un platform 2D", e i personaggi ci passerebbero sopra); rocce, alberi, fiori e simili sono elementi di scena. La sabbia ha particolari sparsi a caso (increspature, piccole dune, luccichii, sassolini, conchiglie, puntini), mai uguali accanto. Il mare forma una baia in alto a destra.
- **Elementi di scena:** disposizione ispirata a una spiaggia libera italiana, con pochi elementi e un criterio (richiesta dell'utente):
  - macchia di palme con cespugli e fiori ai piedi sul lato opposto al mare (in alto a sinistra, dietro il chiosco, a sinistra, in basso a sinistra, in basso);
  - punta della baia con gruppo di scogli; ciottoli e conchiglie sulla linea delle mareggiate; un tronco spiaggiato lungo la riva;
  - due soli gruppi di ombrelloni: a destra due aperti con due teli e una tavola; in basso a sinistra uno aperto e uno chiuso con telo e tavola;
  - il centro libero.
- **Solidi e decorazioni:** palme, rocce medie e grandi, cespugli, ombrelloni, tavole piantate, tronchi, botti e cartello bloccano personaggi e palle di sabbia. Ciottoli, conchiglie, fiori, palme giovani, teli e tavole sdraiate sono decorazioni a terra, calpestabili.
- **Granchio:** si muove (un animaletto non deve essere fermo: richiesta dell'utente). Non è calpestabile.
- Regola di disposizione: gli ostacoli non stanno troppo vicini tra loro né al chiosco, così le nemiche non si incastrano.

## 6. Personaggi

### Protagonista

- Ragazza della spiaggia del concept: chioma rossa voluminosa, costume turchese.

### Nemica base

- Donna adulta atletica e formosa, proporzioni chibi, vita definita, seno e glutei un po' più pieni della protagonista senza eccessi. Capelli viola lunghi e lisci fino alla vita bassa; bikini smeraldo a triangolo con lacci e fiocchi ai fianchi, slip sgambato.

### Ragazzo

- Adulto leggermente più alto delle ragazze, atletico e robusto senza eccessi muscolari; viso bello, occhi verdi, pelle moderatamente abbronzata.
- Capelli corti castano scuro, lati corti e parte superiore pettinata di lato (ispirazione: George Clooney). Barba corta castana su mento e mandibola con pelle libera sotto il labbro e piccolo pizzetto triangolare (ispirazione: Can Yaman).
- Collanina sottile da spiaggia con perline scure e accenti rosso, giallo, verde d'ispirazione giamaicana. Bermuda fino a metà ginocchio, terracotta caldo con cordino chiaro (toni Autunno dell'armocromia).

### Negoziante (Sandro)

- Gestore maturo e ordinario: viso allungato con naso pronunciato, tratti morbidi e piccoli segni d'età, senza baffi; pelle abbronzata, capelli mossi brizzolati schiariti dal sole, cappello di paglia con fascia petrolio, camicia hawaiana corallo a grandi motivi crema aperta su una canotta chiara.
- Sta dietro il bancone e ogni tanto pulisce bicchieri e bancone.
- Vincoli dell'utente: identità da chiosco sulla spiaggia, cappello mantenuto, viso non da bel ragazzo, dimensioni credibili rispetto all'edificio; evitare il viso tondo con baffi simile a Super Mario.

### Chiosco

- Legno caldo, tetto di paglia dorata, tenda rossa e crema a bordo smerlato, lanterna ambrata, mensola con bottiglie, bancone con bibite, tavola da surf crema e rossa con ibisco e botte con corda sul lato sinistro. Niente sgabelli: si arriva direttamente al bancone (richiesta dell'utente).

## 7. Interfaccia

- **Priorità dell'utente:** interfaccia e menu sono provvisori sul piano grafico. Ora devono funzionare, essere leggibili e posizionati bene; il restyling estetico verrà dopo.
- **HUD a bande:** due bande in legno scuro a tutta larghezza, in alto e in basso, così HUD e gioco non si sovrappongono. In alto: ondata (sinistra), punti (centro), monete (destra). In basso: barre di moralità e fedeltà a sinistra, nemiche rimaste e sconfitte a destra. Le voci mostrano solo un'icona e il numero.
- **Barre:** tubi di vetro con liquido che si svuotano piano piano: moralità blu, fedeltà rossa. Sulle barre del ragazzo c'è "valore / massimo".
- **Icone dell'HUD:** illustrate come quelle degli oggetti. Fedeltà: cuore rosso corallo. Moralità: scudo turchese con bordo oro e cuore rosso. Ondata, stella marina (punti), moneta, nemica in piedi (rimaste), nemica a terra (sconfitte).
- **Numeri fluttuanti:** sopra la testa di una nemica colpita sale e svanisce il danno subito. Sopra il ragazzo compaiono perdite e recuperi, del colore della barra interessata; anche per ripristini e aumenti dei massimi.
- **Conto alla rovescia:** "Prossima ondata tra: N" sotto la banda alta, nello stile del popup del bonus.
- **Tipografia:** Luckiest Guy per titoli e annunci; Fredoka per interfaccia e testo. Ruoli, pesi e misure in `Docs/FONTS.md`.
- **Immagini conservate:** logo solo testo, logo completo, copertina con i personaggi, copertina con personaggi e logo. Nessun uso assegnato; non eliminarle come inutilizzate.

## 8. Pipeline grafica e stile visivo

Leggere prima di toccare qualsiasi sprite. Tutte le nuove risorse grafiche (nemiche, ragazzo, oggetti, effetti) seguono questo stile e questi strumenti. Percorsi di concept, sorgenti e risorse: `Docs/CODE_MAP.md`, sezione Risorse grafiche.

### Strumenti

- **Blender** (MCP `blender`): personaggi animati, modello 3D chibi con rig, renderizzato a pixel. Guida `Docs/BLENDER.md`.
- **Pixelorama** (MCP `pixelorama`): oggetti piccoli, effetti, tile, ritocchi dentro la silhouette. Guida `Docs/PIXELORAMA.md`.
- **GIMP** (MCP `gimp`): immagini raster che non sono sprite di personaggio. Crea, compone e ritocca direttamente loghi, copertine, icone e illustrazioni dell'interfaccia, sfondi, testo, correzioni di colore e tono, ritagli, ridimensionamenti ed esportazioni in blocco, senza dover passare da Codex. Non genera concept art con l'IA e non sostituisce Pixelorama nel pixel per pixel. Indicazione dell'utente: Claude userà GIMP direttamente per ogni immagine del gioco (loghi, sfondi, concept e altro), con Codex/ImageGen solo come riferimento; ancora da collaudare su un'immagine di gioco reale. Guida `Docs/GIMP.md`.
- **Godot AI** (MCP `godot-ai`): scene, nodi, script, avvio, log, screenshot per verificare in gioco. Guida `Docs/GODOT.md`.
- **ImageGen:** concept art e icone illustrate, usando i concept esistenti come riferimento. GIMP per rifinirle e comporle; Pixelorama solo se servono ritocchi o pixel art.
- La skill condivisa `game-tools` instrada alle guide generiche; le regole di aggiornamento delle guide sono in `AGENTS.md`.
- Per ogni nuovo elemento con sprite: concept, prompt e sorgenti conservati nel progetto (dove: CODE_MAP).

### Metodo per un nuovo personaggio (indicazione dell'utente)

1. **Il turnaround è il riferimento principale del modello 3D:** le viste (fronte, profilo, retro) si allineano al modello e il personaggio si ricostruisce sopra, con zone di colore prese dal concept. Non si deforma a occhio un modello esistente.
2. **Coerenza con gli altri personaggi:** stesso rig, materiali toon, camera, contorno, occhi a pixel e ombra; la scala viene dal confronto dei concept (altezze relative come nei turnaround).
3. **Dopo ogni revisione del modello** mostrare all'utente il render del modello e lo sprite generato (posa base nelle 4 direzioni, ingrandimento nearest), aprendoli in VS Code. Mostrare le anteprime man mano, senza aspettare il risultato finale.
4. **Pixelorama solo per ritoccare lo sprite** dentro la silhouette (ciocche, viso, dettagli del costume, linee muscolari).
5. **Le correzioni di forma e proporzione tornano nel modello:** lo sprite ritoccato è il riferimento per correggere il modello, così ogni fotogramma esce giusto e coerente tra le direzioni. Non ridisegnare a mano la silhouette vista per vista.

### Regole di stile (vincolanti)

- Pixel art per tutto il mondo di gioco; icone e illustrazioni dell'interfaccia sono invece nello stile illustrato delle copertine.
- Player in celle 48×48; ragazzo e nemica in celle 64×64 alla stessa scala di pixel (ragazzo più alto, nel rapporto dei turnaround: 1,158). In gioco 1 pixel d'arte = 4 pixel a schermo, filtro nearest; proiettili ed effetti alla stessa densità.
- Pixel interi, nessun anti-aliasing, nessuna semitrasparenza tranne l'ombra. Toon a 4 toni con luce fissa dall'alto a sinistra; vista dall'alto a 25°. Tutto è visto di fronte, anche gli edifici (niente viste quasi isometriche).
- Contorno esterno 1 px #3a1418.
- **Palette Player:** pelle #9c5536 #d9864f #faaf72 #ffc994; capelli #5e1c1f #912a2a #d13d3b #ec6a52; costume #4f7f88 #6a9ea6 #96cbcf #c4eef0.
- **Palette sabbia:** #8a6a3e #b8925a #e3c084 #f6e2b0.
- **Palette nemica base:** capelli #2a1240 #4b2a78 #7043a1 #a97fd9; costume #16503a #25805a #3db57d #8de0b4; pelle e viso come il Player.
- **Palette ragazzo:** pelle #8f4a2c #c97847 #e99d63 #f8b47a; capelli e barba #2b140c #4d2a1e #6b3a26 #9b573b; bermuda #6e2818 #9e3f2c #c4553a #dd7050; occhi #1f3319 / #4e7a34; perline #1e0d07 con #c0392b #e8c547 #2e8b45.
- **Occhi** non renderizzati ma timbrati a pixel: 2×3 (scuro + riflesso in alto a destra, riga bassa più chiara); nei profili un solo occhio 1×3; la nemica tiene un occhio 2×3 nelle diagonali anteriori. Sguardo dolce, mai inclinato (inclinato sembra arrabbiato). Bocca 2 px #c25a4a solo di fronte. Ragazzo: occhi 2×2 di fronte (scuro + riflesso, riga bassa verde) e 1×2 di profilo, sopracciglia piatte 2×1 #6b3a26, bocca #b5483a.
- **Braccia leggibili** nelle viste laterali e diagonali: contorno 1 px sul busto dove il braccio lo nasconde, senza anelli sull'attaccatura della spalla.
- **Ombra:** proiezione verticale del corpo, #3a1418 semitrasparente, più piccola quando i piedi sono in aria. Nessuna ombra può coprire un personaggio.
- **Elementi di scena:** stessa densità di pixel dei tile, 4 toni, luce dall'alto a sinistra, contorno #3a1418, ombra incorporata.
- **Proporzioni:** chibi ma vicine al concept (testa grande, corpo non troppo schiacciato).
- **Animazioni:** l'idle muove solo il busto, con piedi e bacino fermi (non deve "saltellare"); nella camminata Nord/Sud le gambe sono leggermente divaricate ma non troppo; ogni animazione d'attacco chiude il ciclo tornando alla posa base.
- Ogni proiettile o effetto che ruota con la mira va disegnato verso destra e simmetrico in verticale, così la luce resta in alto anche lanciando a sinistra.

## 9. Vincoli dell'utente

- Collisioni e RayCast2D si possono modificare se serve per adattarli alla grafica o al gioco; verificare poi in gioco.
- Modificare il gameplay esistente solo se strettamente necessario.
- Scene e nodi si possono riorganizzare e ottimizzare se il risultato visivo e funzionale resta lo stesso; verificare l'equivalenza.
- Solo filtro nearest; rispettare lo stile della sezione 8.
- Nel progetto restano solo le risorse in uso, senza suffissi di versione; non ricreare né citare versioni precedenti.
- `.vscode/settings.json` è gestito dall'utente: non toccarlo.
- I commit li fa l'utente.

## 10. Stato attuale

### 10.1 Punti approvati

Funzionamenti e comportamenti approvati dall'utente: sono il riferimento per gli sviluppi futuri.

- **Protagonista:** aspetto e movimenti; velocità di lancio che parte bassa e cresce solo comprandola.
- **Palla di sabbia:** lancio, impatto e caduta dei colpi mancati.
- **Nemica base:** aspetto, movimenti, flirt, caduta con sbuffo; percorso verso un proprio posto attorno al ragazzo; le nemiche non si urtano tra loro.
- **Ragazzo:** aspetto e movimenti.
- **Chiosco e negoziante:** concept, aspetto e gesti; senza sgabelli. Nome "Chiosco da Sandro". Categorie Giocatore, Partner, Bonus come definite nella sezione 4.
- **Economia di base:** valori dell'ondata 1, monete fisse per nemica senza crescita per ondata, prezzi fissi.
- **Bonus di fine ondata:** regole della sezione 3 e animazione del popup.
- **Mondo:** inquadratura fissa con il ragazzo al centro; terreno di sola sabbia, battigia e mare; mappa del tutorial; elementi di scena e loro disposizione; granchio animato.
- **Interfaccia:** bande in legno scurite, icone dell'HUD, barre a tubo, numeri fluttuanti.
- **Icone degli oggetti:** stile illustrato, con il frullato come riferimento.

### 10.2 Punti in lavorazione

Sviluppi in corso, in test o in attesa di valutazione e approvazione.

- **Chiosco frontale:** versione vista di fronte con bancone più profondo, e sua posizione; da far approvare (l'utente può chiedere di spostarlo).

### 10.3 Punti aperti

Sviluppi decisi, da avviare.

- **Bilanciamento urgente del negozio (primo punto, da riprendere):** al primo playtest i potenziamenti del Giocatore per velocità di movimento e velocità di lancio sono già acquistabili nella prima e nella seconda ondata, troppo presto. L'utente li vuole disponibili non prima della quarta o quinta ondata. Direzione scelta: alzare i prezzi di questi potenziatori (non aumentare danni o velocità d'attacco delle nemiche). In più, per gli oggetti acquistabili più volte con un massimo, ogni acquisto successivo deve costare più del precedente (ipotesi: +50%, fattore da decidere); da verificare se già previsto, altrimenti da aggiungere. Questo prevale sul punto "Prezzi fissi" delle regole d'acquisto, da riscrivere quando si decide.
- **Coda delle nemiche attorno al ragazzo:** quando i posti attorno a lui sono tutti occupati, le nuove nemiche si fermano appena vicine al gruppo, in attesa, e ripartono quando si libera un posto.
- **Varianti di colore e classi di nemiche** (vedi concept, sezione 2).
- **Fuga del ragazzo al game over:** scenetta in cui cede e scappa.
- **Negozio:** prezzi definitivi; nuovi oggetti per Giocatore, Partner e Bonus, compresi altri bonus temporanei.
- **Negozio, quando ci saranno molti oggetti:** verificare che le schede stiano nel pannello o rimpicciolirle; rivalutare la suddivisione di Giocatore e Bonus.
- **Bilanciamento:** dopo i playtest, valutare insieme progressione delle nemiche e potenziamenti acquistabili (danno della protagonista, massimi di moralità e fedeltà, altri bonus). Il giocatore cresce senza limite, quindi le nemiche non hanno tetto. Prezzi fissi; un eventuale aumento graduale solo ogni 5 o 10 ondate, più avanti.
- **Level design del tutorial:** rifinirlo.
- **Export reale:** il catalogo degli oggetti deve entrare nel pacchetto e il negozio deve popolarsi.
- **Playtest completo:** menu, ondate, acquisti (anche con il popup del bonus mentre il negozio è aperto), game over.
- **Restyling grafico di interfaccia e menu**, dopo la fase funzionale. Punto di partenza scelto dall'utente per lo sfondo del menù principale e le sue voci: la scena di spiaggia (cielo a gradiente, sole con alone, mare, battigia ondulata, palma) creata con GIMP, conservata come base. Sarà sviluppata con GIMP, con Codex/ImageGen come riferimento.

## 11. Idee future

Idee e concept su cui ragionare prima di formalizzarli e spostarli nei punti aperti.

- Ondate infinite oppure un limite; modalità di sfida diverse; obiettivi o campagna; altri livelli.
- **Versione mobile:** il gioco sa già se è usato su mobile (tablet compresi); da definire come distinguere i controlli. Ipotesi: movimento con joystick virtuale a sinistra (spingendo a fondo si corre); attacco con un'unica azione a destra con mira automatica sulla nemica più vicina, oppure un secondo joystick di mira per la mira libera. Da adattare anche negozio, pausa, dimensioni di pulsanti e testi, e da verificare su un telefono vero la leggibilità dei personaggi.
- Il ragazzo, al game over, scappa con l'ultima nemica che lo ha attaccato.
- Rigenerazione leggera di moralità e fedeltà tra le ondate (per esempio +10%), come oggetto acquistabile o come regalo.
- **Regali di fine ondata:** ogni tot ondate il giocatore sceglie un bonus tra alcuni proposti; si ottengono solo così, non nel negozio (la rigenerazione leggera è un candidato). Da definire: frequenza, quanti bonus proposti, elenco e interfaccia di scelta.
- Bonus temporanei con limiti diversi dal numero di ondate.
- Animazione del conto alla rovescia della prossima ondata.
- Ogni tanto un fumetto sopra Sandro con una battuta.
- Transizioni tra le profondità del mare.
- Riordino delle cartelle del progetto (proposta in CODE_MAP).
