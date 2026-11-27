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
  - Quando moralità e fedeltà sono a zero il ragazzo non è più fedele e se ne va con la ragazza che lo ha conquistato: è il game over.
- **Come attaccano le nemiche:** non fanno danno fisico. Fanno pose, avances e movimenti sensuali verso il ragazzo; quando la moralità è a zero arrivano anche a toccarlo.
- **Stile delle avances:** le nemiche restano sempre vestite (costumi da spiaggia), niente nudità. Pose ammiccanti e ironiche, fumettistiche e volutamente esagerate (sguardi, baci, capelli, appoggiarsi, braccio al collo). A moralità zero il contatto è sensuale ma ironico: breve e comico, con cuoricini ed espressioni esagerate. Deve essere sempre evidente che le ragazze ci provano attivamente.
- **Reazioni del ragazzo:** con la moralità attiva guarda le ragazze con curiosità, senza malizia; a moralità zero le guarda con più interesse; infine cede e se ne va con l'ultima che lo ha attaccato.
- **Nemiche:** ragazze in spiaggia più belle della protagonista, con la chioma voluminosa e colori variabili di capelli, occhi, costume e pelle. Sono previste diverse "classi": da quelle molto resistenti, con molto danno ma lente (movimento e frequenza di attacco), a quelle fragili e veloci con danno costante, con un ampio range intermedio. Ogni classe può avere un aspetto distinto. Oggi esiste solo la nemica base.
- **Valuta:** le monete sono quelle perse dalle ragazze sconfitte.

## 3. Come funziona il gioco

### Comandi

- Movimento con le frecce (o tasti configurati e gamepad); Spazio tenuto premuto fa correre (velocità doppia).
- Tasto destro del mouse: lancio della palla di sabbia verso il puntatore.
- F: apre il negozio, solo davanti al bancone e durante la pausa tra due ondate.
- Esc: chiude il negozio oppure apre e chiude la pausa.

### Player

- Velocità di movimento a tre livelli; si sale comprando l'Infradito Conchiglia. Ogni livello dà +25% (320, 400, 480 px/s a piedi); la corsa raddoppia la velocità del livello attuale.
- La protagonista non può uscire dallo schermo di gioco. Parte sulla sabbia accanto al telo rosso dell'ombrellone di sinistra (in basso a sinistra): è il suo ombrellone.
- **Lancio:** la palla parte quando il braccio la lancia; si può lanciare anche camminando e correndo. Se si cammina in una direzione e si lancia nell'altra, la protagonista resta rivolta verso dove lancia anche tra un lancio e il successivo (per circa 0,4 secondi dopo l'ultimo lancio), senza tornare per un istante alla camminata verso la direzione di marcia.
- **Velocità di lancio a tre livelli**, si sale solo comprando il Corso di Schiacciata (decisione dell'utente): lenta (come la camminata), media, veloce.
- Non si può lanciare di nuovo finché il gesto precedente non è quasi finito.
- Danno iniziale della palla: 10.
- La palla colpisce una nemica in qualunque punto del corpo e scoppia; scoppia anche contro il chiosco e gli ostacoli. Se non colpisce nulla, ricade sulla sabbia e si disfa.

### Nemiche e ondate

- Le nemiche nascono fuori dall'inquadratura, da tutti i lati tranne il mare, e camminano verso il ragazzo aggirando ostacoli e altre nemiche. Nelle ondate fino a 4 nemiche nascono tutte insieme; con più di 4 nascono una alla volta, circa ogni 1,5 secondi, così non arrivano tutte nello stesso momento.
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
- moralità al massimo: +50%;
- moralità sotto il massimo e oltre il 50%: +25%;
- moralità tra 0 (escluso) e il 50% (compreso): +10% (il caso "esattamente 50%" non è stato specificato dall'utente ed è trattato così);
- moralità a 0: nessun bonus.

Il bonus, se maggiore di zero, è annunciato da un popup animato al centro dello schermo con la percentuale e le monete guadagnate; non blocca il gioco.

### Game over e menu

- **Scenetta di game over:** appena la fedeltà arriva a zero il gioco si ferma (niente più nemiche, attacchi, lanci, negozio o pausa; le palle già in volo e le nemiche che stanno cadendo finiscono, ma le palle non fanno più danno) e parte subito la scenetta. Il ragazzo e l'ultima nemica che lo ha attaccato scendono verso il basso, mentre la protagonista, da dove si trova, cammina verso il suo ombrellone; le altre nemiche restano ferme e guardano il ragazzo. Quando tutti e tre sono arrivati, ragazzo a sinistra e nemica a destra si guardano: lui le manda un bacio (bacia la mano e soffia), un cuoricino vola da lui a lei, lei arrossisce con le mani sulle guance e sopra di lei salgono in diagonale due cuoricini piccoli che sfumano. Dopo circa 2 secondi lui le si avvicina e la segue: escono insieme dall'inquadratura verso destra, un po' più svelti. Appena si allontanano la protagonista, che fino a quel momento guardava il ragazzo, si volta verso il basso e piange con le mani in faccia e le lacrime; le altre nemiche si curvano deluse continuando a guardare la coppia che se ne va. Circa 1 secondo dopo l'uscita della coppia compare il pannello con Ricomincia, Torna al Menù, Esci.
- Menu principale con Nuova partita, Opzioni (volume e muto), Tutorial. Pausa con Esc: Riprendi, Ricomincia, Torna al Menù.
- La musica (unico brano, in loop) suona nel menu; in partita non c'è musica.
- **Effetti sonori:** coerenti con il lancio, materici e morbidi, senza suoni arcade marcati; per ora senza voci. Il lancio della palla di sabbia ha un suono breve di sabbia lanciata (un fruscio con grana), che parte quando la palla viene rilasciata, in quattro varianti. Il colpo a una nemica ha un suono sabbioso corto, in quattro varianti; la sua sconfitta ha un suono più pieno (caduta a sedere con sbuffo). Ogni suono ripetuto cambia a caso di poco tono e volume, e la stessa variante non suona due volte di fila. Quando cade l'ultima nemica suona un jingle di vittoria (fanfara di ottone "wah" con ukulele, pad e batteria, nello stesso mondo sonoro del game over ma allegro). Nella pausa tra le ondate, a 5, 4, 3, 2 e 1 secondi dalla nuova ondata, un tic per ogni numero; allo scadere un breve jingle dello stesso ottone annuncia l'inizio dell'ondata (la prima ondata parte senza). Ogni acquisto nel negozio suona come monete che tintinnano con un "ding" finale (tre varianti); un acquisto non possibile non ha suono, perché il pulsante è disabilitato. Quando compare il pannello di game over parte uno stinger di circa 3 secondi, comico e pieno, alla "ops, hai perso!": un ottone che fa "wha wha wha waaah" e scivola verso il basso, sostenuto da pad, ukulele, basso e batteria in tono maggiore. Interrompe la musica di sottofondo, che in partita non c'è ancora. Nella scenetta di game over ci sono lo schiocco del bacio del ragazzo (due piccoli pop ravvicinati, "mu-ah", il primo appena accennato) e uno sfavillio per i due cuoricini piccoli e il rossore della nemica. Non hanno suono passi, attacchi delle nemiche, apertura del negozio e palla che ricade. Il volume dei suoni non è ancora regolabile a parte dal volume generale delle Opzioni.

## 4. Negozio

- Nome ufficiale: **"Chiosco da Sandro"**; il negoziante si chiama Sandro. È un chiosco sulla spiaggia, in alto a sinistra del ragazzo.
- Si apre con F stando davanti al bancone, solo durante la pausa tra le ondate. Mentre il pannello è aperto il Player non si muove e non lancia. Uscire dall'area, premere Esc o la fine della pausa lo chiudono.
- **Pannello:** mostra le monete disponibili e divide gli oggetti in tre gruppi: Giocatore, Partner, Bonus. Ogni oggetto ha icona, nome, descrizione e prezzo, in schede piccole per poterne aggiungere molti (richiesta dell'utente). Partner ha una sola sezione "Moralità e Fedeltà", divisa in tre righe (moralità, fedeltà, entrambi) da separatori sottili; ogni riga inizia con un'icona al centro (scudo, cuore, scudo e cuore in diagonale) e anche Giocatore (palla di sabbia in volo) e Bonus (regalo) hanno un'icona di riga. Giocatore e Bonus, per scelta dell'utente, non sono suddivisi in altre sezioni finché non ci saranno abbastanza oggetti. Le schede sono compatte (testo, immagini e pulsanti piccoli) perché ne stiano molte per riga.
- **Regole d'acquisto:** non si può comprare se le monete non bastano, se l'oggetto ha raggiunto il massimo di acquisti, se è inutile o sprecato o se non è ancora acquistabile per sblocco o attesa (vedi sotto). **Ripristini:** il 25% si usa sempre, purché la barra non sia piena; il 50% solo se non ripristina più di quanto manca (con il massimo a 100, barra a 50 o meno); i ripristini al 100% sono premi (vedi sotto) e si possono prendere se la barra (o almeno una delle due, per Entrambi) non è piena. La scheda dice il motivo nel tooltip ("Ripristinerebbe 50 di moralità, ma ne mancano 49", "La moralità è già al massimo").
- **Prezzi crescenti** (prezzi sempre a cifre tonde, multipli di 5, con aumento composto del 15%):
  - Gli oggetti **acquistabili sempre** (senza massimo) salgono del 15% a ogni multiplo di 5 ondate finite: dalla pausa dopo l'ondata 5 costano il 15% in più, dopo la 10 circa il 32% in più, e così via.
  - Gli oggetti **con un massimo di acquisti** hanno un calcolo a parte: il prezzo sale del 15% a ogni livello già comprato (il secondo costa il 15% più del primo, il terzo il 15% più del secondo) e non dipende dall'ondata.
- **Sblocchi per ondata:** gli oggetti con massimo sono potenziamenti e bonus, per questo costano più della media e si sbloccano solo avanzando: "dall'ondata X" significa nella pausa tra l'ondata X e la X+1. Prima dello sblocco la scheda è visibile ma non acquistabile, con un tooltip che dice da quando lo sarà. Ogni scheda non acquistabile ha un tooltip con il motivo: livello massimo raggiunto, già attivo per quante ondate, barra già al massimo, monete che ancora servono. Lo sblocco vale per l'oggetto, non per ogni livello.
- **Sandro avvisa e ringrazia:** nella pausa dopo un'ondata multipla di 5, quando i prezzi salgono, nel fumetto di Sandro compare, con il testo più piccolo del solito per occupare poco più dei ringraziamenti, "L'inflazione colpisce! Stessa qualità, ma del 15% in più!" (la percentuale è quella dell'aumento). Scompare da solo dopo circa 4 secondi (i ringraziamenti dopo circa 3); si zittisce prima se si apre il negozio (interagire con lui, anche senza comprare) o finisce la pausa. Quando si chiude il negozio, in qualunque modo, Sandro dice per circa 3 secondi "Grazie per l'acquisto!" se si è comprato almeno un oggetto in quella visita, altrimenti "Grazie per la visita!".
- **Disponibilità periodica:** la Barretta Energetica è una ricompensa a crediti: ogni volta che si finisce un'ondata multipla di 4 (4, 8, 12...) si ha diritto a un acquisto, che si può fare in qualsiasi pausa successiva; un credito non usato non scade e si somma al successivo (a ondata 8 se ne possono comprare due). Quando i crediti sono finiti la scheda dice tra quante ondate ne arriva un altro. Il prezzo sale del 15% ogni 5 ondate come per gli altri oggetti acquistabili sempre. Il Gelato Fondente si sblocca dopo l'ondata 5 e resta acquistabile finché non lo si compra; se lo si compra nella pausa dopo l'ondata X, funziona nell'ondata X+1, non è acquistabile nella pausa dopo la X+1 e lo torna a essere dopo la X+2, e così via. Le due schede restano visibili ma non acquistabili, con un tooltip che dice tra quante ondate potranno essere comprate.
- **Categorie** (definizione dell'utente, vincolante per ogni nuovo oggetto):
  - **Giocatore:** potenziamenti della protagonista (danno, rapidità di lancio, movimento e simili).
  - **Partner:** tutto ciò che riguarda il ragazzo: ripristino di moralità e fedeltà, aumento dei loro massimi e altro.
  - **Bonus:** extra che non riguardano né il ragazzo né la ragazza, come il bonus sulle monete; alcuni possono essere temporanei.
- **Oggetti temporanei:** comprati nella pausa, valgono dall'ondata successiva per il numero di ondate indicato. Finché sono attivi non si possono ricomprare, quindi non si sommano.
- **Oggetti attuali** (prezzi base e sblocchi provvisori, da tarare con i playtest; i prezzi crescenti si applicano come descritto sopra):

| Oggetto | Categoria | Effetto | Prezzo base | Massimo | Sblocco |
| --- | --- | --- | --- | --- | --- |
| Acqua Tonica | Partner / Moralità | ripristina il 25% della moralità | 45¢ | illimitato | subito |
| Granita al Limone | Partner / Moralità | ripristina il 50% | 75¢ | illimitato | subito |
| Frullato ai Frutti di Bosco | Partner / Moralità | ripristina il 100% | premio | un premio ogni 5 ondate dalla 5, uno solo tra i tre ripristini al 100% |
| Crema Protezione 50+ | Partner / Moralità | massimo +25% del valore iniziale (riempie la parte aggiunta) | 300¢ | 4 | dopo l'ondata 5 |
| Ombrellone | Partner / Moralità | dimezza la perdita di moralità per 3 ondate | 120¢ | temporaneo | subito |
| Caramelle alla Menta | Partner / Fedeltà | ripristina il 25% della fedeltà | 45¢ | illimitato | subito |
| Patatine al Rosmarino | Partner / Fedeltà | ripristina il 50% | 75¢ | illimitato | subito |
| Milkshake alla Fragola | Partner / Fedeltà | ripristina il 100% | premio | come sopra |
| Braccialetto Portafortuna | Partner / Fedeltà | massimo +25% del valore iniziale | 300¢ | 4 | dopo l'ondata 5 |
| Settimana Enigmistica | Partner / Fedeltà | dimezza la perdita di fedeltà per 3 ondate | 120¢ | temporaneo | subito |
| Frullato Frutti di Bosco e Fragola | Partner / Entrambi | ripristina il 50% di moralità e di fedeltà, dall'ondata 15 il 100% | premio | come sopra |
| Barretta Energetica | Giocatore | danno +20% del danno iniziale | 120¢ | illimitato | un acquisto ogni 4 ondate dalla 4, cumulabile |
| Corso di Schiacciata | Giocatore | un livello di velocità di lancio in più | 120¢ | 2 | dopo l'ondata 2 |
| Infradito Conchiglia | Giocatore | un livello di velocità di movimento in più | 225¢ | 2 | dopo l'ondata 4 |
| Salvadanaio a Forma di Granchio | Bonus | monete +15% | 150¢ | 5 | dopo l'ondata 5 |
| Gelato Fondente | Bonus | monete raddoppiate nella prossima ondata | 50¢ | temporaneo (1 ondata) | dopo l'ondata 5, poi una pausa saltata dopo ogni acquisto |

- **Premio di ripristino a scelta:** i ripristini al 100% (moralità, fedeltà, Entrambi) non si comprano: sono premi gratuiti per chi resiste alle ondate (se resisti, il gioco ti rimette a posto). Ogni volta che si finisce un'ondata multipla di 5 (5, 10, 15...) si ha diritto a **un solo premio da scegliere tra i tre**: il Frullato ai Frutti di Bosco (moralità), il Milkshake alla Fragola (fedeltà) o il Frullato Frutti di Bosco e Fragola (Entrambi), così si decide in base a quale barra è messa peggio. Scelto uno, gli altri due aspettano la prossima ondata premio. Il premio si prende in qualsiasi pausa successiva, non scade e si somma al successivo (due crediti = due premi). Perché la scelta abbia senso, Entrambi ripristina il 50% di ciascuna barra fino all'ondata 14; dalla pausa dopo l'ondata 15 ripristina il 100% di entrambe (la descrizione della scheda mostra la percentuale di ora). Un premio si può prendere se la barra non è piena (Entrambi: se almeno una barra non è piena). Se non si può, la scheda dice perché, e dice tra quante ondate arriva il premio seguente. Immaginario: il frullato Entrambi unisce quello ai frutti di bosco e quello alla fragola.
- **Icone degli oggetti:** illustrate, nello stile di concept e copertine (contorno caldo scuro, colori vivi, cel shading). Il frullato è il riferimento di stile approvato. Le due granite hanno ghiaccio giallo limone e una coppetta di carta con fascia corallo. Dal ghiaccio sporge il manico del cucchiaino rosso. La variante aromatizzata si riconosce dagli aghi e dal rametto di rosmarino.
- **Nuovi oggetti:** se l'utente non li indica, nomi e descrizioni li sceglie l'agente rispettando spiaggia, tono ironico e contesto. Devono essere cose plausibili in un baretto o bancarella di spiaggia o legate agli sport estivi. Gli oggetti acquistabili più volte non devono essere cose che nella realtà si comprano una volta sola (per esempio un anello di fidanzamento).

## 5. Mondo di gioco

- **Livello tutorial:** l'unico livello attuale, con level design semplice per imparare i comandi, ispirato alle copertine. La mappa è più grande dell'inquadratura e le nemiche arrivano da tutti i lati tranne il mare.
- **Inquadratura fissa** (decisione dell'utente): la camera non segue il Player e mostra l'intera spiaggia giocabile. Il ragazzo sta al centro dello schermo, il Player parte davanti a lui.
- **Terreno:** solo sabbia, battigia (con la sabbia bagnata) e mare con le sue profondità. Scogli ed erba non sono terreno (scartati dall'utente: "vanno bene per un platform 2D", e i personaggi ci passerebbero sopra); rocce, alberi, fiori e simili sono elementi di scena. La sabbia ha particolari sparsi a caso (increspature, piccole dune, luccichii, sassolini, conchiglie, puntini), mai uguali accanto. Il mare forma una baia in alto a destra.
- **Elementi di scena:** disposizione ispirata a una spiaggia libera italiana, con pochi elementi e un criterio (richiesta dell'utente):
  - macchia di palme con cespugli e fiori ai piedi sul lato opposto al mare (in alto a sinistra, dietro il chiosco, a sinistra, in basso a sinistra, in basso);
  - punta della baia con gruppo di scogli; ciottoli e conchiglie sulla linea delle mareggiate; un tronco spiaggiato lungo la riva;
  - due soli gruppi di ombrelloni: a destra due aperti con due teli e una tavola; in basso a sinistra uno aperto con telo e tavola (quello della protagonista);
  - il centro libero.
- **Solidi e decorazioni:** palme, rocce medie e grandi, cespugli, ombrelloni, tavole piantate, tronchi, botti e cartello bloccano personaggi e palle di sabbia. Ciottoli, conchiglie, fiori, palme giovani, teli e tavole sdraiate sono decorazioni a terra, calpestabili.
- **Granchio:** si muove (un animaletto non deve essere fermo: richiesta dell'utente). Non è calpestabile.
- Regola di disposizione: gli ostacoli non stanno troppo vicini tra loro né al chiosco, così le nemiche non si incastrano.

## 6. Personaggi

### Protagonista

- Ragazza della spiaggia del concept: chioma rossa voluminosa, costume turchese.

### Nemica base

- Donna adulta atletica e formosa, proporzioni chibi, vita definita, seno e glutei un po' più pieni della protagonista senza eccessi. Capelli viola lunghi e lisci fino alla vita bassa; bikini smeraldo a triangolo con lacci e fiocchi ai fianchi, slip sgambato.
- **Varianti di colore:** a ogni nascita ogni nemica riceve a caso un colore di capelli (viola del concept, nero, castano, biondo, rosa, azzurro, acqua) e un colore di costume (verde del concept, blu, nero, bianco, rosso, viola; niente colori vicini alla pelle come rosa, arancione o giallo, perché sembrerebbero nude), mai lo stesso nome su entrambi. La prima nemica di ogni ondata ha sempre i colori del concept (capelli viola, bikini verde). Il bikini è ben leggibile anche a dimensione di gioco (coppe, lacci e slip più ampi). Ogni colore ha tre toni nello stile toon; pelle, occhi e contorni non cambiano. Le future classi di nemiche useranno lo stesso sistema.

### Ragazzo

- Adulto leggermente più alto delle ragazze, atletico e robusto senza eccessi muscolari; viso bello, occhi verdi, pelle moderatamente abbronzata.
- Capelli corti castano scuro, lati corti e parte superiore pettinata di lato (ispirazione: George Clooney). Barba corta castana su mento e mandibola con pelle libera sotto il labbro e piccolo pizzetto triangolare (ispirazione: Can Yaman).
- Collanina sottile da spiaggia con perline scure e accenti rosso, giallo, verde d'ispirazione giamaicana. Bermuda fino a metà ginocchio, terracotta caldo con cordino chiaro (toni Autunno dell'armocromia).

### Negoziante (Sandro)

- Gestore maturo e ordinario: viso allungato con naso pronunciato, tratti morbidi e piccoli segni d'età, senza baffi; pelle abbronzata, capelli mossi brizzolati schiariti dal sole, cappello di paglia con fascia petrolio, camicia hawaiana corallo a grandi motivi crema aperta su una canotta chiara.
- Sta dietro il bancone e ogni tanto pulisce bicchieri e bancone.
- **Fumetto di Sandro:** Sandro parla con un fumetto crema dal contorno bordeaux, in un solo pezzo con la sua coda sottile e allungata, che parte dalla zona della bocca di Sandro; il corpo si apre a destra, sopra il bancone (sopra il chiosco non c'è spazio). Dice l'avviso dell'aumento dei prezzi e i ringraziamenti (vedi sezione 4); è anche la base per le battute future.
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
- **Immagini promozionali:** logo intero, logo solo testo e le cover (sfondo vuoto, con personaggi, con personaggi e logo, quadrata; sezione 10.1). Nessun uso assegnato nel gioco; non eliminarle come inutilizzate.

## 8. Pipeline grafica e stile visivo

Leggere prima di toccare qualsiasi sprite. Tutte le nuove risorse grafiche (nemiche, ragazzo, oggetti, effetti) seguono questo stile e questi strumenti. Percorsi di concept, sorgenti e risorse: `Docs/CODE_MAP.md`, sezione Risorse grafiche.

### Strumenti

- **Blender** (MCP `blender`): personaggi animati, modello 3D chibi con rig, renderizzato a pixel. Guida `Docs/BLENDER.md`.
- **Pixelorama** (MCP `pixelorama`): oggetti piccoli, effetti, tile, ritocchi dentro la silhouette. Guida `Docs/PIXELORAMA.md`.
- **GIMP** (MCP `gimp`): immagini raster che non sono sprite di personaggio. Crea, compone e ritocca direttamente loghi, copertine, icone e illustrazioni dell'interfaccia, sfondi, testo, correzioni di colore e tono, ritagli, ridimensionamenti ed esportazioni in blocco, senza dover passare da Codex. Non genera concept art con l'IA e non sostituisce Pixelorama nel pixel per pixel. Indicazione dell'utente: Claude userà GIMP direttamente per ogni immagine del gioco (loghi, sfondi, concept e altro), con Codex/ImageGen solo come riferimento. Metodo scelto dall'utente: le immagini generate da Codex si ricalcano in GIMP il più possibile uguali, a livelli separati, così restano identiche nel tempo, si modificano aggiungendo o togliendo elementi e i loro pezzi (personaggi delle copertine, sfondi, decorazioni) si riusano in altre immagini senza le variazioni che Codex introdurrebbe rigenerandole. **Regola fissa dell'utente sul ricalco:** l'originale entra solo come riferimento (livello nascosto per i confronti) e ogni elemento si ridisegna da zero, nella stessa posizione e il più possibile uguale; non si ritagliano pezzi dell'originale per incollarli nella nuova immagine, né si usa l'originale come maschera da completare. Si possono riusare solo elementi già ricreati da zero (per esempio il logo solo testo dentro il logo completo). Metodo scelto: contorni misurati col codice sul riferimento e ridisegnati come tracciati vettoriali; colori, sfumature, luci e ombre dipinti da capo. **Modo di lavorare preferito dall'utente:** quando c'è un riferimento, ogni elemento si ricalca dalle zone di tono e dai contorni dell'originale invece di ricostruirlo a mano con forme proprie, che divergono troppo; a mano si disegna solo ciò che il riferimento non mostra (parti coperte o fuori cornice), nello stesso stile. I testi usano i font del progetto (Luckiest Guy, Fredoka), installati anche sul PC perché GIMP li veda. Guida `Docs/GIMP.md`.
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

- **Illustrazione singola del ragazzo:** prende il sole rivolto a destra, con gli occhi chiusi, il mento alzato e le mani sui fianchi. Pelle, capelli e costume mantengono i colori naturali, senza riflessi solari.
- **Illustrazioni della protagonista e della coppia:** da sola, lei prepara il lancio di una palla di sabbia. Tiene le ginocchia piegate, porta la palla dietro la spalla e tende la mano libera verso il bersaglio. Nella posa di coppia si appoggia a lui con la mano sul suo petto. Lui le cinge le spalle, inclina la testa verso di lei e sorride a bocca chiusa. Entrambi guardano chi osserva.

Funzionamenti e comportamenti approvati dall'utente: sono il riferimento per gli sviluppi futuri.

- **Protagonista:** aspetto e movimenti; velocità di lancio che parte bassa e cresce solo comprandola.
- **Palla di sabbia:** lancio, impatto e caduta dei colpi mancati.
- **Nemica base:** aspetto, movimenti, flirt, caduta con sbuffo; percorso verso un proprio posto attorno al ragazzo; le nemiche non si urtano tra loro.
- **Concept di Pesante, Veloce e Influencer:** turnaround dedicati con vista frontale, profilo rivolto a destra e vista posteriore, approvati come riferimenti per la modellazione. La Veloce ha un fisico slanciato e tonico.
- **Ragazzo:** aspetto e movimenti.
- **Chiosco e negoziante:** concept, aspetto e gesti; senza sgabelli; versione frontale con bancone più profondo e relativa posizione. Nome "Chiosco da Sandro". Categorie Giocatore, Partner, Bonus come definite nella sezione 4.
- **Economia di base:** valori dell'ondata 1, monete fisse per nemica senza crescita per ondata.
- **Bonus di fine ondata:** regole della sezione 3 e animazione del popup.
- **Fumetto di Sandro:** grafica, dimensione, posizione e durata dei ringraziamenti; avviso dell'aumento dei prezzi (sezione 4).
- **Scenetta di game over:** sequenza, tempi e sprite come descritti nella sezione 3 ("Game over e menu"): camminata e bacio del ragazzo, imbarazzo e delusione delle nemiche, pianto della protagonista, cuoricini. Punto di partenza della protagonista accanto al telo del suo ombrellone, senza l'ombrellone chiuso.
- **Mondo:** inquadratura fissa con il ragazzo al centro; terreno di sola sabbia, battigia e mare; mappa del tutorial; elementi di scena e loro disposizione; granchio animato.
- **Suono dell'acquisto:** due note, una breve e una più alta e lunga (tipo moneta raccolta), in tre varianti.
- **Interfaccia:** bande in legno scurite, icone dell'HUD, barre a tubo, numeri fluttuanti.
- **Icone degli oggetti:** stile illustrato, con il frullato come riferimento.
- **Logo solo testo:** ricreato in GIMP a livelli (lettere in Luckiest Guy disposte e inclinate come nell'originale, contorno scuro e bordo crema, gradienti giallo-arancio e corallo-rosso con lo stacco lucido sfumato da una dissolvenza corta, bordi interni chiari, riflessi bianchi).
- **Logo completo:** ricreato in GIMP a livelli attorno al logo solo testo (sole con nuvole, due palme, foglie, ibisco, schizzi d'acqua, onde, isolotto di sabbia, conchiglia, stella marina, raggi).
- **Cover del gioco:** ambiente di spiaggia ricostruito in GIMP su una tela estesa che funziona anche da sola: cielo e nuvole, isolotto con la collina lontana, scogliera che prosegue in un promontorio, mare con onde e schiuma, sabbia, scogli in acqua e sulla riva, due palme, chiosco con tetto di paglia che continua oltre il bordo sinistro in prospettiva, tavola da surf, barile con la corda, cespo con l'ibisco, cespugli, rocce in primo piano, stella marina e conchiglie. Gli elementi sono ricalcati dall'originale; le parti che l'originale non mostra (dietro i personaggi, sotto le foglie, oltre la cornice) sono dipinte nello stesso stile. Il cespo con l'ibisco sale verso destra come il fiore; cespugli e rocce poggiano sulla sabbia con ombre di contatto. I personaggi (coppia con palla di sabbia, briciole, segni "!" e gocce di sudore; rivale con cuoricini e scia rosa) sono i ritagli dell'originale, con le ombre ridisegnate: l'utente li tiene così e non vanno ricalcati. Immagini finite: logo intero, logo solo testo, sfondo senza personaggi né logo, sfondo con i personaggi, cover con personaggi e logo intero (personaggi più piccoli, la rivale staccata dalla coppia, il cespo con l'ibisco davanti alla gamba della rossa, logo nell'angolo in alto a destra), ognuna nella cornice originale 16:9 e in una versione più ampia (la tela estesa; per la cover con logo un suo ritaglio in 16:9 senza la fascia bassa e il bordo sinistro), più un'immagine quadrata con il logo intero in alto, tutto sul cielo a destra delle palme, e i personaggi sotto.

### 10.2 Punti in lavorazione

Sviluppi in corso, in test o in attesa di valutazione e approvazione.

- **Illustrazioni di flirt:** quattro pose a figura intera, una per nemica, con lo sguardo rivolto al ragazzo. L'Influencer lo guarda sopra gli occhiali abbassati, la nemica base lo invita con un dito, la Veloce gli lancia un bacio a metà passo e la Pesante gioca con una ciocca con fare sicuro. Le pose sono in attesa di valutazione come illustrazioni da comporre in altre immagini.
- **Coda delle nemiche attorno al ragazzo:** quando i posti attorno a lui sono tutti occupati, le nuove nemiche continuano a camminare finché non sono vicine a quelle già attaccate o in attesa, poi restano ferme lì; quando una di quelle che attaccano cade, la nemica libera che vede il posto lo prende. Obiettivo di gioco: costringere il giocatore a muoversi per sconfiggere le nemiche. Da provare in partita con tante nemiche.
- **Pacchetti di ripristino e righe con icona nel negozio:** il premio Entrambi e sezione "Moralità e Fedeltà" a righe con icona e schede compatte (sezione 4). Il premio ha un'illustrazione dedicata e le righe Giocatore e Bonus hanno come simboli una palla di sabbia in volo e un regalo. Le cinque icone sono nel pannello. Prezzi e sblocchi da provare in partita.
- **Varianti di colore della nemica base:** capelli e costume a colori casuali (sezione 6). Da provare in partita: scelta dei colori e leggibilità del bikini nelle pose di flirt.
- **Bilanciamento del negozio:** prezzi più alti a cifre tonde, aumento del 15% ogni 5 ondate per gli oggetti acquistabili sempre, aumento del 15% per livello per quelli con massimo, sblocchi per ondata, Barretta e Gelato con disponibilità periodica (sezione 4). I prezzi di ripristini, protezioni e potenziamenti sono circa 1,5 volte quelli di partenza, con le stesse proporzioni tra loro: alla fine della prima ondata si possono avere al massimo 81 monete, quindi il giocatore non riempie le barre fin dall'inizio, ma con le entrate di un'ondata (circa 70-80) riesce a ripristinare circa 40 punti di moralità o fedeltà, contro i circa 80-110 che le nemiche tolgono nelle ondate 3-4 di una partita di prova. Il Gelato Fondente costa 50¢ (prima 80¢): raddoppiando le entrate di un'ondata rende quanto l'ondata incassa, quindi a 100¢ era quasi pari e non conveniva mai; il prezzo giusto è circa metà di quello che rende. Il Salvadanaio costa 150¢, dà +15% per livello e si sblocca dopo l'ondata 5, perché con il +10% di prima e lo sblocco all'ondata 10 rendeva circa 20 monete a ondata e non conveniva mai; resta da ritarare sui numeri reali (si deve ripagare in 5-8 ondate). Nelle ondate 2-5 il danno subito supera comunque quello che il negozio può ripristinare, perché le nemiche si sconfiggono troppo lentamente: la salute delle nemiche cresce quindi più piano (alla ondata 5 è 64 invece di 78) il Corso di Schiacciata si può comprare già dalla pausa dopo l'ondata 2 a un prezzo (120¢) raggiungibile con due ondate di risparmio, per far salire il danno al secondo prima dell'ondata 5, e nelle ondate con più di 4 nemiche queste nascono una alla volta (circa ogni 1,5 secondi) invece che tutte insieme, perché chi attacca nello stesso momento fa crescere il danno col quadrato del numero di nemiche; la Barretta Energetica è una ricompensa a un acquisto ogni 4 ondate, così il danno del giocatore tiene il passo con la salute delle nemiche, e si può comprare in qualsiasi pausa dopo averla guadagnata, così il prezzo che sale a ogni multiplo di 5 non la rende irraggiungibile. Da riprovare in partita: se la moralità resta a zero già alle prime ondate, le altre leve sono numero di nemiche, danno e tempo tra gli attacchi. Un log dei playtest registra monete, acquisti e danni di ogni ondata per questa taratura. Da provare in partita, tarando prezzi e ondate di sblocco.
- **Ripristini come premio a scelta:** i tre ripristini al 100% sono un premio unico a scelta ogni ondata premio, con Entrambi al 50% fino all'ondata 14 (sezione 4). Da provare in partita: se il 50% di Entrambi prima dell'ondata 15 è un valore giusto, se conviene accumulare i crediti, e se senza i 100% in vendita il giocatore resta senza ripristini nelle ondate dure (nell'ultima prova la moralità è arrivata a 0 dall'ondata 17).
- **Frase di Sandro sui prezzi e conto alla rovescia da 5:** la frase ironica e breve sull'inflazione e i tic a 5, 4, 3, 2, 1 con un nuovo bip arcade (sezione 3 e sezione 4). Da provare in partita: leggibilità della frase nel tempo del fumetto e resa del nuovo suono dei tic.
- **Effetti sonori:** elenco nella sezione 3 ("Game over e menu"); il suono dell'acquisto e il jingle di fine ondata sono approvati (il jingle coincide nel tempo con la comparsa del testo del bonus di fine ondata). Da provare in partita per gli altri: bilanciamento tra i suoni, resa del jingle di inizio ondata e del game over, momento dello schiocco del bacio rispetto al gesto del ragazzo.

### 10.3 Punti aperti

Sviluppi decisi, da avviare.

Punto più importante: ondata difficile con le classi di nemiche.

- **Ondata difficile ogni 5 ondate (punto principale):** ogni quinta ondata più dura (nemiche più forti o veloci, oppure una nemica boss). Aumento dei prezzi e sblocchi del negozio a ogni multiplo di 5 sono già fatti (sezione 4); restano da definire difficoltà, boss e ricompense.
- **Classi di nemiche** (vedi concept, sezione 2), collegate all'ondata difficile: la nemica base c'è sempre; dall'ondata 5 possono comparire anche le altre classi (ondata di comparsa e frequenza di ognuna da definire). Ognuna avrà le sue varianti di colore con lo stesso sistema della nemica base e una silhouette ben distinta. I turnaround approvati guideranno la realizzazione di modelli e sprite. Restano da quantificare velocità, salute, danno e frequenza d'attacco. Classi decise:
  - **Direzione del concept (vale per tutte):** stesso stile e stesse proporzioni chibi della nemica base (stessa testa e stessa altezza), adulte, sempre vestite, turnaround a tre viste (fronte, profilo destro, retro) su fondo grigio. Ogni classe si riconosce a 64×64 pixel da una sola caratteristica forte nella silhouette, non da dettagli sottili; capelli e costume restano in pochi toni netti perché poi si ricolorano con le varianti, mentre pelle, occhi e contorni non cambiano. Le classi sono varianti dello stesso corpo (più largo, più stretto) con testa, capelli e accessori propri, così si riusano modello e animazioni.
  - **Valori decisi (rispetto alla nemica base, la cui crescita per ondata vale per tutte):** salute e danno sono moltiplicatori dei valori della base all'ondata in corso (la base attacca ogni 1,4 secondi e vale 18 monete). Pesante velocità 60%, salute ×2,5, danno ×2,5 ogni 2,8 secondi, 36 monete, subisce il 40% della spinta dei colpi, dall'ondata 5; Veloce velocità 165%, salute ×0,55, danno ×0,5 ogni 0,7 secondi, 13 monete, dall'ondata 5; Influencer velocità 90%, salute ×0,6, danno ×0,8 ogni 2 secondi, 24 monete, dall'ondata 7, al massimo 3 contemporanee. Probabilità che una nemica sia di una classe speciale: 20% dall'ondata 5, in salita fino al 40% dall'ondata 15. Piano di lavoro: `Docs/PIANO_CLASSI_NEMICHE.md`. Le classi speciali sono rare all'inizio e più frequenti con le ondate. Finché non ci sono gli sprite, le nuove classi usano un segnaposto.
  - **Attacco dell'Influencer:** si ferma su un anello più largo di quello delle nemiche che attaccano da vicino (circa una nemica di distanza in più) e non occupa i loro posti attorno al ragazzo; ogni 2 secondi manda un bacio volante, un cuoricino che vola verso il ragazzo e gli toglie moralità o fedeltà quando arriva. I cuoricini non si possono abbattere.
  - **Pesante:** una ragazza più robusta; lenta a muoversi, con molta più salute della base e tanto danno, ma in un tempo più lungo (attacca meno spesso). Aspetto: corpo più largo del 35-40% (spalle, fianchi, arti), imponente, fiera e dignitosa, mai una caricatura; capelli castano scuro raccolti in un grande chignon disordinato (la sua silhouette); costume intero blu reale con pareo crema annodato a un fianco; sguardo calmo e sicuro di sé.
  - **Veloce:** una ragazza più magra; più veloce a muoversi, con meno salute e meno danno, ma più rapido (attacca più spesso). Aspetto: corpo più stretto del 20-25%, slanciato e tonico, addome morbido e muscoli appena accennati su spalle, braccia e gambe; postura scattante; capelli biondo dorato in una coda altissima e lunga con frangetta (la sua silhouette); top sportivo corto e slip atletici rossi con striscia laterale bianca; sorriso furbo e occhi vivaci.
  - **Influencer:** seduce il ragazzo da lontano, ma non troppo: si ferma ad almeno la distanza di una nemica base dal ragazzo (distanza esatta da misurare) e da lì fa selfie e manda baci. Fragile, ti costringe a inseguirla. Nel concept è super truccata ma sempre sexy, ancora di più della nemica base. Aspetto: trucco da influencer a forme grafiche leggibili (ciglia lunghe, labbra lucide a broncio, guance illuminate), capelli biondo miele lunghi e lucidi con onde da piega e occhiali da sole grandi sulla testa, bikini bianco con anelli e finiture dorate, orecchini a cerchio, collana e bracciali dorati; tiene nella mano destra uno smartphone con cover colorata, il suo oggetto distintivo, sguardo ammiccante da selfie.
  - **Ladra di monete:** ti ruba monete e, se la sconfiggi, te le restituisce con un extra. Se non ha rubato nulla, lascia solo le sue monete normali. Se ha rubato anche una sola moneta, lascia le sue, quelle rubate e il 10% in più; da decidere se il 10% è calcolato sulle sue monete base o sulla somma delle sue e di quelle rubate. **Da decidere per primo: in che modo ruba** (a contatto con la protagonista, a distanza, quando passa vicino, quante monete alla volta, quando scappa o se resta a cercare di rubare).
  - **Miss Spiaggia (boss):** la nemica boss dell'ondata difficile, nome deciso. Da pensare a fondo (aspetto, abilità, combinazione con le altre classi, ricompensa), insieme al punto sull'ondata difficile.
- **Restyling grafico di interfaccia e menu**, dopo la fase funzionale, insieme alla gestione delle Opzioni (volume separato di effetti e musica, regolato dal menu). Punto di partenza scelto dall'utente per lo sfondo del menù principale e le sue voci: la scena di spiaggia (cielo a gradiente, sole con alone, mare, battigia ondulata, palma) creata con GIMP, conservata come base. Sarà sviluppata con GIMP, con Codex/ImageGen come riferimento.

## 11. Idee future

Idee e concept su cui ragionare prima di formalizzarli e spostarli nei punti aperti.

- **Ondate limitate per livello:** ogni livello avrà un numero massimo di ondate, forse 20 o 30; l'idea è avere più livelli da 30 ondate ciascuno, ognuno con il suo level design. Il resto (modalità di sfida, obiettivi o campagna, quanti livelli) se ne riparla più avanti.
- **Musica di sottofondo in partita:** oggi in partita non c'è musica (c'è solo il game over e i jingle di ondata). Idea da sviluppare, con la musica solo come accompagnamento sullo sfondo:
  - **Ruolo:** un sottofondo che non copre mai gli effetti sonori (più bassa dei suoni di gioco; l'ottone solista suona a tratti, non di continuo). Il volume di musica e di effetti sarà regolabile a parte nelle Opzioni.
  - **Coerenza con il game over:** punto di partenza è lo stinger del game over, quindi stessa tavolozza e stesso tono ironico e estivo: ottone con timbro "wah", ukulele a contrattempo, pad, basso funky sincopato, cassa, battito di mani e hi-hat leggeri, in Do maggiore con Fa e Do come accordi di base. Il game over è lo stesso mondo sonoro che crolla; restando nella stessa tonalità, lo stinger si innesta bene sulla musica che interrompe.
  - **Un'unica musica che si trasforma (idea dell'utente):** la musica non si interrompe e non cambia con uno stacco: sembra sempre un'unica canzone che cambia secondo la situazione, con dissolvenze e passaggi che la fanno scorrere senza interruzioni (è la tecnica della musica adattiva o interattiva). La sequenza: parte alla prima ondata come canzone di sottofondo; quando finisce l'ondata diventa il jingle di fine ondata; poi diventa la canzone della pausa di circa 20 secondi, sempre la stessa; poi diventa il jingle di inizio ondata; poi una canzone di sottofondo dell'ondata successiva, scelta a rotazione casuale tra un certo numero di canzoni (senza ripetere la stessa due volte di fila); e così via fino alla fine. Ogni canzone di sottofondo e la canzone della pausa si ripetono in loop senza stacchi finché l'ondata o la pausa non finiscono; le ondate alte durano anche più di un minuto.
  - **Regole per comporre in questo modo:** stesso tempo, stessa tonalità (Do maggiore) e battute della stessa lunghezza per tutte le canzoni e i jingle; i passaggi cadono sull'inizio di battuta o di un movimento (l'ondata finisce in un momento qualunque: la musica aspetta il battito o la battuta successivi, circa un terzo di secondo o poco più, oppure il jingle entra sovrapposto alla canzone che si dissolve in quel breve tratto, soluzione approvata dall'utente), su un accordo comune (Do) che ogni canzone attraversa a intervalli regolari; ogni canzone esportata come file separato per strumento, della stessa lunghezza, senza dissolvenze, con le code riportate all'inizio del loop; batteria e basso restano il filo conduttore tra una canzone e l'altra. Il jingle di fine ondata, la canzone della pausa e il jingle di inizio ondata vanno riscritti con lo stesso tempo (oggi 170 e 175 BPM) e in battute intere, senza la coda di riverbero dell'esportazione a singolo suono.
  - **La pausa:** una canzone della durata della pausa o in loop, nello stesso mondo sonoro, con qualche variante (stesso tempo e stessa tonalità) a rotazione così non è sempre identica ascoltata a ogni ondata; i tic del conto alla rovescia (5, 4, 3, 2, 1) suonano sopra di essa; il negozio aperto non la cambia; con Esc la musica va in pausa con il gioco.
  - **Game over:** all'inizio della scenetta la musica corrente si trasforma in un mix tra canzone di sottofondo e jingle del game over (per esempio la canzone che rallenta e si scurisce mentre entra lo stinger), così il passaggio risulta naturale e non uno stacco. Interrompe la musica solo in questo modo; lo stinger è già predisposto nel codice.
  - **Tappe (concordate con l'utente, non si fa tutto insieme):** (1, modello Opus) infrastruttura: gestore della musica con transizioni quantizzate e dissolvenze, una sola canzone di sottofondo, la canzone della pausa e i jingle di fine e inizio ondata riscritti in battute intere con lo stesso tempo, per verificare a orecchio se il passaggio sembra un'unica canzone; (2, modello Sonnet, a ricetta fissata) altre canzoni di sottofondo e varianti della canzone della pausa; (3, Opus) trasformazione della musica nel game over; (4, Opus per il progetto, Sonnet per i brani) vittoria (jingle, trasformazione e scenetta), quando si sceglierà il numero di ondate. Motivo: il lavoro delicato (progettare le transizioni, il codice del gestore, la coerenza di tempo e tonalità) va fatto con il modello più potente, perché un errore di impostazione costringe a rifare tutte le canzoni; la composizione ripetitiva con regole chiare può farla uno più economico.
  - **Da decidere:** quante canzoni di sottofondo (almeno 4-5), come si comporta la prima ondata (oggi parte senza jingle), cosa succede alla musica quando si apre il pannello di Esc, durata dei loop e delle dissolvenze, e se le ondate difficili e i boss hanno canzoni o strati propri (musica adattiva a strati: la canzone divisa per strumento, di cui il gioco alza o abbassa il volume secondo la situazione).
- **Vittoria:** un jingle di vittoria "opposto" a quello del game over: se il game over scende verso il basso, la vittoria sale verso l'alto. Suona al termine dell'ultima ondata (quando si deciderà il numero massimo di ondate di ogni livello), preceduto dalla musica che si trasforma come per il game over (la canzone che sale e si illumina mentre entra il jingle), e legato a una scenetta di vittoria dedicata, simile a quella del game over: da disegnare, con la protagonista, il ragazzo e le nemiche. Il jingle va scritto in LMMS con lo stesso mondo sonoro (ottone "wha" che sale, Do maggiore).
- **Versione mobile:** il gioco sa già se è usato su mobile (tablet compresi); da definire come distinguere i controlli. Ipotesi: movimento con joystick virtuale a sinistra (spingendo a fondo si corre); attacco con un'unica azione a destra con mira automatica sulla nemica più vicina, oppure un secondo joystick di mira per la mira libera. Da adattare anche negozio, pausa, dimensioni di pulsanti e testi, e da verificare su un telefono vero la leggibilità dei personaggi.
- **Negozio, novità sbloccate** (idee da valutare insieme):
  - **Avviso di Sandro sulle novità:** ogni volta che si sbloccano nuovi oggetti, Sandro dice nel suo fumetto una frase come "Ci sono nuovi oggetti nel negozio!", nella pausa in cui diventano acquistabili (stesso comportamento degli altri fumetti: compare e scompare da solo).
  - **Oggetti bloccati nascosti:** gli oggetti ancora da sbloccare non si vedono nel negozio; compaiono solo appena si sbloccano (oggi la scheda è visibile ma non acquistabile, con il tooltip di sblocco). Di conseguenza la scheda principale del negozio, quella che si apre per prima, deve essere Partner (oggi la prima è Giocatore), perché è quella con più oggetti disponibili fin dall'inizio.
  - **Quali oggetti:** decidere se Sandro, oltre a dire che ci sono novità, dice anche quali oggetti si sono sbloccati (per esempio "Ora ho la Crema Protezione 50+!"), e come gestire più oggetti sbloccati nella stessa pausa (un elenco breve, una frase generica o un nome a rotazione).
- **Grafica 2D disegnata al posto della pixel art (intenzione dell'utente):** personaggi, e poi il resto del mondo di gioco, nello stesso stile dei concept e delle icone (contorno caldo scuro, colori vivi, toni piatti), con la pixel art solo per piccole cose. Per ora il gioco resta in pixel art. Ricostruire i personaggi in automatico dai turnaround non basta: le tre viste del concept non descrivono in modo coerente i lati (attaccatura, basette, barba), quindi servono disegni veri per ogni direzione. Cosa servirebbe:
  - **Viste per direzione:** per ogni personaggio cinque disegni nello stesso stile e coerenti tra loro (fronte, tre quarti davanti, profilo, tre quarti dietro, retro; le altre tre direzioni si ottengono specchiando), visti dall'angolazione dall'alto della camera di gioco, generati da Codex.
  - **Parti separate:** ogni vista ricalcata in GIMP a livelli (testa, capelli, busto, braccia, gambe, costume, accessori), ridisegnata e non ritagliata, con le parti nascoste completate a mano.
  - **Animazione a ossa 2D in Godot:** per ogni direzione uno scheletro che muove le parti (idle, camminata, avances e gesti delle nemiche, lancio della protagonista, pose del ragazzo); le animazioni sono più rigide di quelle in 3D e vanno costruite direzione per direzione.
  - **Gioco:** celle più grandi, filtro lineare, nuova scala dei personaggi, ombre e contorni rifatti; poi chiosco, oggetti e terreno nello stesso stile per coerenza.
  - **Prova:** prima un solo personaggio, il ragazzo (meno animazioni), da confrontare in gioco con la pixel art.
  - **Alternativa:** personaggi 3D con capelli, basette e barba modellati come forme vere (non ricavati dai disegni) e shader a toni piatti con contorno; più fluido nelle animazioni, ma la somiglianza ai concept non è garantita.
- **Caposquadra (nuova classe di nemica):** poco pericolosa da sola, ma le nemiche vicine diventano più veloci o più forti (aura). È il bersaglio da colpire per primo. Da definire: raggio e intensità dell'aura, comparsa.
- **Nemica con scudo (nuova classe di nemica):** una nemica protetta da uno scudo che va distrutto prima di poterla abbattere; l'ombrellone non convince come scudo, da trovare un oggetto più adatto. Da definire: oggetto, direzione della protezione, resistenza dello scudo.
- **Fuoco continuo (oggetto del negozio, categoria Giocatore):** una volta acquistato, tenendo premuto il pulsante di lancio la protagonista lancia le palle di continuo, senza dover premere a ripetizione. Da definire: prezzo, sblocco, se il ritmo è quello normale di lancio o più lento, se è permanente o temporaneo.
- **Arma corpo a corpo a tema** (idea dell'utente): oltre al lancio di palle, un'arma da usare a distanza ravvicinata, per esempio un ombrellone o un altro oggetto da spiaggia, che colpisce ogni tot secondi più nemiche insieme, soprattutto nelle ondate alte, dove le nemiche si accumulano attorno al ragazzo. Da definire: come si ottiene (acquisto nel negozio, premio), tasto e animazione, tempo di ricarica, raggio e danno rispetto alla palla, e se ha livelli di potenziamento. Serve anche da spesa per le monete che a fine partita avanzano.
- Rigenerazione leggera di moralità e fedeltà tra le ondate (per esempio +10%), come oggetto acquistabile o come regalo.
- **Regali di fine ondata:** ogni tot ondate il giocatore sceglie un bonus tra alcuni proposti; si ottengono solo così, non nel negozio (la rigenerazione leggera è un candidato). Da definire: frequenza, quanti bonus proposti, elenco e interfaccia di scelta.
- Bonus temporanei con limiti diversi dal numero di ondate.
- Possibilità di saltare la scenetta di game over con un tasto, se dopo averla provata più volte risulta lunga.
- Animazione del conto alla rovescia della prossima ondata.
- Battute e freddure brevi che Sandro dice ogni tanto, a caso, nel suo fumetto (frasi da scrivere, frequenza da decidere).
- Transizioni tra le profondità del mare.
- Riordino delle cartelle del progetto (proposta in CODE_MAP).
