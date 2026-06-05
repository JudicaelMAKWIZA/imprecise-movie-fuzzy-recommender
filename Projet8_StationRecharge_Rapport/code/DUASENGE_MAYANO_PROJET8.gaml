/**
 * Name: ProjetSMA8_StationRecharge
 * Author: Duasenge Mayano
 * Tags: SMA, GAMA, station, vehicule electrique, file d'attente
 * Hypothèse: monde fermé — tout ce qui n'est pas déclaré est faux/inexistant.
 */

model ProjetSMA8_StationRecharge

global {
	/* ======================================================================
	   CONSTANTES DE TYPOLOGIE DE BORNES
	   ====================================================================== */
	string TYPE_LENTE <- "lente";
	string TYPE_ACC <- "acceleree";
	string TYPE_RAPIDE <- "rapide";
	
	/* ======================================================================
	   CONSTANTES D'ÉTATS DES BORNES
	   ====================================================================== */
	string ETAT_LIBRE <- "libre";
	string ETAT_OCCUPEE <- "occupee";
	string ETAT_PANNE <- "panne";
	string ETAT_MAINT <- "maintenance";
	
	/* ======================================================================
	   CONSTANTES D'ÉTATS DES VÉHICULES
	   ====================================================================== */
	string STATE_ARRIVING <- "arriving";
	string STATE_WAITING <- "waiting";
	string STATE_CHARGING <- "charging";
	string STATE_SERVED <- "served";
	string STATE_ABANDONED <- "abandoned";
	
	/* ======================================================================
	   CONSTANTES DE POLITIQUE DE FILE D'ATTENTE
	   ====================================================================== */
	string POL_FIFO <- "fifo";
	string POL_LOWBAT <- "lowbat";
	string POL_URGENCE <- "urgence";
	string POL_PREF <- "pref";
	
	/* ======================================================================
	   PUISSANCES DES BORNES (en kW) - PARAMÉTRABLES
	   ====================================================================== */
	float puissance_lente <- 7.0;
	float puissance_acc <- 22.0;
	float puissance_rapide <- 50.0;
	
	/* ======================================================================
	   NOMBRE DE BORNES PAR TYPE
	   ====================================================================== */
	int nb_bornes_lentes <- 10;
	int nb_bornes_acc <- 8;
	int nb_bornes_rapides <- 5;
	
	/* ======================================================================
	   CAPACITÉ ET GÉOMÉTRIE DE LA STATION
	   ====================================================================== */
	geometry shape <- square(100);
	float capacite_kwh_default <- 85.0;  // Capacité moyenne des véhicules (kWh)
	
	/* ======================================================================
	   PROBABILITÉS STOCHASTIQUES
	   ====================================================================== */
	float p_panne_par_pas <- 0.0005;     // Probabilité de panne à chaque pas
	float p_fin_panne <- 0.01;           // Probabilité de fin de panne
	float p_burst <- 0.02;               // Probabilité d'arrivée groupée
	int taille_burst <- 4;               // Nombre de véhicules en cas de burst
	
	/* ======================================================================
	   PARAMÈTRES RÉSEAU
	   ====================================================================== */
	float puissance_reseau_factor <- 1.0;  // Entre 0.5 et 1.0
	
	/* ======================================================================
	   POLITIQUE ACTIVE ET AFFICHAGE
	   ====================================================================== */
	string politique_file <- POL_FIFO;
	bool affichage_temps_attente <- true;  // Affichage par défaut activé
	bool file_unique <- true;              // Unique file vs files par type
	
	/* ======================================================================
	   PARAMÈTRES TEMPORELS
	   ====================================================================== */
	float step <- 1 #mn;
	float heure_simulee update: (cycle * step / #h) mod 24.0;
	
	/* ======================================================================
	   PARAMÈTRES D'ARRIVÉE DES VÉHICULES (Poisson non-homogène)
	   ====================================================================== */
	float taux_base <- 0.5;      // Taux moyen (véhicules/heure)
	float amplitude <- 1.5;      // Ampleur des variations diurnes
	float sigma <- 3.0;          // Largeur de la distribution (heures)
	
	/* ======================================================================
	   COMPTEURS KPI - INITIALISÉS À 0 (MONDE FERMÉ)
	   ====================================================================== */
	int total_arrivees <- 0;
	int total_servis <- 0;
	int total_abandons <- 0;
	
	float somme_temps_attente <- 0.0;
	int nb_temps_attente <- 0;
	
	float somme_satisfaction <- 0.0;
	int nb_satisfaction <- 0;
	
	float taux_occupation_courant <- 0.0;
	float taille_file_courante <- 0.0;
	
	// Accumulation pour calcul de moyennes temporelles (Comment 7, 8)
	float somme_taux_occupation <- 0.0;
	int nb_obs_occupation <- 0;
	float somme_taille_file <- 0.0;
	int nb_obs_file <- 0;
	
	/* ======================================================================
	   VARIABLES DÉRIVÉES (mise à jour automatique via update:)
	   ====================================================================== */
	float taux_occupation_moyen update: 
		nb_obs_occupation > 0 ? (somme_taux_occupation / nb_obs_occupation) : 0.0;
	
	float temps_attente_moyen update: 
		nb_temps_attente > 0 ? (somme_temps_attente / nb_temps_attente) : 0.0;
	
	float taux_abandon update: 
		total_arrivees > 0 ? (float(total_abandons) / float(total_arrivees)) : 0.0;
	
	float taux_satisfaction update: 
		nb_satisfaction > 0 ? (somme_satisfaction / nb_satisfaction) : 0.0;
	
	float taille_file_moyenne update: 
		nb_obs_file > 0 ? (somme_taille_file / nb_obs_file) : 0.0;
	
	/* ======================================================================
	   INIT: CRÉATION DE LA STATION ET DES BORNES
	   ====================================================================== */
	init {
		// Créer 1 unique station
		create station number: 1 {
			location <- {50.0, 50.0};  // Centre du shape
		}
		
		// Créer les bornes lentes (Comment 3, 4: location et capture avec returns)
		create borne returns: created_lentes number: nb_bornes_lentes {
			type_borne <- TYPE_LENTE;
			puissance_kw <- puissance_lente;
			location <- {rnd(0, 30), rnd(0, 30)};
		}
		ask first(station) {
			add all: created_lentes to: bornes;
		}
		
		// Créer les bornes accélérées
		create borne returns: created_acc number: nb_bornes_acc {
			type_borne <- TYPE_ACC;
			puissance_kw <- puissance_acc;
			location <- {rnd(30, 60), rnd(30, 60)};
		}
		ask first(station) {
			add all: created_acc to: bornes;
		}
		
		// Créer les bornes rapides
		create borne returns: created_rapides number: nb_bornes_rapides {
			type_borne <- TYPE_RAPIDE;
			puissance_kw <- puissance_rapide;
			location <- {rnd(60, 100), rnd(60, 100)};
		}
		ask first(station) {
			add all: created_rapides to: bornes;
		}
	}
	
	/* ======================================================================
	   REFLEX GLOBAL: GÉNÉRATION D'ARRIVÉES (Poisson non-homogène)
	   ====================================================================== */
	reflex generer_arrivees {
		// Calcul du taux instantané : pic en soirée (19h)
		float taux_instant <- taux_base * (1.0 + amplitude * 
			exp(-((heure_simulee - 19.0) ^ 2.0) / (2.0 * sigma ^ 2.0)));
		
		// Tirage Poisson approximé pour 1 véhicule
		if (flip(min(1.0, taux_instant * step / #h))) {
			create vehicule number: 1 {
				etat_v <- STATE_ARRIVING;
				t_arrivee <- time;
			}
			total_arrivees <- total_arrivees + 1;
		}
		
		// Arrivée groupée (burst) : créer taille_burst véhicules supplémentaires
		if (flip(p_burst)) {
			create vehicule number: taille_burst {
				etat_v <- STATE_ARRIVING;
				t_arrivee <- time;
			}
			total_arrivees <- total_arrivees + taille_burst;
		}
	}
	
	/* ======================================================================
	   REFLEX GLOBAL: VARIATION DU FACTEUR RÉSEAU (toutes les 30 min)
	   ====================================================================== */
	reflex variation_reseau when: (cycle mod 30) = 0 {
		puissance_reseau_factor <- rnd(0.5, 1.0);
	}
	
	/* ======================================================================
	   REFLEX GLOBAL: ACCUMULATION DES KPI POUR MOYENNES TEMPORELLES
	   ====================================================================== */
	reflex maj_kpi {
		// Lecture des KPIs écrits par station.maj_kpi_station, accumulation pour les moyennes temporelles
		// (Comment 1, 7, 8: station est propriétaire unique de taux_occupation_courant et taille_file_courante)
		somme_taux_occupation <- somme_taux_occupation + taux_occupation_courant;
		nb_obs_occupation <- nb_obs_occupation + 1;
		
		somme_taille_file <- somme_taille_file + taille_file_courante;
		nb_obs_file <- nb_obs_file + 1;
	}
}

/* ======================================================================
   ESPÈCE: STATION (1 instance, centre logistique)
   ====================================================================== */
species station {
	/* ====================================================================
	   ATTRIBUTS EXPLICITES
	   ==================================================================== */
	list<borne> bornes <- [];
	list<vehicule> file_unique_list <- [];
	map<string, list<vehicule>> files_par_type <- 
		map([TYPE_LENTE::[], TYPE_ACC::[], TYPE_RAPIDE::[]]);
	int nb_servis_local <- 0;
	int nb_abandons_local <- 0;
	
	/* ====================================================================
	   ACTION: ENFILER UN VÉHICULE
	   ==================================================================== */
	action enfiler(vehicule v) {
		if (file_unique) {
			add v to: file_unique_list;
		} else {
			if (v.preference_puissance in files_par_type.keys) {
				add v to: files_par_type[v.preference_puissance];
			} else {
				add v to: files_par_type[TYPE_LENTE];  // Fallback
			}
		}
	}
	
	/* ====================================================================
	   ACTION: RETIRER UN VÉHICULE DE LA FILE
	   ==================================================================== */
	action retirer(vehicule v) {
		remove v from: file_unique_list;
		loop type over: files_par_type.keys {
			remove v from: files_par_type[type];
		}
	}
	
	/* ====================================================================
	   ACTION: REMETTRE EN FILE (après panne de borne)
	   ==================================================================== */
	action requeue(vehicule v) {
		// Retirer du lieu courant
		do retirer(v);
		
		// Remettre en tête de file
		if (file_unique) {
			add v at: 0 to: file_unique_list;
		} else {
			if (v.preference_puissance in files_par_type.keys) {
				add v at: 0 to: files_par_type[v.preference_puissance];
			} else {
				add v at: 0 to: files_par_type[TYPE_LENTE];
			}
		}
		
		// Réinitialiser l'état
		v.etat_v <- STATE_WAITING;
	}
	
	/* ====================================================================
	   ACTION: SÉLECTIONNER LE PROCHAIN VÉHICULE SELON LA POLITIQUE
	   ==================================================================== */
	vehicule selectionner_suivant(string type_libere) {
		list<vehicule> file_active <- [];
		
		// Récupérer la file appropriée
		if (file_unique) {
			file_active <- file_unique_list;
		} else {
			// Chercher d'abord dans la file du type libéré
			if (type_libere in files_par_type.keys and !empty(files_par_type[type_libere])) {
				file_active <- files_par_type[type_libere];
			} else {
				// Sinon, combiner toutes les files
				loop type over: files_par_type.keys {
					add all: files_par_type[type] to: file_active;
				}
			}
		}
		
		if (empty(file_active)) {
			return nil;
		}
		
		vehicule selection <- nil;
		
		// Appliquer la politique (Comment 1: switch...match au lieu de switch...case)
		switch (politique_file) {
			match POL_FIFO {
				selection <- first(file_active);
			}
			match POL_LOWBAT {
				vehicule v_lowbat <- file_active[0];
				loop v over: file_active {
					if (v.batterie < v_lowbat.batterie) {
						v_lowbat <- v;
					}
				}
				selection <- v_lowbat;
			}
			match POL_URGENCE {
				vehicule v_urgent <- file_active[0];
				loop v over: file_active {
					if (v.urgence > v_urgent.urgence) {
						v_urgent <- v;
					}
				}
				selection <- v_urgent;
			}
			match POL_PREF {
				// Chercher d'abord avec préférence
				list<vehicule> avec_pref <- file_active where (each.preference_puissance = type_libere);
				if (!empty(avec_pref)) {
					selection <- first(avec_pref);
				} else {
					selection <- first(file_active);
				}
			}
			default {
				selection <- first(file_active);
			}
		}
		
		return selection;
	}
	
	/* ====================================================================
	   REFLEX: ATTRIBUER LES BORNES LIBRES AUX VÉHICULES EN FILE
	   ==================================================================== */
	reflex attribuer_bornes_libres {
		// Parcourir les bornes libres
		list<borne> bornes_libres <- bornes where (each.etat = ETAT_LIBRE);
		
		loop b over: bornes_libres {
			// Sélectionner le prochain véhicule
			vehicule v <- selectionner_suivant(b.type_borne);
			
			if (v != nil) {
				// Retirer de la file
				do retirer(v);
				
				// Démarrer la recharge
				ask b {
					do demarrer_recharge(v);
				}
				
				v.etat_v <- STATE_CHARGING;
				v.borne_assignee <- b;
			}
		}
	}
	
	/* ====================================================================
	   ACTION: ESTIMER LE TEMPS D'ATTENTE
	   ==================================================================== */
	float estimer_attente(vehicule v) {
		// Calcul du nombre de bornes compatibles (Comment 9: fix copy-paste bug)
		int nb_bornes_compatibles <- file_unique ? 
			length(bornes where (each.etat = ETAT_LIBRE)) :
			length(bornes where (each.type_borne = v.preference_puissance and each.etat = ETAT_LIBRE));
		int nb_bornes_actives <- max(1, nb_bornes_compatibles + 1);
		
		// Taille de la file
		int taille_file <- 0;
		if (file_unique) {
			taille_file <- length(file_unique_list);
		} else {
			loop t over: files_par_type.keys {
				taille_file <- taille_file + length(files_par_type[t]);
			}
		}
		
		// Temps moyen de recharge estimé (simplifié)
		float temps_recharge_moyen <- 30.0 * #mn;  // 30 minutes en moyenne
		
		// Estimation : (taille_file / bornes_actives) × temps_moyen
		float estimation <- (float(taille_file) / float(nb_bornes_actives)) * temps_recharge_moyen;
		
		return estimation;
	}
	
	/* ====================================================================
	   REFLEX: MISE À JOUR DES KPI DE LA STATION
	   ==================================================================== */
	reflex maj_kpi_station {
		// Taux d'occupation
		int nb_bornes_total <- length(bornes);
		int nb_bornes_occupees <- length(bornes where (each.etat = ETAT_OCCUPEE));
		
		if (nb_bornes_total > 0) {
			taux_occupation_courant <- float(nb_bornes_occupees) / float(nb_bornes_total);
		} else {
			taux_occupation_courant <- 0.0;
		}
		
		// Taille de la file
		if (file_unique) {
			taille_file_courante <- float(length(file_unique_list));
		} else {
			int total_en_file <- 0;
			loop type over: files_par_type.keys {
				total_en_file <- total_en_file + length(files_par_type[type]);
			}
			taille_file_courante <- float(total_en_file);
		}
	}
	
	/* ====================================================================
	   ASPECT VISUEL
	   ==================================================================== */
	aspect base {
		// Rectangle représentant la station (borne grisâtre)
		draw rectangle(30.0, 60.0) at: {50.0, 50.0} color: #lightgray border: #black;
		
		// Zone de file d'attente (cercle gris pâle)
		draw circle(15.0) at: {50.0, 15.0} color: #gainsboro border: #gray;
		
		// Texte d'information
		draw text: "Station" color: #black size: 2.0 at: {50.0, 50.0};
		draw text: ("File: " + string(int(taille_file_courante))) 
			color: #black size: 1.5 at: {50.0, 15.0};
	}
}

/* ======================================================================
   ESPÈCE: BORNE (points de recharge)
   ====================================================================== */
species borne {
	/* ====================================================================
	   ATTRIBUTS EXPLICITES (MONDE FERMÉ)
	   ==================================================================== */
	string type_borne <- TYPE_LENTE;           // Type de borne (à modifier à la création)
	float puissance_kw <- puissance_lente;     // Puissance en kW (cohérent avec type_borne)
	string etat <- ETAT_LIBRE;                 // État courant (par défaut explicite)
	vehicule vehicule_branche <- nil;          // Véhicule en cours de recharge
	float temps_panne_restant <- 0.0;          // Durée restante de panne (en mn)
	int nb_recharges_effectuees <- 0;          // Compteur de recharges complétées
	int nb_pas_occupee <- 0;                   // Nombre de pas où la borne était occupée
	int nb_pas_total <- 0;                     // Nombre total de pas de simulation
	
	/* ====================================================================
	   ACTION: DEMARRER UNE RECHARGE
	   ==================================================================== */
	action demarrer_recharge(vehicule v) {
		etat <- ETAT_OCCUPEE;
		vehicule_branche <- v;
		
		// Calcul du temps de recharge en heures (Comment 6: utiliser v.capacite_kwh)
		float delta_batterie <- v.batterie_cible - v.batterie;  // % à charger
		float energie_kwh <- (delta_batterie / 100.0) * v.capacite_kwh;  // kWh à fournir
		float puissance_effective <- puissance_kw * puissance_reseau_factor;  // kW effectifs
		
		if (puissance_effective > 0.0) {
			v.temps_recharge_restant <- (energie_kwh / puissance_effective) * #h;  // en unités GAMA
		} else {
			v.temps_recharge_restant <- 1.0 * #h;  // Fallback sûr
		}
	}
	
	/* ====================================================================
	   ACTION: LIBÉRER LA BORNE
	   ==================================================================== */
	action liberer {
		etat <- ETAT_LIBRE;
		vehicule_branche <- nil;
		nb_recharges_effectuees <- nb_recharges_effectuees + 1;
	}
	
	/* ====================================================================
	   REFLEX: RECHARGER LE VÉHICULE BRANCHÉ
	   ==================================================================== */
	reflex recharger when: (etat = ETAT_OCCUPEE and vehicule_branche != nil) {
		// Décrémentation du temps restant (pondéré par le facteur réseau)
		float decrement <- step * puissance_reseau_factor;
		vehicule_branche.temps_recharge_restant <- vehicule_branche.temps_recharge_restant - decrement;
		
		// Mise à jour du niveau de batterie proportionnellement (Comment 6: utiliser v.capacite_kwh)
		float puissance_effective <- puissance_kw * puissance_reseau_factor;
		if (puissance_effective > 0.0 and vehicule_branche.capacite_kwh > 0.0) {
			float kwh_fournis <- (puissance_effective * step / #h);
			float pct_batterie <- (kwh_fournis / vehicule_branche.capacite_kwh) * 100.0;
			vehicule_branche.batterie <- min(100.0, vehicule_branche.batterie + pct_batterie);
		}
		
		// Fin de recharge : batterie cible atteinte
		if (vehicule_branche.batterie >= vehicule_branche.batterie_cible 
		    or vehicule_branche.temps_recharge_restant <= 0.0) {
			vehicule_branche.etat_v <- STATE_SERVED;
			
			// Libération de la borne (Comment 11: do liberer; au lieu de liberer();)
			do liberer;
		}
	}
	
	/* ====================================================================
	   REFLEX: TOMBER EN PANNE
	   ==================================================================== */
	reflex tomber_en_panne when: (etat = ETAT_LIBRE or etat = ETAT_OCCUPEE) and flip(p_panne_par_pas) {
		// Si occupée, le véhicule branché rejoint la file (Comment 5: re-queue le véhicule)
		if (etat = ETAT_OCCUPEE and vehicule_branche != nil) {
			vehicule v <- vehicule_branche;
			station s <- first(station);
			if (s != nil) {
				ask s {
					do requeue(v);
				}
			}
			vehicule_branche <- nil;
		}
		
		// Passage en panne avec durée aléatoire
		etat <- ETAT_PANNE;
		temps_panne_restant <- rnd(30.0, 180.0) * #mn;  // Entre 30 et 180 minutes
	}
	
	/* ====================================================================
	   REFLEX: RÉPARER LA BORNE
	   ==================================================================== */
	reflex reparer when: etat = ETAT_PANNE {
		// Décrémentation de la durée de panne
		temps_panne_restant <- temps_panne_restant - step;
		
		if (temps_panne_restant <= 0.0) {
			// Passage en maintenance temporaire
			etat <- ETAT_MAINT;
			temps_panne_restant <- rnd(5.0, 15.0) * #mn;  // Maintenance 5-15 min
		}
	}
	
	/* ====================================================================
	   REFLEX: COMPTER L'OCCUPATION
	   ==================================================================== */
	reflex compter_occupation {
		nb_pas_total <- nb_pas_total + 1;
		if (etat = ETAT_OCCUPEE) {
			nb_pas_occupee <- nb_pas_occupee + 1;
		}
	}
	
	/* ====================================================================
	   ASPECT VISUEL
	   ==================================================================== */
	aspect base {
		// Couleur selon l'état
		rgb couleur <- etat = ETAT_LIBRE ? #green : (etat = ETAT_OCCUPEE ? #orange : (etat = ETAT_PANNE ? #red : (etat = ETAT_MAINT ? #gray : #white)));
		
		// Label abrégé du type
		string label <- type_borne = TYPE_LENTE ? "L" : (type_borne = TYPE_ACC ? "A" : (type_borne = TYPE_RAPIDE ? "R" : "?"));
		
		// Cercle représentant la borne
		draw circle(2.0) color: couleur;
		// Texte au-dessus indiquant le type
		draw text: label color: #black size: 1.0;
	}
}

/* ======================================================================
   ESPÈCE: VEHICULE (agents dynamiques)
   ====================================================================== */
species vehicule {
	/* ====================================================================
	   ATTRIBUTS EXPLICITES (MONDE FERMÉ)
	   ==================================================================== */
	float batterie <- rnd(5.0, 40.0);                    // % initial de batterie
	float batterie_cible <- 80.0;                        // Objectif de recharge
	float capacite_kwh <- rnd(30.0, 80.0);              // Capacité du réservoir
	float urgence <- rnd(0.0, 1.0);                     // Niveau d'urgence (0=aucune, 1=max)
	float tolerance_attente <- rnd(15.0, 90.0) * #mn;  // Tolérance d'attente maximale
	string preference_puissance <- one_of([TYPE_LENTE, TYPE_ACC, TYPE_RAPIDE]);  // Type préféré
	string etat_v <- STATE_ARRIVING;                    // État du véhicule
	float t_arrivee <- time;                            // Temps d'arrivée initial
	float temps_attente_actuel <- 0.0;                  // Durée d'attente accumulée
	float temps_recharge_restant <- 0.0;                // Temps restant pour recharge
	borne borne_assignee <- nil;                        // Borne assignée (si recharge)
	float seuil_urgence_quitter <- 0.85;                // Seuil d'urgence pour abandon
	
	/* ====================================================================
	   ACTION: ESSAYER UNE CONNEXION À UNE BORNE
	   ==================================================================== */
	action essayer_connexion {
		// Chercher une borne libre correspondant à la préférence
		list<borne> bornes_libres <- (borne where (each.etat = ETAT_LIBRE));
		
		if (empty(bornes_libres)) {
			// Aucune borne libre : rejoindre la file
			etat_v <- STATE_WAITING;
			station first_station <- first(station);
			if (first_station != nil) {
				ask first_station {
					do enfiler(myself);
				}
			}
		} else {
			// Chercher d'abord une borne avec la puissance préférée
			list<borne> bornes_pref <- bornes_libres where (each.type_borne = preference_puissance);
			
			if (!empty(bornes_pref)) {
				borne_assignee <- first(bornes_pref);
			} else {
				borne_assignee <- first(bornes_libres);
			}
			
			// Démarrer la recharge
			if (borne_assignee != nil) {
				ask borne_assignee {
					do demarrer_recharge(myself);
				}
				etat_v <- STATE_CHARGING;
			}
		}
	}
	
	/* ====================================================================
	   ACTION D'INITIALISATION: APPELÉE À LA CRÉATION
	   ==================================================================== */
	init {
		do essayer_connexion;
	}
	
	/* ====================================================================
	   REFLEX: GESTION DE L'ATTENTE EN FILE
	   ==================================================================== */
	// Réévaluation périodique toutes les 5 minutes (Comment 12, 2)
	reflex attente when: etat_v = STATE_WAITING {
		// Accumulation du temps d'attente
		temps_attente_actuel <- temps_attente_actuel + step;
		
		// Re-query ETA every 5 simulated minutes; modulo detects boundary crossing
		if (affichage_temps_attente and (int(temps_attente_actuel) mod (5 * 60)) < int(step)) {
			float eta_estime <- 0.0;
			station first_station <- first(station);
			if (first_station != nil) {
				ask first_station {
					eta_estime <- estimer_attente(myself);
				}
			}
			
			// Abandon préemptif si ETA trop long
			if (eta_estime > tolerance_attente) {
				etat_v <- STATE_ABANDONED;
			}
		}
		
		// Abandon par dépassement de tolérance
		if (temps_attente_actuel > tolerance_attente) {
			etat_v <- STATE_ABANDONED;
		}
		
		// Abandon par urgence élevée + attente prolongée
		if (urgence > seuil_urgence_quitter and 
		    temps_attente_actuel > (tolerance_attente / 2.0)) {
			etat_v <- STATE_ABANDONED;
		}
		
		// Traitement de l'abandon : retrait de la file et statistiques
		if (etat_v = STATE_ABANDONED) {
			station first_station <- first(station);
			if (first_station != nil) {
				ask first_station {
					do retirer(myself);
				}
			}
			total_abandons <- total_abandons + 1;
			somme_satisfaction <- somme_satisfaction + 0.0;
			nb_satisfaction <- nb_satisfaction + 1;
			do die;
		}
	}
	
	/* ====================================================================
	   REFLEX: COMPTABILISER LES VÉHICULES SERVIS
	   ==================================================================== */
	reflex comptabiliser_servi when: etat_v = STATE_SERVED {
		// Accumulation des temps d'attente
		somme_temps_attente <- somme_temps_attente + temps_attente_actuel;
		nb_temps_attente <- nb_temps_attente + 1;
		
		// Calcul de la satisfaction
		float satisfaction_temps <- max(0.0, 1.0 - (temps_attente_actuel / tolerance_attente));
		float bonus_preference <- (borne_assignee != nil and 
		                           preference_puissance = borne_assignee.type_borne) ? 1.0 : 0.7;
		float satisfaction <- satisfaction_temps * bonus_preference;
		
		// Enregistrement de la satisfaction
		somme_satisfaction <- somme_satisfaction + satisfaction;
		nb_satisfaction <- nb_satisfaction + 1;
		
		// Incrémentation des véhicules servis
		total_servis <- total_servis + 1;
		
		// Destruction du véhicule
		do die;
	}
	
	/* ====================================================================
	   ASPECT VISUEL
	   ==================================================================== */
	aspect base {
		// Couleur selon l'état du véhicule
		rgb couleur <- etat_v = STATE_ARRIVING ? #blue : (etat_v = STATE_WAITING ? #yellow : (etat_v = STATE_CHARGING ? #cyan : (etat_v = STATE_SERVED ? #green : (etat_v = STATE_ABANDONED ? #red : #white))));
		
		// Positionnement : près de la borne si en charge, sinon dans la zone file
		point pos <- location;
		if (etat_v = STATE_CHARGING and borne_assignee != nil) {
			pos <- borne_assignee.location;  // Comment 3: location au lieu de position
		} else if (etat_v = STATE_WAITING) {
			// Placer dans une zone "file" (zone de waiting)
			pos <- {50.0 + rnd(-10.0, 10.0), 10.0 + rnd(-5.0, 5.0)};
		}
		
		// Triangle représentant le véhicule
		draw triangle(1.5) at: pos color: couleur;
	}
}

/* ======================================================================
   EXPERIMENT: INTERFACE GRAPHIQUE
   ====================================================================== */
experiment Station_Recharge type: gui {
	/* ====================================================================
	   PARAMÈTRES EXPOSÉS À L'INTERFACE UTILISATEUR
	   ==================================================================== */
	parameter "Nombre de bornes lentes" var: nb_bornes_lentes category: "Bornes";
	parameter "Nombre de bornes accélérées" var: nb_bornes_acc category: "Bornes";
	parameter "Nombre de bornes rapides" var: nb_bornes_rapides category: "Bornes";
	
	parameter "Puissance lente (kW)" var: puissance_lente category: "Puissances";
	parameter "Puissance accélérée (kW)" var: puissance_acc category: "Puissances";
	parameter "Puissance rapide (kW)" var: puissance_rapide category: "Puissances";
	
	parameter "Politique de file d'attente" var: politique_file
		among: [POL_FIFO, POL_LOWBAT, POL_URGENCE, POL_PREF] category: "File";
	parameter "File unique (vs par type)" var: file_unique category: "File";
	
	parameter "Affichage temps d'attente" var: affichage_temps_attente category: "Information";
	
	parameter "Probabilité de panne par pas" var: p_panne_par_pas category: "Stochastique";
	parameter "Probabilité d'arrivée groupée" var: p_burst category: "Stochastique";
	parameter "Taille des arrivées groupées" var: taille_burst category: "Stochastique";
	
	/* ====================================================================
	   SORTIES GRAPHIQUES ET MONITEURS
	   ==================================================================== */
	output {
		// Affichage de la carte de la station
		display CarteStation type: 2d refresh: every(1#cycle) {
			species station aspect: base;
			species borne aspect: base;
			species vehicule aspect: base;
		}
		
		// Série temporelle du taux d'occupation
		display Occupation_Series refresh: every(1#cycle) type: 2d {
			chart "Taux d'occupation des bornes" type: series {
				data "Taux d'occupation" value: taux_occupation_courant color: rgb('blue');
				data "Taux d'occupation moyen" value: taux_occupation_moyen color: rgb('darkblue');
			}
		}
		
		// Série temporelle de la taille de file (Comment 8: ajouter taille_file_moyenne)
		display File_Series refresh: every(1#cycle) type: 2d {
			chart "Évolution de la file d'attente" type: series {
				data "Taille file instantanée" value: taille_file_courante color: rgb('orange');
				data "Taille file moyenne" value: taille_file_moyenne color: rgb('darkorange');
			}
		}
		
		// Série temporelle du temps d'attente moyen
		display Attente_Series refresh: every(1#cycle) type: 2d {
			chart "Temps d'attente moyen" type: series {
				data "Temps d'attente moyen (mn)" value: temps_attente_moyen color: rgb('red');
			}
		}
		
		// Série temporelle des taux d'abandon et satisfaction
		display Abandon_Satisfaction refresh: every(1#cycle) type: 2d {
			chart "Abandon et satisfaction" type: series {
				data "Taux d'abandon" value: taux_abandon color: rgb('magenta');
				data "Taux de satisfaction" value: taux_satisfaction color: rgb('green');
			}
		}
		
		// Répartition des états des bornes (camembert)
		display Repartition_Bornes_Pie refresh: every(5#cycle) {
			chart "Répartition des bornes par état" type: pie {
				data "Libres" value: borne count (each.etat = ETAT_LIBRE) color: rgb('green');
				data "Occupées" value: borne count (each.etat = ETAT_OCCUPEE) color: rgb('orange');
				data "En panne" value: borne count (each.etat = ETAT_PANNE) color: rgb('red');
				data "Maintenance" value: borne count (each.etat = ETAT_MAINT) color: rgb('gray');
			}
		}
		
		// Répartition des véhicules par état (histogramme) (Comment 14: remplacer Arriving par Served)
		display Repartition_Vehicules_Hist refresh: every(5#cycle) {
			chart "Répartition des véhicules par état" type: histogram {
				data "Waiting" value: vehicule count (each.etat_v = STATE_WAITING) color: rgb('yellow');
				data "Charging" value: vehicule count (each.etat_v = STATE_CHARGING) color: rgb('cyan');
				data "Served (cumul)" value: total_servis color: rgb('green');
			}
		}
		
		// Indicateurs globaux (histogramme)
		display Indicateurs_Globaux_Hist refresh: every(10#cycle) {
			chart "Indicateurs globaux" type: histogram {
				data "Total arrivées" value: total_arrivees color: rgb('blue');
				data "Total servis" value: total_servis color: rgb('green');
				data "Total abandons" value: total_abandons color: rgb('red');
			}
		}
		
		// Moniteurs d'indicateurs clés
		monitor "Heure simulée" value: heure_simulee;
		monitor "Politique" value: politique_file;
		monitor "Facteur réseau" value: puissance_reseau_factor;
		monitor "Taux occupation moyen" value: taux_occupation_moyen;
		monitor "Temps attente moyen (mn)" value: temps_attente_moyen;
		monitor "Taux abandon" value: taux_abandon;
		monitor "Taux satisfaction" value: taux_satisfaction;
	}
}
