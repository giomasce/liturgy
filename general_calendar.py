#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from constants import *
from movable_dates import get_pentecost, get_saint_family
from utils import int_to_roman

WEEKDAYS_ITALIAN = {
    WD_MONDAY: u'lunedì',
    WD_TUESDAY: u'martedì',
    WD_WEDNESDAY: u'mercoledì',
    WD_THURSDAY: u'giovedì',
    WD_FRIDAY: u'venerdì',
    WD_SATURDAY: u'sabato',
    WD_SUNDAY: u'domenica',
}

SEASONS_ITALIAN = {
    SEASON_ADVENT: u'tempo di avvento',
    SEASON_CHRISTMAS: u'tempo di Natale',
    SEASON_ORDINARY_I: u'tempo ordinario',
    SEASON_LENT: u'tempo di quaresima',
    SEASON_EASTER: u'tempo di Pasqua',
    SEASON_ORDINARY_II: 'tempo ordinario',
}

BASE_TITLE_ITALIAN = u'%s della %s settimana del %s'

GENERAL_CALENDAR_LIST = [
    (1, 1, u"Maria SS. Madre di Dio", TYPE_SOLEMNITY),
    (1, 2, u"Ss. Basilio Magno e Gregorio Nazianzeno, vescovi e dottori della Chiesa", TYPE_MEMORY),
    (1, 3, u"SS. Nome di Gesù", TYPE_OPTIONAL_MEMORY),
    #(1, 6, u"Epifania del Signore", TYPE_SOLEMNITY),
    (1, 7, u"S. Raimondo da Peñafort", TYPE_OPTIONAL_MEMORY),
    (1, 13, u"S. Ilario, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (1, 17, u"S. Antonio, abate", TYPE_MEMORY),
    (1, 20, u"S. Fabiano, papa e martire", TYPE_OPTIONAL_MEMORY),
    (1, 20, u"S. Sebastiano, martire", TYPE_OPTIONAL_MEMORY),
    (1, 21, u"S. Agnese, vergine e martire", TYPE_MEMORY),
    (1, 22, u"S. Vincenzo, diacono e martire", TYPE_OPTIONAL_MEMORY),
    (1, 24, u"S. Francesco di Sales, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (1, 25, u"Conversione di S. Paolo, apostolo", TYPE_FEAST),
    (1, 26, u"Ss. Timòteo e Tito, vescovi", TYPE_MEMORY),
    (1, 27, u"S. Angela Merici, vergine", TYPE_OPTIONAL_MEMORY),
    (1, 28, u"S. Tommaso d'Aquino, sacerdote e dottore della Chiesa", TYPE_MEMORY),
    (1, 31, u"S. Giovanni Bosco, sacerdote", TYPE_MEMORY),

    (2, 2, u"Presentazione del Signore", TYPE_LORD_FEAST),
    (2, 3, u"S. Biagio, vescovo e martire", TYPE_OPTIONAL_MEMORY),
    (2, 3, u"S. Ansgario (Oscar), vescovo", TYPE_OPTIONAL_MEMORY),
    (2, 5, u"S. Agata, vergine e martire", TYPE_MEMORY),
    (2, 6, u"Ss. Paolo Miki e compagni, martiri", TYPE_MEMORY),
    (2, 8, u"S. Girolamo Emiliani", TYPE_OPTIONAL_MEMORY),
    (2, 8, u"S. Giuseppina Bakhita, vergine", TYPE_OPTIONAL_MEMORY),
    (2, 10, u"S. Scolastica, vergine", TYPE_MEMORY),
    (2, 11, u"Beata Vergine Maria di Lourdes", TYPE_OPTIONAL_MEMORY),
    (2, 14, u"Ss. Cirillo, monaco, e Metodio, vescovo, patroni d'Europa", TYPE_FEAST),
    (2, 17, u"Ss. Sette Fondatori dell'Ordine dei Servi della beata Vergine Maria", TYPE_OPTIONAL_MEMORY),
    (2, 21, u"S. Pier Damiani, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (2, 22, u"Cattedra di S. Pietro, apostolo", TYPE_FEAST),
    (2, 23, u"S. Policarpo, vescovo e martire", TYPE_MEMORY),

    (3, 4, u"S. Casimiro", TYPE_OPTIONAL_MEMORY),
    (3, 7, u"Ss. Perpetua e Felicita, martiri", TYPE_MEMORY),
    (3, 8, u"S. Giovanni di Dio, religioso", TYPE_OPTIONAL_MEMORY),
    (3, 9, u"S. Francesca Romana, religiosa", TYPE_OPTIONAL_MEMORY),
    (3, 17, u"S. Patrizio, vescovo", TYPE_OPTIONAL_MEMORY),
    (3, 18, u"S. Cirillo di Gerusalemme, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (3, 19, u"S. Giuseppe, sposo della beata Vergine Maria", TYPE_SOLEMNITY),
    (3, 23, u"S. Turibio de Mogrovejo, vescovo", TYPE_OPTIONAL_MEMORY),
    (3, 25, u"Annunciazione del Signore", TYPE_SOLEMNITY),

    (4, 2, u"S. Francesco de Paola, eremita", TYPE_OPTIONAL_MEMORY),
    (4, 4, u"S. Isidoro, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (4, 5, u"S. Vincenzo Ferrer, sacerdote", TYPE_OPTIONAL_MEMORY),
    (4, 7, u"S. Giovanni Battista de la Salle, sacerdote", TYPE_MEMORY),
    (4, 11, u"S. Stanislao, vescovo e martire", TYPE_MEMORY),
    (4, 13, u"S. Martino I, papa e martire", TYPE_OPTIONAL_MEMORY),
    (4, 21, u"S. Anselmo, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (4, 23, u"S. Adalberto, vescovo e martire", TYPE_OPTIONAL_MEMORY),
    (4, 23, u"S. Giorgio, martire", TYPE_OPTIONAL_MEMORY),
    (4, 24, u"S. Fedele da Sigmaringen, sacerdote e martire", TYPE_OPTIONAL_MEMORY),
    (4, 25, u"S. Marco, evangelista", TYPE_FEAST),
    (4, 28, u"S. Luigi Maria Grignion da Montfort, sacerdote", TYPE_OPTIONAL_MEMORY),
    (4, 28, u"S. Pietro Chanel, sacerdote e martire", TYPE_OPTIONAL_MEMORY),
    (4, 29, u"S. Caterina da Siena, vergine e dottore della Chiesa, patrona d'Italia e d'Europa", TYPE_FEAST),
    (4, 30, u"S. Pio V, papa", TYPE_OPTIONAL_MEMORY),

    (5, 1, u"S. Giuseppe Lavoratore", TYPE_OPTIONAL_MEMORY),
    (5, 2, u"S. Atanasio, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (5, 3, u"Ss. Filippo e Giacomo, apostoli", TYPE_FEAST),
    (5, 12, u"Ss. Nereo e Achilleo, martiri", TYPE_OPTIONAL_MEMORY),
    (5, 12, u"S. Pancrazio, martire", TYPE_OPTIONAL_MEMORY),
    (5, 13, u"Beata Vergine Maria di Fatima", TYPE_OPTIONAL_MEMORY),
    (5, 14, u"S. Mattia, apostolo", TYPE_FEAST),
    (5, 18, u"S. Giovanni I, papa e martire", TYPE_OPTIONAL_MEMORY),
    (5, 20, u"S. Bernardino da Siena, sacerdote", TYPE_OPTIONAL_MEMORY),
    (5, 21, u"Ss. Cristoforo Magellanes, sacerdote, e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (5, 22, u"S. Rita da Cascia, religiosa", TYPE_OPTIONAL_MEMORY),
    (5, 25, u"S. Beda Venerabile, sacerdote e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (5, 25, u"S. Gregorio VII, papa", TYPE_OPTIONAL_MEMORY),
    (5, 25, u"S. Maria Maddalena de' Pazzi, vergine", TYPE_OPTIONAL_MEMORY),
    (5, 26, u"S. Filippo Neri, sacerdoti", TYPE_MEMORY),
    (5, 27, u"S. Agostino di Canterbury, vescovo", TYPE_OPTIONAL_MEMORY),
    (5, 31, u"Visitazione della Beata Vergine Maria", TYPE_FEAST),

    (6, 1, u"S. Giustino, martire", TYPE_MEMORY),
    (6, 2, u"Ss. Marcellino e Pietro, martiri", TYPE_OPTIONAL_MEMORY),
    (6, 3, u"S. Carlo Lwanga e compagni, martiri", TYPE_MEMORY),
    (6, 5, u"S. Bonifacio, vescovo e martire", TYPE_MEMORY),
    (6, 6, u"S. Norberto, vescovo", TYPE_OPTIONAL_MEMORY),
    (6, 9, u"S. Efrem, diacono e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (6, 11, u"S. Barnaba, apostolo", TYPE_MEMORY),
    (6, 13, u"S. Antonio da Padova, sacerdote e dottore della Chiesa", TYPE_MEMORY),
    (6, 19, u"S. Romualdo, abate", TYPE_OPTIONAL_MEMORY),
    (6, 21, u"S. Luigi Gonzaga, religioso", TYPE_MEMORY),
    (6, 22, u"S. Paolino da Nola, vescovo", TYPE_OPTIONAL_MEMORY),
    (6, 22, u"Ss. Giovanni Fisher, vescovo, e Tommaso More, martiri", TYPE_OPTIONAL_MEMORY),
    (6, 24, u"Natività di S. Giovanni Battista", TYPE_SOLEMNITY),
    (6, 27, u"S. Cirillo d'Alessandria, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (6, 28, u"S. Ireneo, vescovo e martire", TYPE_MEMORY),
    (6, 29, u"Ss. Pietro e Paolo, apostoli", TYPE_SOLEMNITY),
    (6, 30, u"Ss. Primi martiri della Chiesa di Roma", TYPE_OPTIONAL_MEMORY),

    (7, 3, u"S. Tommaso, apostolo", TYPE_FEAST),
    (7, 4, u"S. Elisabetta di Portogallo", TYPE_OPTIONAL_MEMORY),
    (7, 5, u"S. Antonio Maria Zaccaria, sacerdote", TYPE_OPTIONAL_MEMORY),
    (7, 6, u"S. Maria Goretti, vergine e martire", TYPE_OPTIONAL_MEMORY),
    (7, 9, u"Ss. Agostino Zhao Rong, sacerdote, e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (7, 11, u"S. Benedetto, abate, patrono d'Europa", TYPE_FEAST),
    (7, 13, u"S. Enrico", TYPE_OPTIONAL_MEMORY),
    (7, 14, u"S. Camillo de Lellis, sacerdote", TYPE_OPTIONAL_MEMORY),
    (7, 15, u"S. Bonaventura, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (7, 16, u"Beata Vergine Maria del Monte Carmelo", TYPE_OPTIONAL_MEMORY),
    (7, 20, u"S. Apollinare, vescovo e martire", TYPE_OPTIONAL_MEMORY),
    (7, 21, u"S. Lorenzo da Brindisi, sacerdote e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (7, 22, u"S. Maria Maddalena", TYPE_MEMORY),
    (7, 23, u"S. Brigida, religiosa", TYPE_FEAST),
    (7, 24, u"S. Charbel Makhluf, sacerdote", TYPE_OPTIONAL_MEMORY),
    (7, 25, u"S. Giacomo, apostolo", TYPE_FEAST),
    (7, 26, u"S. Gioacchino e Anna, genitori della Beata Vergine Maria", TYPE_MEMORY),
    (7, 29, u"S. Marta", TYPE_MEMORY),
    (7, 30, u"S. Pietro Crisologo, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (7, 31, u"S. Ignazio di Loyola, sacerdote", TYPE_MEMORY),

    (8, 1, u"S. Alfonso Maria de' Liguori, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (8, 2, u"S. Eusebio di Vercelli, vescovo", TYPE_OPTIONAL_MEMORY),
    (8, 2, u"S. Pier Giuliano Eymard, sacerdote", TYPE_OPTIONAL_MEMORY),
    (8, 4, u"S. Giovanni Maria Vianney, sacertode", TYPE_MEMORY),
    (8, 5, u"Dedicazione della Basilica di S. Maria Maggiore", TYPE_OPTIONAL_MEMORY),
    (8, 6, u"Trasfigurazione del Signore", TYPE_LORD_FEAST),
    (8, 7, u"Ss. Sisto II, papa, e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (8, 7, u"S. Gaetano, sacerdote", TYPE_OPTIONAL_MEMORY),
    (8, 8, u"S. Domenico, sacerdote", TYPE_MEMORY),
    (8, 9, u"S. Teresa Benedetta della Croce, vergine e martire, patrona d'Europa", TYPE_FEAST),
    (8, 10, u"S. Lorenzo, diacono e martire", TYPE_FEAST),
    (8, 11, u"S. Chiara, vergine", TYPE_MEMORY),
    (8, 12, u"S. Giovanna Francesca de Chantal, religiosa", TYPE_OPTIONAL_MEMORY),
    (8, 13, u"Ss. Ponziano, papa, e Ippolito, sacerdote, martiri", TYPE_OPTIONAL_MEMORY),
    (8, 14, u"S. Massimiliano Maria Kolbe, sacerdote e martire", TYPE_MEMORY),
    (8, 15, u"Assunzione della beata Vergine Maria", TYPE_SOLEMNITY),
    (8, 16, u"S. Stefano di Ungheria", TYPE_OPTIONAL_MEMORY),
    (8, 19, u"S. Giovanni Eudes, sacerdote", TYPE_OPTIONAL_MEMORY),
    (8, 20, u"S. Bernardo, abate e dottore della Chiesa", TYPE_MEMORY),
    (8, 21, u"S. Pio X, papa", TYPE_MEMORY),
    (8, 22, u"Beata Vergine Maria Regina", TYPE_MEMORY),
    (8, 23, u"S. Rosa da Lima, vergine", TYPE_OPTIONAL_MEMORY),
    (8, 24, u"S. Bartolomeo, apostolo", TYPE_FEAST),
    (8, 25, u"S. Ludovico", TYPE_OPTIONAL_MEMORY),
    (8, 25, u"S. Giuseppe Calasanzio, sacerdote", TYPE_OPTIONAL_MEMORY),
    (8, 27, u"S. Monica", TYPE_MEMORY),
    (8, 28, u"S. Agostino, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (8, 29, u"Martirio di S. Giovanni Battista", TYPE_MEMORY),

    (9, 3, u"S. Gregorio Magno, papa e dottore della Chiesa", TYPE_MEMORY),
    (9, 8, u"Natività della beata Vergine Maria", TYPE_FEAST),
    (9, 9, u"S. Pietro Claver, sacerdote", TYPE_OPTIONAL_MEMORY),
    (9, 12, u"SS. Nome di Maria", TYPE_OPTIONAL_MEMORY),
    (9, 13, u"S. Giovanni Crisostomo, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (9, 14, u"Esaltazione della Santa Croce", TYPE_LORD_FEAST),
    (9, 15, u"Beata Vergine Maria Addolorata", TYPE_MEMORY),
    (9, 16, u"Ss. Cornelio, papa, e Cipriano, vescovo, martiri", TYPE_MEMORY),
    (9, 17, u"S. Roberto Bellarmino, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (9, 19, u"S. Gennaro, vescovo e martire", TYPE_OPTIONAL_MEMORY),
    (9, 20, u"Ss. Andrea Kim Taegon, sacerdote, Paolo Chong Hasang e compagni, martiri", TYPE_MEMORY),
    (9, 21, u"S. Matteo, apostolo ed evangelista", TYPE_FEAST),
    (9, 23, u"S. Pio da Pietralcina, sacerdote", TYPE_MEMORY),
    (9, 26, u"Ss. Cosma e Damiano, martiri", TYPE_OPTIONAL_MEMORY),
    (9, 27, u"S. Vincenzo de' Paoli, sacerdote", TYPE_MEMORY),
    (9, 28, u"S. Venceslao, martire", TYPE_OPTIONAL_MEMORY),
    (9, 28, u"S. Lorenzo Ruiz e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (9, 29, u"Ss. Michele, Gabriele e Raffaele, arcangeli", TYPE_FEAST),
    (9, 30, u"S. Girolamo, sacerdote e dottore della Chiesa", TYPE_MEMORY),

    (10, 1, u"S. Teresa di Gesù Bambino, vergine e dottore della Chiesa", TYPE_MEMORY),
    (10, 2, u"Ss. Angeli Custodi", TYPE_MEMORY),
    (10, 4, u"S. Francesco d'Assisi, patrono d'Italia", TYPE_FEAST),
    (10, 6, u"S. Bruno, monato", TYPE_OPTIONAL_MEMORY),
    (10, 7, u"Beata Vergine Maria del Rosario", TYPE_MEMORY),
    (10, 9, u"Ss. Dionigi, vescovo, e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (10, 9, u"S. Giovanni Leonardi, sacerdote", TYPE_OPTIONAL_MEMORY),
    (10, 14, u"S. Callisto I, papa e martire", TYPE_OPTIONAL_MEMORY),
    (10, 15, u"S. Teresa d'Avila, vergine e dottore della Chiesa", TYPE_MEMORY),
    (10, 16, u"S. Edvige, religiosa", TYPE_OPTIONAL_MEMORY),
    (10, 16, u"S. Margherita Maria Alacoque, vergine", TYPE_OPTIONAL_MEMORY),
    (10, 17, u"S. Ignazio di Antiochia, vescovo e martire", TYPE_MEMORY),
    (10, 18, u"S. Luca, evangelista", TYPE_FEAST),
    (10, 19, u"Ss. Giovanni de Brébeuf e Isacco Jogues, sacerdoti, e compagni, martiri", TYPE_OPTIONAL_MEMORY),
    (10, 19, u"S. Paolo della Croce, sacerdote", TYPE_OPTIONAL_MEMORY),
    (10, 23, u"S. Giovanni da Capestrano, sacerdote", TYPE_OPTIONAL_MEMORY),
    (10, 24, u"S. Antonio Maria Claret, vescovo", TYPE_OPTIONAL_MEMORY),
    (10, 28, u"Ss. Simone e Giuda, apostoli", TYPE_FEAST),

    (11, 1, u"Tutti i santi", TYPE_SOLEMNITY),
    # Techincally "commemorazione" is not a solemnity, but it is
    # granted the same priority level
    #(11, 2, u"Commemoriazione di tutti i fedeli defunti", TYPE_SOLEMNITY),
    (11, 3, u"S. Martino de Porres, religioso", TYPE_OPTIONAL_MEMORY),
    (11, 4, u"S. Carlo Borromeo, vescovo", TYPE_MEMORY),
    (11, 9, u"Dedicazione della Basilica Lateranense", TYPE_FEAST),
    (11, 10, u"S. Leone Magno, papa e dottore della Chiesa", TYPE_MEMORY),
    (11, 11, u"S. Martino di Tours, vescovo", TYPE_MEMORY),
    (11, 12, u"S. Giosafat, vescovo e martire", TYPE_MEMORY),
    (11, 15, u"S. Alberto Magno, vescovo e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (11, 16, u"S. Margherita di Scozia", TYPE_OPTIONAL_MEMORY),
    (11, 16, u"S. Geltrude, vergine", TYPE_OPTIONAL_MEMORY),
    (11, 17, u"S. Elisabetta di Ungheria, religiosa", TYPE_MEMORY),
    (11, 18, u"Dedicazione delle Basiliche dei Ss. Pietro e Paolo, apostoli", TYPE_OPTIONAL_MEMORY),
    (11, 21, u"Presentazione della beata Vergine Maria", TYPE_MEMORY),
    (11, 22, u"S. Cecilia, vergine e martire", TYPE_MEMORY),
    (11, 23, u"S. Clemente I, papa e martire", TYPE_OPTIONAL_MEMORY),
    (11, 23, u"S. Colombano, abate", TYPE_OPTIONAL_MEMORY),
    (11, 24, u"Ss. Andrea Dung-Lac, sacerdote, e compagni, martiri", TYPE_MEMORY),
    (11, 25, u"S. Caterina di Alessandria, vergine e martire", TYPE_OPTIONAL_MEMORY),
    (11, 30, u"S. Andrea, apostolo", TYPE_FEAST),

    (12, 3, u"S. Francesco Saverio, sacerdote", TYPE_MEMORY),
    (12, 4, u"S. Giovanni Damasceno, sacerdote e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (12, 6, u"S. Nicola, vescovo", TYPE_OPTIONAL_MEMORY),
    (12, 7, u"S. Ambrogio, vescovo e dottore della Chiesa", TYPE_MEMORY),
    (12, 8, u"Immacolata Concezione della beata Vergine Maria", TYPE_SOLEMNITY),
    (12, 9, u"S. Giovanni Diego Cuauhtlatoatzin", TYPE_OPTIONAL_MEMORY),
    (12, 11, u"S. Damaso I, papa", TYPE_OPTIONAL_MEMORY),
    (12, 12, u"Beata Vergine Maria di Guadalupe", TYPE_OPTIONAL_MEMORY),
    (12, 13, u"S. Lucia, vergine e martire", TYPE_MEMORY),
    (12, 14, u"S. Giovanni della Croce, sacerdote e dottore della Chiesa", TYPE_MEMORY),
    (12, 21, u"S. Pietro Canisio, sacerdote e dottore della Chiesa", TYPE_OPTIONAL_MEMORY),
    (12, 23, u"S. Giovanni da Kety", TYPE_OPTIONAL_MEMORY),
    #(12, 25, u"Natale del Signore", TYPE_SOLEMNITY),
    (12, 26, u"S. Stefano, primo martire", TYPE_FEAST),
    (12, 27, u"S. Giovanni, apostolo ed evangelista", TYPE_FEAST),
    (12, 28, u"Ss. Innocenti, martiri", TYPE_FEAST),
    (12, 29, u"S. Tommaso Becket, vescovo e martire", TYPE_OPTIONAL_MEMORY),
    (12, 31, u"S. Silvestro I, papa", TYPE_OPTIONAL_MEMORY),
]

# Bad, but temporary
MOVABLE_CALENDAR_STR = {
    u"saint_family": [(u"Santa Famiglia di Gesù, Maria e Giuseppe", TYPE_LORD_FEAST)],
    u"pentecost + datetime.timedelta(days=7)": [(u"SS. Trinità", TYPE_SOLEMNITY)],
    u"pentecost + datetime.timedelta(days=14)": [(u"SS. Corpo e Sangue di Cristo", TYPE_SOLEMNITY)],
    u"pentecost + datetime.timedelta(days=19)": [(u"Sacratissimo Cuore di Gesù", TYPE_SOLEMNITY)],
    u"pentecost + datetime.timedelta(days=20)": [(u"Cuore Immacolato della beata Vergine Maria", TYPE_MEMORY)],
    }

def populate_base_competitors(session):
    import database

    # Advent
    pairs = []
    for week in [1, 2]:
        for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                        WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
            pairs.append((week, weekday))
    week = 3
    for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                    WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
        pairs.append((week, weekday))
    pairs.append((4, WD_SUNDAY))
    for week, weekday in pairs:
        title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[weekday],
                                      int_to_roman(week),
                                      SEASONS_ITALIAN[SEASON_ADVENT])
        te = database.TimedEvent()
        te.status = u'incomplete'
        te.week = week
        te.weekday = weekday
        te.season = SEASON_ADVENT
        te.title = title
        te.priority = PRI_CHRISTMAS if weekday == WD_SUNDAY else PRI_WEEKDAYS
        session.add(te)

    for day in xrange(17, 25):
        fe = database.FixedEvent()
        fe.status = u'incomplete'
        fe.day = day
        fe.month = 12
        fe.title = u'%d dicembre' % (day)
        fe.priority = PRI_STRONG_WEEKDAYS
        session.add(fe)

    # Christmas
    fe = database.FixedEvent()
    fe.status = u'incomplete'
    fe.day = 25
    fe.month = 12
    fe.title = u'Natale del Signore'
    fe.priority = PRI_CHRISTMAS
    session.add(fe)

    # Octave after Christmas
    for day in xrange(29, 32):
        fe = database.FixedEvent()
        fe.status = u'incomplete'
        fe.day = day
        fe.month = 12
        fe.title = u'%d dicembre' % (day)
        fe.priority = PRI_STRONG_WEEKDAYS
        session.add(fe)

    # Sunday after Christmas
    te = database.TimedEvent()
    te.status = u'incomplete'
    te.week = 2
    te.weekday = WD_SUNDAY
    te.season = SEASON_CHRISTMAS
    te.title = u'seconda domenica dopo Natale'
    te.priority = PRI_SUNDAYS
    session.add(te)

    # Weekdays in January
    for day in range(2, 6) + range(7, 13):
        fe = database.FixedEvent()
        fe.status = u'incomplete'
        fe.day = day
        fe.month = 1
        fe.season = SEASON_CHRISTMAS
        fe.title = u'%d gennaio' % (day)
        fe.priority = PRI_WEEKDAYS
        session.add(fe)

    # Epiphany
    fe = database.FixedEvent()
    fe.status = u'incomplete'
    fe.day = 6
    fe.month = 1
    fe.title = u'Epifania del Signore'
    fe.priority = PRI_CHRISTMAS
    session.add(fe)

    # Baptism
    me = database.MovableEvent()
    me.status = u'incomplete'
    me.calc_func = 'baptism'
    me.priority = PRI_SUNDAYS
    me.title = u'Battesimo del Signore'
    session.add(me)

    # Ordinary time
    for week in xrange(1, 35):
        for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                        WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
            if (week, weekday) == (1, WD_SUNDAY):
                continue
            title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[weekday],
                                          int_to_roman(week),
                                          SEASONS_ITALIAN[SEASON_ORDINARY])
            if (week, weekday) == (34, WD_SUNDAY):
                title = u"Nostro Signore Gesù Cristo Re dell'Universo"
            te = database.TimedEvent()
            te.status = u'incomplete'
            te.week = week
            te.weekday = weekday
            te.season = SEASON_ORDINARY
            te.title = title
            te.priority = PRI_SUNDAYS if weekday == WD_SUNDAY else PRI_WEEKDAYS
            session.add(te)

    # Ash day and following ones
    for weekday in [WD_WEDNESDAY, WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
        te = database.TimedEvent()
        te.status = u'incomplete'
        te.season = SEASON_LENT
        te.week = 0
        te.weekday = weekday
        te.priority = PRI_CHRISTMAS if weekday == WD_WEDNESDAY else PRI_STRONG_WEEKDAYS
        te.title = u'Mercoledì delle Ceneri' if weekday == WD_WEDNESDAY else u'%s dopo le Ceneri' % (WEEKDAYS_ITALIAN[weekday])
        session.add(te)

    # Lent
    for week in xrange(1, 6):
        for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                        WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
            title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[weekday],
                                          int_to_roman(week),
                                          SEASONS_ITALIAN[SEASON_LENT])
            te = database.TimedEvent()
            te.status = u'incomplete'
            te.week = week
            te.weekday = weekday
            te.season = SEASON_LENT
            te.title = title
            te.priority = PRI_CHRISTMAS if weekday == WD_SUNDAY else PRI_STRONG_WEEKDAYS
            session.add(te)

    # Holy week
    for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                    WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
        title = u'Domenica delle Palme' if weekday == WD_SUNDAY else u'%s Santo' % (WEEKDAYS_ITALIAN[weekday].capitalize())
        te = database.TimedEvent()
        te.status = u'incomplete'
        te.week = 6
        te.weekday = weekday
        te.season = SEASON_LENT
        te.title = title
        te.priority = PRI_TRIDUUM if weekday in [WD_THURSDAY, WD_FRIDAY, WD_SATURDAY] else PRI_CHRISTMAS
        session.add(te)

    # Easter
    for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                    WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
        title = u'Pasqua di Resurrezione' if weekday == WD_SUNDAY else u"%s fra l'ottava di Pasqua" % (WEEKDAYS_ITALIAN[weekday])
        te = database.TimedEvent()
        te.status = u'incomplete'
        te.week = 1
        te.weekday = weekday
        te.season = SEASON_EASTER
        te.title = title
        te.priority = PRI_TRIDUUM if weekday == WD_SUNDAY else PRI_CHRISTMAS
        session.add(te)

    # Easter time
    for week in xrange(2, 8):
        for weekday in [WD_SUNDAY, WD_MONDAY, WD_TUESDAY, WD_WEDNESDAY,
                        WD_THURSDAY, WD_FRIDAY, WD_SATURDAY]:
            title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[weekday],
                                          int_to_roman(week),
                                          SEASONS_ITALIAN[SEASON_EASTER])
            if (week, weekday) == (7, WD_SUNDAY):
                title = u'Ascensione del Signore'
            te = database.TimedEvent()
            te.status = u'incomplete'
            te.week = week
            te.weekday = weekday
            te.season = SEASON_EASTER
            te.title = title
            te.priority = PRI_CHRISTMAS if weekday == WD_SUNDAY else PRI_WEEKDAYS
            session.add(te)

    # Pentecost
    te = database.TimedEvent()
    te.status = u'incomplete'
    te.week = 8
    te.weekday = WD_SUNDAY
    te.season = SEASON_EASTER
    te.title = u'Domenica di Pentecoste'
    te.priority = PRI_CHRISTMAS
    session.add(te)

def populate_database():
    import database
    database.Base.metadata.create_all()
    session = database.Session()

    for month, day, title, type_ in GENERAL_CALENDAR_LIST:
        fe = database.FixedEvent()
        fe.status = u'incomplete'
        fe.day = day
        fe.month = month
        fe.type = type_
        fe.title = title
        session.add(fe)

    for calc_func, data in MOVABLE_CALENDAR_STR.iteritems():
        me = database.MovableEvent()
        me.status = u'incomplete'
        me.type = data[0][1]
        me.title = data[0][0]
        me.calc_func = calc_func
        session.add(me)

    populate_base_competitors(session)

    # An exception
    fe = database.FixedEvent()
    fe.status = u'incomplete'
    fe.day = 2
    fe.month = 11
    fe.priority = PRI_SOLEMNITIES
    fe.title = u'Commemorazione di tutti i fedeli defunti'
    session.add(fe)

    session.commit()

if __name__ == '__main__':
    populate_database()
