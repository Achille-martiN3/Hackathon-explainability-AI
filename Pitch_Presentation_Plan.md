# STRUCTURE DE LA PRÉSENTATION (10 MINUTES)
Hackathon - Projet Trusted HR-AI

## CHRONOMÉTRAGE IDÉAL
* 00:00 - 01:30 : Introduction & Le Problème (Slides 1, 2)
* 01:30 - 03:00 : Notre Solution & Différenciation (Slide 3)
* 03:00 - 07:00 : DÉMO LIVE DE L'APPLICATION (Cœur de la présentation)
* 07:00 - 08:30 : Sous le capot : Cybersécurité & Privacy by Design (Slide 4)
* 08:30 - 09:30 : Sous le capot : Éthique & Explicabilité (Slide 5)
* 09:30 - 10:00 : Conclusion & Prochaines étapes (Slide 6)

----------------------------------------------------------------------
## DÉTAIL DES SLIDES

### SLIDE 1 : Titre (0:30 min)
* Titre : Trusted HR-AI : Conservez vos talents en toute sécurité.
* Sous-titre : Prédiction du turnover, Intelligence Explicable et Privacy by Design.
* Discours (Accroche) : "Saviez-vous qu'un départ imprévu coûte en moyenne 6 à 9 mois de salaire à l'entreprise ? Et si l'IA pouvait le prévenir, sans devenir une boîte noire discriminatoire ?"

### SLIDE 2 : Le Problème (1:00 min)
* Contenu :
  1. Dramatique pour le business : La perte de talents coûte cher et fait perdre en savoir-faire.
  2. Le danger des statistiques aveugles : Des modèles qui font des moyennes, sans aider l'individu.
  3. Le danger de l'IA boîte noire : Refus des RH d'utiliser des algorithmes qui décident sans expliquer, au mépris des lois sur les données privées (RGPD).
* Discours : "On veut anticiper les départs. Mais on ne peut pas injecter des données RH ultra-sensibles dans une boîte noire. Il faut de la confiance, de l'explicabilité et de la sécurité."

### SLIDE 3 : Notre Solution : "Trusted HR-AI" (1:30 min)
* Contenu : Un système d'aide à la décision RH basé sur le Machine Learning...
* 3 Piliers :
  1. Prédictif (Machine Learning) : Capte les signaux faibles et non linéaires.
  2. Explicable (XAI) : Algorithmes SHAP pour comprendre *pourquoi* un individu spécifique veut partir.
  3. Sécurisé & Éthique : Privacy by Design, contrôles d'accès, audit anti-biais.
* Transition : "Plutôt que d'en parler, voici l'outil que la ligne RH utilise au quotidien."

----------------------------------------------------------------------
### DÉMO LIVE : 4 Minutes (Ouvrir Streamlit)
1. Login (30s) : Montrer l'écran de connexion. Parler de RBAC (Role-Based Access Control) pour protéger l'accès aux données. (admin / hr-secure-2024).
2. Dashboard (1m) : Montrer le leaderboard des risques. Préciser que tous les noms/IDs sont hachés (pseudonymisation).
3. Employee Analysis (1m30s) : LE CŒUR DE LA DÉMO. Choisir un employé à risque. Montrer les barres SHAP vertes et rouges. "L'IA donne ici le *pourquoi*. L'action RH devient chirurgicale (ex: proposer une formation)."
4. Fairness Audit (1m) : Montrer l'onglet éthique. C'est l'audit automatique des biais de Genre et de Race (FPR). "Nous prouvons statistiquement que l'IA ne discrimine pas."
----------------------------------------------------------------------

### SLIDE 4 : Sous le capot : Cybersécurité (1:30 min)
* Titre : Sécurité by Design & DevSecOps
* Contenu :
  - Pseudonymisation forte (Salting) : "Nous hachons les PII (SHA-256) en y ajoutant un 'Salt' caché (variable d'environnement) pour contrer les attaques par dictionnaire/Rainbow tables."
  - Anti-fuite de données (Data Leakage) : Nettoyage drastique des variables post-événement pour ne pas tricher lors de l'entraînement.
  - Code Sécurisé : "Approche DevSecOps : Notre pipeline intègre 'Bandit' (scanneur de failles Python). Zéro faille critique."

### SLIDE 5 : Sous le capot : Éthique & Explicabilité (1:00 min)
* Titre : Explicabilité locale et Conformité
* Contenu (Mettre un bout de screenshot du notebook 'FPR by Race') :
  - Légalité & Anti-biais : Vérification systémique du Taux de Faux Positifs (FPR) sur les groupes protégés (Genre/Origine). L'IA ne copie pas les discriminations du passé.
  - XAI (Shapley) : Utilisation de la théorie des jeux pour forcer le modèle Random Forest à fournir une explication pondérée de sa décision. Pas de Black Box.

### SLIDE 6 : Conclusion & Avenir (0:30 min)
* Titre : L'Avenir du Projet
* Contenu :
  - Brancher le login sur un vrai SSO d'entreprise (OAuth2).
  - Évolution vers le "Prescriptif" (L'IA recommandera l'action RH exacte à mener).
* Mot de la fin : "Avec Trusted HR-AI, ce n'est pas la machine qui décide. Ce sont les Humains. Mais l'IA vient de leur donner un super-pouvoir. Merci."

----------------------------------------------------------------------
## 💡 CONSEILS POUR LE JURY
* Placez bien les buzzwords : "Privacy by Design", "RBAC", "Zero Trust", "DevSecOps".
* Ne rentrez pas trop dans les mathématiques pures de SHAP, le jury veut voir la valeur métier et l'impact.
* Si le jury vous attaque sur "Pourquoi pas un modèle IA génératif (ChatGPT) ?", répondez : "Pour des données RH tabulaires et quantitatives basées sur le passé, le Machine Learning classique couplé à de l'Explicabilité (SHAP) est beaucoup moins coûteux, moins énergivore, plus souverain et surtout moins sujet aux hallucinations qu'un LLM."