# Structs und File I/O

## Lernziel

Das Arbeiten mit eigenen Datentypen und Dateioperationen soll am Beispiel eines Vokabeltrainers geübt werden. 

## Beschreibung

Schreiben Sie ein Programm, welches Vokabelpaare (ein Wort und dessen Übersetzung in eine andere Sprache) aus einer Datei liest. Im Anschluss wird dem Benutzer jeweils ein Element eines Paares ausgegeben und die richtige Übersetzung muss durch den Benutzer eingegeben werden. Zum Abschluss wird dem Benutzer angezeigt wie viele richtige Antworten gegeben wurden.

## Datentyp

Definieren Sie einen Datentyp für die Vokabelpaare. Die entsprechende Struktur soll zwei C-Strings (als Character-Pointer) als Elemente beinhalten. 

## Dateiformat

Die Vokabelpaare werden in einer Textdatei gespeichert, wobei jeweils pro Zeile ein Vokabelpaar gespeichert wird. Die beiden Elemente des Vokabelpaares werden durch mindestens ein Leerzeichen getrennt.

Einzelne Zeilen sind mit einem Zeilenumbruch (\n) abgeschlossen. Es dürfen zu Zeilenbeginn und Zeilenende beliebig viele Leerzeichen vorliegen.

Sollte eine Zeile nicht genau zwei Elemente enthalten ist die Vokabeldatei ungültig (siehe Fehlermeldungen).

## Programmablauf

Das Programm wird mit einem Kommandozeilenparameter aufgerufen. Dieser gibt den Dateinamen der zu öffnenden Vokabeldatei an. Sollte das Programm ohne Kommandozeilenparameter aufgerufen werden kommt es zu einer Fehlermeldung. Sollte das Programm mit mehr als einem Kommandozeilenparameter aufgerufen werden, so werden alle Parameter nach dem ersten ignoriert.

Im ersten Schritt liest das Programm die Vokabeldatei ein. Die Inhalte der Datei müssen hierbei am Heap gespeichert werden (siehe Spezifikation).

Im zweiten Schritt wird das erste Element des ersten Vokabelpaares gefolgt von der Zeichenfolge " - " ausgegeben und auf eine Benutzereingabe gewartet.

Die vom Benutzer eingegebene Zeichenkette wird mit dem zweiten Element des Vokabelpaares verglichen. Stimmen die beiden Zeichenketten überein wird "correct\n" ausgegeben, ansonsten "incorrect\n".

Anschließend wird mit dem nächsten Vokabelpaar fortgesetzt, wobei in diesem Fall das zweite Element ausgegeben wird und die Eingabe mit dem ersten Element verglichen wird.

Für jedes gerade Vokabelpaar (0., 2., 4., ...) wird das erste Element des Paares ausgegeben und die Eingabe mit dem zweiten Element verglichen. Für jedes ungerade Vokabelpaar (1., 3., 5., ...) wird das zweite Element des Paares ausgegeben und die Eingabe mit dem ersten verglichen.

Abschließend wird eine Statistik ausgegeben: "[correct] / [pairs]\n" wobei [correct] durch die anzahl der richtig beantworteten Vokabeln und [pairs] durch die Anzahl der Vokabelpaare ersetzt wird.
### Rückgabewerte und Fehlermeldungen

| Wert | Bedeutung   | Fehlermeldung   |
| :--: | ----------- | ----------- |
| 0    | Erfolgsfall | |
| 1  | keine Kommandozeilenparameter   | usage: [executable] filename |
| 2   | Vokabeldatei kann nicht geöffnet werden   | ERROR: cannot open file [filename] |
| 3   | Vokabeldatei ungültig | ERROR: file [filename] invalid |
| 4   | kein Speicher kann mehr angefordert werden | ERROR: Out of Memory |

[executable] wird durch den Namen des kompiliertenProgramms ersetzt.

[filename] wird durch den Namen der Vokabeldatei ersetzt.

## Spezifikation

* keine zusätzlichen Ausgaben
* alle Ausgaben erfolgen auf stdout
  * keinerlei Ausgaben auf stderr 
* Abgabe beinhaltet keine Binärdateien
* Dateiinhalt muss am Heap gespeichert werden
  * Vokabelpaare werden in der definierten Datenstruktur am Heap gespeichert
  * Pointer auf die Datenstrukturen werden in einem dynamisch wachsenden Array gespeichert
    * Das Array soll anfangs 10 Elemente groß sein. Wann immer notwendig soll es um 10 Elemente vergrößert werden. (10->20->30->...)

## Abgabe

* Abgabe auf Progpipe mittels git
  * tag mit der Bezeichnung "submission"
* Deadline: 17.11.2019 23:59

## Verantwortlicher Tutor
* Florian Hager