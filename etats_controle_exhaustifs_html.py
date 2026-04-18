# -*- coding: utf-8 -*-
"""
Module de génération HTML pour les 16 états de contrôle exhaustifs
Génère du HTML complet conforme au fichier test_etats_controle_html.html
"""

from typing import Dict, List, Any


def format_montant(montant: float) -> str:
    """Formate un montant avec séparateurs de milliers"""
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def generate_etat_1_statistiques_couverture_n(controles: Dict) -> str:
    """1. Statistiques de Couverture (Exercice N)"""
    stats = controles.get('statistiques', {})
    taux = stats.get('taux_couverture', 0)
    
    # Déterminer le badge
    if taux >= 95:
        badge_class = "badge-success"
        badge_text = "Excellent"
        box_class = "success-box"
        status_text = "Excellent - La majorité des comptes sont intégrés dans les états financiers"
    elif taux >= 80:
        badge_class = "badge-warning"
        badge_text = "Acceptable"
        box_class = "warning-box"
        status_text = "Acceptable - La plupart des comptes sont intégrés"
    else:
        badge_class = "badge-danger"
        badge_text = "Insuffisant"
        box_class = "danger-box"
        status_text = "Insuffisant - Trop de comptes non intégrés"
    
    html = f"""
            <!-- 1. Statistiques de Couverture -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>📊 1. Statistiques de Couverture (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="{box_class}">
                            <h3>✅ Taux de Couverture: <span class="badge {badge_class}">{taux:.1f}%</span></h3>
                            <p style="margin-top: 10px;">{status_text}</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>Indicateur</th>
                                    <th style="text-align: right;">Valeur</th>
                                    <th style="text-align: center;">Statut</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Comptes dans la balance</td>
                                    <td class="montant-cell">{stats.get('total_comptes_balance', 0)}</td>
                                    <td style="text-align: center;">-</td>
                                </tr>
                                <tr>
                                    <td>Comptes intégrés</td>
                                    <td class="montant-cell">{stats.get('comptes_integres', 0)}</td>
                                    <td style="text-align: center;"><span class="badge badge-success">✓</span></td>
                                </tr>
                                <tr>
                                    <td>Comptes non intégrés</td>
                                    <td class="montant-cell">{stats.get('comptes_non_integres', 0)}</td>
                                    <td style="text-align: center;"><span class="badge badge-warning">⚠</span></td>
                                </tr>
                                <tr class="total-row">
                                    <td>Taux de couverture</td>
                                    <td class="montant-cell">{taux:.1f}%</td>
                                    <td style="text-align: center;"><span class="badge {badge_class}">{badge_text}</span></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Interprétation</h4>
                            <ul style="margin-left: 20px; margin-top: 10px;">
                                <li><strong>≥ 95%</strong> : ✅ Excellent (badge vert)</li>
                                <li><strong>80-94%</strong> : ⚠️ Acceptable (badge orange)</li>
                                <li><strong>&lt; 80%</strong> : ❌ Insuffisant (badge rouge)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
"""
    return html


def generate_etat_2_equilibre_bilan_n(controles: Dict, totaux: Dict) -> str:
    """2. Équilibre du Bilan (Exercice N)"""
    equilibre = controles.get('equilibre_bilan', {})
    actif = equilibre.get('actif', 0)
    passif = equilibre.get('passif', 0)
    difference = equilibre.get('difference', 0)
    pct_ecart = equilibre.get('pourcentage_ecart', 0)
    est_equilibre = equilibre.get('equilibre', False)
    
    if est_equilibre:
        box_class = "success-box"
        badge_class = "badge-success"
        status_text = "Le bilan est parfaitement équilibré (Actif = Passif)"
        badge_text = "✓ Équilibré"
    else:
        box_class = "danger-box"
        badge_class = "badge-danger"
        status_text = "Le bilan n'est PAS équilibré - Vérifier les écritures"
        badge_text = "✗ Déséquilibré"
    
    html = f"""
            <!-- 2. Équilibre du Bilan -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚖️ 2. Équilibre du Bilan (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="{box_class}">
                            <h3>{'✅' if est_equilibre else '❌'} Bilan {'Équilibré' if est_equilibre else 'Déséquilibré'} <span class="badge {badge_class}">Différence {'<' if est_equilibre else '≥'} 0.01</span></h3>
                            <p style="margin-top: 10px;">{status_text}</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>Élément</th>
                                    <th style="text-align: right;">Montant (FCFA)</th>
                                    <th style="text-align: center;">Statut</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Total Actif</td>
                                    <td class="montant-cell">{format_montant(actif)}</td>
                                    <td style="text-align: center;">-</td>
                                </tr>
                                <tr>
                                    <td>Total Passif</td>
                                    <td class="montant-cell">{format_montant(passif)}</td>
                                    <td style="text-align: center;">-</td>
                                </tr>
                                <tr class="total-row">
                                    <td>Différence (Actif - Passif)</td>
                                    <td class="montant-cell">{format_montant(difference)}</td>
                                    <td style="text-align: center;"><span class="badge {badge_class}">{badge_text}</span></td>
                                </tr>
                                <tr>
                                    <td>Pourcentage d'écart</td>
                                    <td class="montant-cell">{pct_ecart:.2f}%</td>
                                    <td style="text-align: center;"><span class="badge {badge_class}">{'Parfait' if est_equilibre else 'Écart'}</span></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Seuil de Tolérance</h4>
                            <ul style="margin-left: 20px; margin-top: 10px;">
                                <li><strong>&lt; 0.01</strong> : ✅ Équilibré</li>
                                <li><strong>≥ 0.01</strong> : ❌ Déséquilibré</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
"""
    return html


def generate_etat_3_coherence_resultat_n(controles: Dict, totaux: Dict) -> str:
    """3. Cohérence Résultat (Exercice N)"""
    equilibre_res = controles.get('equilibre_resultat', {})
    resultat_cr = equilibre_res.get('resultat_cr', 0)
    resultat_bilan = equilibre_res.get('resultat_bilan', 0)
    difference = equilibre_res.get('difference', 0)
    est_coherent = equilibre_res.get('equilibre', False)
    
    type_resultat = "Bénéfice" if resultat_cr > 0 else "Perte" if resultat_cr < 0 else "Nul"
    badge_type = "badge-success" if resultat_cr > 0 else "badge-danger" if resultat_cr < 0 else "badge-info"
    
    if est_coherent:
        box_class = "success-box"
        badge_class = "badge-success"
        status_text = "Le résultat du compte de résultat correspond au résultat du bilan"
    else:
        box_class = "danger-box"
        badge_class = "badge-danger"
        status_text = "INCOHÉRENCE détectée entre le résultat CR et le résultat Bilan"
    
    html = f"""
            <!-- 3. Cohérence Résultat -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>💰 3. Cohérence Résultat (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="{box_class}">
                            <h3>{'✅' if est_coherent else '❌'} Résultats {'Cohérents' if est_coherent else 'Incohérents'} <span class="badge {badge_class}">Différence {'<' if est_coherent else '≥'} 0.01</span></h3>
                            <p style="margin-top: 10px;">{status_text}</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>Source</th>
                                    <th style="text-align: right;">Résultat (FCFA)</th>
                                    <th style="text-align: center;">Type</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Résultat Compte de Résultat (Produits - Charges)</td>
                                    <td class="montant-cell">{format_montant(resultat_cr)}</td>
                                    <td style="text-align: center;"><span class="badge {badge_type}">{type_resultat}</span></td>
                                </tr>
                                <tr>
                                    <td>Résultat Bilan (Actif - Passif)</td>
                                    <td class="montant-cell">{format_montant(resultat_bilan)}</td>
                                    <td style="text-align: center;"><span class="badge {badge_type}">{type_resultat}</span></td>
                                </tr>
                                <tr class="total-row">
                                    <td>Différence</td>
                                    <td class="montant-cell">{format_montant(difference)}</td>
                                    <td style="text-align: center;"><span class="badge {badge_class}">{'✓ Cohérent' if est_coherent else '✗ Incohérent'}</span></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Formule</h4>
                            <p style="margin-top: 10px;"><strong>Résultat CR</strong> = Produits - Charges</p>
                            <p><strong>Résultat Bilan</strong> = Actif - Passif</p>
                            <p><strong>Cohérence</strong> = |Résultat CR - Résultat Bilan| &lt; 0.01</p>
                        </div>
                    </div>
                </div>
            </div>
"""
    return html


def generate_etat_4_comptes_non_integres_n(controles: Dict) -> str:
    """4. Comptes Non Intégrés (Exercice N)"""
    comptes_non_integres = controles.get('comptes_non_integres', [])
    nb_comptes = len(comptes_non_integres)
    
    if nb_comptes == 0:
        html = f"""
            <!-- 4. Comptes Non Intégrés -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚠️ 4. Comptes Non Intégrés (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="success-box">
                            <h3>✅ Tous les Comptes Intégrés <span class="badge badge-success">Parfait</span></h3>
                            <p style="margin-top: 10px;">Tous les comptes de la balance ont été intégrés dans les états financiers</p>
                        </div>
                    </div>
                </div>
            </div>
"""
    else:
        # Calculer l'impact total
        impact_total = sum(abs(c.get('solde_net', 0)) for c in comptes_non_integres)
        
        # Générer les lignes du tableau
        lignes_tableau = ""
        for compte in comptes_non_integres:
            num_compte = compte.get('numero_compte', '')
            intitule = compte.get('intitule', '')
            classe = str(num_compte)[0] if num_compte else ''
            solde_debit = compte.get('solde_debit', 0)
            solde_credit = compte.get('solde_credit', 0)
            solde_net = compte.get('solde_net', 0)
            raison = compte.get('raison', 'Non défini')
            
            lignes_tableau += f"""
                                <tr>
                                    <td class="ref-cell">{num_compte}</td>
                                    <td>{intitule}</td>
                                    <td style="text-align: center;">{classe}</td>
                                    <td class="montant-cell">{format_montant(solde_debit) if solde_debit > 0 else '-'}</td>
                                    <td class="montant-cell">{format_montant(abs(solde_credit)) if solde_credit < 0 else '-'}</td>
                                    <td class="montant-cell">{format_montant(solde_net)}</td>
                                    <td>{raison}</td>
                                </tr>
"""
        
        html = f"""
            <!-- 4. Comptes Non Intégrés -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚠️ 4. Comptes Non Intégrés (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="warning-box">
                            <h3>⚠️ {nb_comptes} Comptes Non Intégrés <span class="badge badge-warning">À Vérifier</span></h3>
                            <p style="margin-top: 10px;">Certains comptes de la balance n'ont pas été intégrés dans les états financiers</p>
                            <p style="margin-top: 5px;"><strong>Impact:</strong> {format_montant(impact_total)} FCFA</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>N° Compte</th>
                                    <th>Intitulé</th>
                                    <th style="text-align: center;">Classe</th>
                                    <th style="text-align: right;">Solde Débit</th>
                                    <th style="text-align: right;">Solde Crédit</th>
                                    <th style="text-align: right;">Solde Net</th>
                                    <th>Raison</th>
                                </tr>
                            </thead>
                            <tbody>
{lignes_tableau}
                                <tr class="total-row">
                                    <td colspan="5">Total Comptes Non Intégrés</td>
                                    <td class="montant-cell">{format_montant(impact_total)}</td>
                                    <td>{nb_comptes} comptes</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Actions Correctives</h4>
                            <ol style="margin-left: 20px; margin-top: 10px;">
                                <li>Vérifier la codification du compte</li>
                                <li>Ajouter la racine dans <code>correspondances_syscohada.json</code></li>
                                <li>Vérifier si le compte doit être intégré</li>
                                <li>Contrôler la cohérence avec le plan comptable SYSCOHADA</li>
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    return html


def generate_etat_5_comptes_sens_inverse_n(controles: Dict) -> str:
    """5. Comptes avec Sens Inversé (Exercice N)"""
    comptes_sens_inverse = controles.get('comptes_sens_inverse', [])
    nb_comptes = len(comptes_sens_inverse)
    
    if nb_comptes == 0:
        html = f"""
            <!-- 5. Comptes avec Sens Inversé -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🔄 5. Comptes avec Sens Inversé (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="success-box">
                            <h3>✅ Aucun Compte avec Sens Inversé <span class="badge badge-success">Parfait</span></h3>
                            <p style="margin-top: 10px;">Tous les comptes ont le sens normal de leur classe</p>
                        </div>
                    </div>
                </div>
            </div>
"""
    else:
        # Générer les lignes du tableau
        lignes_tableau = ""
        for compte in comptes_sens_inverse:
            num_compte = compte.get('numero_compte', '')
            intitule = compte.get('intitule', '')
            classe = str(num_compte)[0] if num_compte else ''
            sens_attendu = compte.get('sens_attendu', 'Variable')
            sens_reel = compte.get('sens_reel', '')
            solde_net = compte.get('solde_net', 0)
            
            badge_attendu = "badge-info"
            badge_reel = "badge-warning"
            
            lignes_tableau += f"""
                                <tr>
                                    <td class="ref-cell">{num_compte}</td>
                                    <td>{intitule}</td>
                                    <td style="text-align: center;">{classe}</td>
                                    <td style="text-align: center;"><span class="badge {badge_attendu}">{sens_attendu}</span></td>
                                    <td style="text-align: center;"><span class="badge {badge_reel}">{sens_reel}</span></td>
                                    <td class="montant-cell">{format_montant(solde_net)}</td>
                                </tr>
"""
        
        html = f"""
            <!-- 5. Comptes avec Sens Inversé -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🔄 5. Comptes avec Sens Inversé (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="warning-box">
                            <h3>⚠️ {nb_comptes} Comptes avec Sens Inversé <span class="badge badge-warning">À Analyser</span></h3>
                            <p style="margin-top: 10px;">Ces comptes ont un solde contraire au sens normal de leur classe</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>N° Compte</th>
                                    <th>Intitulé</th>
                                    <th style="text-align: center;">Classe</th>
                                    <th style="text-align: center;">Sens Attendu</th>
                                    <th style="text-align: center;">Sens Réel</th>
                                    <th style="text-align: right;">Solde Net</th>
                                </tr>
                            </thead>
                            <tbody>
{lignes_tableau}
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Sens Normal par Classe</h4>
                            <table style="width: 100%; margin-top: 10px;">
                                <tbody>
                                    <tr>
                                        <td><strong>Classe 1:</strong> Crédit (Capitaux)</td>
                                        <td><strong>Classe 2:</strong> Débit (Immobilisations)</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Classe 3:</strong> Débit (Stocks)</td>
                                        <td><strong>Classe 4:</strong> Variable (Tiers)</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Classe 5:</strong> Débit (Trésorerie)</td>
                                        <td><strong>Classe 6:</strong> Débit (Charges)</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Classe 7:</strong> Crédit (Produits)</td>
                                        <td><strong>Classe 8:</strong> Variable (Spéciaux)</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    return html


def generate_etat_6_comptes_desequilibre_n(controles: Dict) -> str:
    """6. Comptes Créant un Déséquilibre (Exercice N)"""
    comptes_desequilibre = controles.get('comptes_desequilibre', [])
    nb_comptes = len(comptes_desequilibre)
    
    if nb_comptes == 0:
        html = f"""
            <!-- 6. Comptes Créant un Déséquilibre -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚠️ 6. Comptes Créant un Déséquilibre (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="success-box">
                            <h3>✅ Aucun Compte en Déséquilibre <span class="badge badge-success">Parfait</span></h3>
                            <p style="margin-top: 10px;">Tous les comptes ont le sens correct pour leur section</p>
                        </div>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Règles de Sens par Section</h4>
                            <table style="width: 100%; margin-top: 10px;">
                                <thead>
                                    <tr>
                                        <th>Section</th>
                                        <th>Sens Attendu</th>
                                        <th>Problème si...</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>Bilan Actif</strong></td>
                                        <td>Débit (positif)</td>
                                        <td>Solde créditeur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Bilan Passif</strong></td>
                                        <td>Crédit (négatif)</td>
                                        <td>Solde débiteur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Charges</strong></td>
                                        <td>Débit (positif)</td>
                                        <td>Solde créditeur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Produits</strong></td>
                                        <td>Crédit (négatif)</td>
                                        <td>Solde débiteur</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
"""
    else:
        # Générer les lignes du tableau
        lignes_tableau = ""
        for compte in comptes_desequilibre:
            num_compte = compte.get('numero_compte', '')
            intitule = compte.get('intitule', '')
            section = compte.get('section', '')
            sens_attendu = compte.get('sens_attendu', '')
            sens_reel = compte.get('sens_reel', '')
            solde_net = compte.get('solde_net', 0)
            
            lignes_tableau += f"""
                                <tr>
                                    <td class="ref-cell">{num_compte}</td>
                                    <td>{intitule}</td>
                                    <td>{section}</td>
                                    <td style="text-align: center;"><span class="badge badge-info">{sens_attendu}</span></td>
                                    <td style="text-align: center;"><span class="badge badge-danger">{sens_reel}</span></td>
                                    <td class="montant-cell">{format_montant(solde_net)}</td>
                                </tr>
"""
        
        html = f"""
            <!-- 6. Comptes Créant un Déséquilibre -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚠️ 6. Comptes Créant un Déséquilibre (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="danger-box">
                            <h3>❌ {nb_comptes} Comptes en Déséquilibre <span class="badge badge-danger">À Corriger</span></h3>
                            <p style="margin-top: 10px;">Ces comptes ont un sens incorrect pour leur section</p>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>N° Compte</th>
                                    <th>Intitulé</th>
                                    <th>Section</th>
                                    <th style="text-align: center;">Sens Attendu</th>
                                    <th style="text-align: center;">Sens Réel</th>
                                    <th style="text-align: right;">Solde Net</th>
                                </tr>
                            </thead>
                            <tbody>
{lignes_tableau}
                            </tbody>
                        </table>
                        
                        <div class="info-box" style="margin-top: 20px;">
                            <h4>📌 Règles de Sens par Section</h4>
                            <table style="width: 100%; margin-top: 10px;">
                                <thead>
                                    <tr>
                                        <th>Section</th>
                                        <th>Sens Attendu</th>
                                        <th>Problème si...</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>Bilan Actif</strong></td>
                                        <td>Débit (positif)</td>
                                        <td>Solde créditeur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Bilan Passif</strong></td>
                                        <td>Crédit (négatif)</td>
                                        <td>Solde débiteur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Charges</strong></td>
                                        <td>Débit (positif)</td>
                                        <td>Solde créditeur</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Produits</strong></td>
                                        <td>Crédit (négatif)</td>
                                        <td>Solde débiteur</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    return html


def generate_etat_7_hypothese_affectation_n(controles: Dict, totaux: Dict) -> str:
    """7. Hypothèse d'Affectation du Résultat (Exercice N)"""
    hypothese = controles.get('hypothese_affectation', {})
    resultat_net = hypothese.get('resultat_net', 0)
    actif = hypothese.get('actif', 0)
    passif_sans_resultat = hypothese.get('passif_sans_resultat', 0)
    difference_avant = hypothese.get('difference_avant', 0)
    passif_avec_resultat = hypothese.get('passif_avec_resultat', 0)
    difference_apres = hypothese.get('difference_apres', 0)
    equilibre_apres = hypothese.get('equilibre_apres', False)
    
    type_resultat = "Bénéfice" if resultat_net > 0 else "Perte" if resultat_net < 0 else "Nul"
    badge_type = "badge-success" if resultat_net > 0 else "badge-danger" if resultat_net < 0 else "badge-info"
    
    box_class = "success-box" if equilibre_apres else "danger-box"
    
    # Préparer les textes sans backslash
    if equilibre_apres:
        recommandation_text = "Affecter le résultat au passif (compte 13 - Résultat de l'exercice)"
        explication_text = "Cette affectation permettra d'équilibrer parfaitement le bilan."
        titre_equilibre = "S'Équilibrerait"
        texte_equilibre = "équilibrerait"
    else:
        recommandation_text = "Vérifier les écritures comptables avant affectation"
        explication_text = "Le bilan ne s'équilibre pas même avec l'affectation du résultat."
        titre_equilibre = "Ne S'Équilibrerait Pas"
        texte_equilibre = "n'équilibrerait pas"
    
    html = f"""
            <!-- 7. Hypothèse d'Affectation du Résultat -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>💡 7. Hypothèse d'Affectation du Résultat (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="{box_class}">
                            <h3>{'✅' if equilibre_apres else '❌'} Le Bilan {titre_equilibre} <span class="badge {'badge-success' if equilibre_apres else 'badge-danger'}">Hypothèse {'Validée' if equilibre_apres else 'Non Validée'}</span></h3>
                            <p style="margin-top: 10px;">L'affectation du résultat au passif (compte 13) {texte_equilibre} le bilan</p>
                        </div>
                        
                        <h3 style="margin-top: 30px; margin-bottom: 15px;">Type de Résultat</h3>
                        <div class="{'success-box' if resultat_net > 0 else 'danger-box'}">
                            <h3><span class="badge {badge_type}">{type_resultat.upper()}</span> {format_montant(resultat_net)} FCFA</h3>
                        </div>
                        
                        <h3 style="margin-top: 30px; margin-bottom: 15px;">Situation Actuelle (sans affectation)</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Élément</th>
                                    <th style="text-align: right;">Montant (FCFA)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Actif</td>
                                    <td class="montant-cell">{format_montant(actif)}</td>
                                </tr>
                                <tr>
                                    <td>Passif (sans résultat)</td>
                                    <td class="montant-cell">{format_montant(passif_sans_resultat)}</td>
                                </tr>
                                <tr class="total-row">
                                    <td>Différence (Actif - Passif)</td>
                                    <td class="montant-cell" style="color: {'#4caf50' if difference_avant >= 0 else '#f44336'};">{format_montant(difference_avant)}</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <h3 style="margin-top: 30px; margin-bottom: 15px;">Hypothèse (si résultat affecté au passif)</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Élément</th>
                                    <th style="text-align: right;">Montant (FCFA)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Résultat Net</td>
                                    <td class="montant-cell" style="color: {'#4caf50' if resultat_net >= 0 else '#f44336'};">{format_montant(resultat_net)}</td>
                                </tr>
                                <tr>
                                    <td>Passif + Résultat</td>
                                    <td class="montant-cell">{format_montant(passif_avec_resultat)}</td>
                                </tr>
                                <tr class="total-row">
                                    <td>Différence (Actif - (Passif + Résultat))</td>
                                    <td class="montant-cell" style="color: {'#4caf50' if equilibre_apres else '#f44336'};">{format_montant(difference_apres)}</td>
                                </tr>
                                <tr>
                                    <td><strong>Bilan Équilibré</strong></td>
                                    <td class="montant-cell"><span class="badge {'badge-success' if equilibre_apres else 'badge-danger'}">{'OUI ✓' if equilibre_apres else 'NON ✗'}</span></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="{'success-box' if equilibre_apres else 'warning-box'}" style="margin-top: 20px;">
                            <h4>📌 Recommandation</h4>
                            <p style="margin-top: 10px;"><strong>{recommandation_text}</strong></p>
                            <p style="margin-top: 5px;">{explication_text}</p>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    return html




def generate_etat_8_comptes_sens_anormal_n(controles: Dict) -> str:
    """8. Comptes avec Sens Anormal par Nature (Exercice N)"""
    comptes_sens_anormal = controles.get('comptes_sens_anormal', {})
    critiques = comptes_sens_anormal.get('critiques', [])
    eleves = comptes_sens_anormal.get('eleves', [])
    moyens = comptes_sens_anormal.get('moyens', [])
    faibles = comptes_sens_anormal.get('faibles', [])
    
    nb_critiques = len(critiques)
    nb_total = nb_critiques + len(eleves) + len(moyens) + len(faibles)
    
    if nb_total == 0:
        return """
            <!-- 8. Comptes avec Sens Anormal par Nature -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🚨 8. Comptes avec Sens Anormal par Nature (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="success-box">
                            <h3>✅ Aucun Compte Anormal <span class="badge badge-success">Parfait</span></h3>
                            <p style="margin-top: 10px;">Tous les comptes ont un sens conforme à leur nature comptable</p>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    # Générer les tableaux par gravité
    def generer_tableau_gravite(comptes, titre, badge_class, badge_text):
        if not comptes:
            return ""
        
        lignes = ""
        for compte in comptes:
            num_compte = compte.get('numero_compte', '')
            nature = compte.get('nature', '')
            intitule = compte.get('intitule', '')
            sens_attendu = compte.get('sens_attendu', '')
            sens_reel = compte.get('sens_reel', '')
            solde_net = compte.get('solde_net', 0)
            
            lignes += f"""
                                <tr>
                                    <td><span class="badge {badge_class}">{badge_text}</span></td>
                                    <td class="ref-cell">{num_compte}</td>
                                    <td>{nature}</td>
                                    <td>{intitule}</td>
                                    <td style="text-align: center;"><span class="badge badge-info">{sens_attendu}</span></td>
                                    <td style="text-align: center;"><span class="badge badge-danger">{sens_reel}</span></td>
                                    <td class="montant-cell">{format_montant(solde_net)}</td>
                                </tr>
"""
        
        return f"""
                        <h3 style="margin-top: 30px; margin-bottom: 15px;">{titre}</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th style="width: 100px;">Gravité</th>
                                    <th>N° Compte</th>
                                    <th>Nature</th>
                                    <th>Intitulé</th>
                                    <th style="text-align: center;">Sens Attendu</th>
                                    <th style="text-align: center;">Sens Réel</th>
                                    <th style="text-align: right;">Solde Net</th>
                                </tr>
                            </thead>
                            <tbody>
{lignes}
                            </tbody>
                        </table>
"""
    
    tableau_critiques = generer_tableau_gravite(critiques, "🔴 Comptes CRITIQUES (Action Immédiate)", "badge-critical", "CRITIQUE")
    tableau_eleves = generer_tableau_gravite(eleves, "🟠 Comptes ÉLEVÉS (Vérification Prioritaire)", "badge-warning", "ÉLEVÉ")
    tableau_moyens = generer_tableau_gravite(moyens, "🟡 Comptes MOYENS (À Vérifier)", "badge-info", "MOYEN")
    tableau_faibles = generer_tableau_gravite(faibles, "⚪ Comptes FAIBLES (Vérification de Routine)", "badge", "FAIBLE")
    
    return f"""
            <!-- 8. Comptes avec Sens Anormal par Nature -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🚨 8. Comptes avec Sens Anormal par Nature (Exercice N)</span>
                    <span class="arrow">›</span>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="danger-box">
                            <h3>🚨 {nb_critiques} Comptes CRITIQUES Détectés <span class="badge badge-critical">Action Immédiate</span></h3>
                            <p style="margin-top: 10px;">Ces comptes ont un sens contraire à leur nature comptable spécifique</p>
                        </div>
{tableau_critiques}
{tableau_eleves}
{tableau_moyens}
{tableau_faibles}
                        <div class="info-box" style="margin-top: 30px;">
                            <h4>📌 Niveaux de Gravité</h4>
                            <table style="width: 100%; margin-top: 10px;">
                                <thead>
                                    <tr>
                                        <th>Niveau</th>
                                        <th>Impact</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><span class="badge badge-critical">CRITIQUE</span></td>
                                        <td>Déséquilibre majeur</td>
                                        <td>Correction immédiate requise</td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge badge-warning">ÉLEVÉ</span></td>
                                        <td>Anomalie comptable</td>
                                        <td>Vérification et correction prioritaire</td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge badge-info">MOYEN</span></td>
                                        <td>À vérifier</td>
                                        <td>Analyse et justification nécessaire</td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge" style="background: #9e9e9e; color: white;">FAIBLE</span></td>
                                        <td>Situation exceptionnelle possible</td>
                                        <td>Vérification de routine</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
"""



def generate_all_16_etats_controle_html(controles_n: Dict, controles_n1: Dict, totaux_n: Dict, totaux_n1: Dict) -> str:
    """
    Génère les 16 états de contrôle exhaustifs (8 pour N + 8 pour N-1)
    
    Args:
        controles_n: Résultats des contrôles pour l'exercice N
        controles_n1: Résultats des contrôles pour l'exercice N-1
        totaux_n: Totaux pour l'exercice N
        totaux_n1: Totaux pour l'exercice N-1
    
    Returns:
        HTML complet des 16 états de contrôle
    """
    html_parts = []
    
    # États 1-8 pour N
    html_parts.append(generate_etat_1_statistiques_couverture_n(controles_n))
    html_parts.append(generate_etat_2_equilibre_bilan_n(controles_n, totaux_n))
    html_parts.append(generate_etat_3_coherence_resultat_n(controles_n, totaux_n))
    html_parts.append(generate_etat_4_comptes_non_integres_n(controles_n))
    html_parts.append(generate_etat_5_comptes_sens_inverse_n(controles_n))
    html_parts.append(generate_etat_6_comptes_desequilibre_n(controles_n))
    html_parts.append(generate_etat_7_hypothese_affectation_n(controles_n, totaux_n))
    html_parts.append(generate_etat_8_comptes_sens_anormal_n(controles_n))
    
    # États 9-16 pour N-1 (mêmes fonctions avec données N-1)
    # On réutilise les mêmes fonctions en changeant juste les numéros dans le HTML
    html_n1_1 = generate_etat_1_statistiques_couverture_n(controles_n1).replace("1. Statistiques", "9. Statistiques").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_2 = generate_etat_2_equilibre_bilan_n(controles_n1, totaux_n1).replace("2. Équilibre", "10. Équilibre").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_3 = generate_etat_3_coherence_resultat_n(controles_n1, totaux_n1).replace("3. Cohérence", "11. Cohérence").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_4 = generate_etat_4_comptes_non_integres_n(controles_n1).replace("4. Comptes Non", "12. Comptes Non").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_5 = generate_etat_5_comptes_sens_inverse_n(controles_n1).replace("5. Comptes avec Sens", "13. Comptes avec Sens").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_6 = generate_etat_6_comptes_desequilibre_n(controles_n1).replace("6. Comptes Créant", "14. Comptes Créant").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_7 = generate_etat_7_hypothese_affectation_n(controles_n1, totaux_n1).replace("7. Hypothèse", "15. Hypothèse").replace("(Exercice N)", "(Exercice N-1)")
    html_n1_8 = generate_etat_8_comptes_sens_anormal_n(controles_n1).replace("8. Comptes avec Sens Anormal", "16. Comptes avec Sens Anormal").replace("(Exercice N)", "(Exercice N-1)")
    
    html_parts.extend([html_n1_1, html_n1_2, html_n1_3, html_n1_4, html_n1_5, html_n1_6, html_n1_7, html_n1_8])
    
    return "\n".join(html_parts)
