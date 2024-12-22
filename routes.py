# from flask import Blueprint, render_template, request, redirect, url_for, flash
# import pymysql
# from config import connection

# # Définir un Blueprint
# routes = Blueprint('routes', __name__)

# # Route pour la page d'accueil
# @routes.route('/')
# @routes.route('/home')
# def index():
#     return render_template('index.html')

# # Route pour afficher la liste des avions
# @routes.route('/avions')
# def list_avions():
#     avions = Avion.query.all()  # Récupérer tous les avions de la base de données
#     return render_template('list_avions.html', avions=avions)

# # Route pour afficher les vols
# @routes.route('/vols', methods=['GET'])
# def gestion_vols():
#     try:
#         with connection.cursor(pymysql.cursors.DictCursor) as cursor:
#             query = "SELECT NUMVOL, VILDEP, VILARR, HDEP, DURVOL, STATUTVOL FROM vol"
#             cursor.execute(query)
#             vols = cursor.fetchall()
#         return render_template('vol.html', vols=vols)
#     except Exception as e:
#         print("Erreur lors de la récupération des données :", e)
#         return "Erreur lors de la récupération des vols", 500

# # Route pour ajouter un vol
# @routes.route('/ajouter_vol', methods=['GET', 'POST'])
# def ajouter_vol():
#     if request.method == 'POST':
#         num_vol = request.form['NUMVOL']
#         depart = request.form['VILDEP']
#         arrivee = request.form['VILARR']
#         heure_depart = request.form['HDEP']
#         duree_vol = request.form['DURVOL']
#         statut_vol = request.form['STATUTVOL']
#         num_avion = request.form['NUMAV']
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO vol (NUMVOL, VILDEP, VILARR, HDEP, DURVOL, STATUTVOL, NUMAV) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                 (num_vol, depart, arrivee, heure_depart, duree_vol, statut_vol, num_avion),
#             )
#             connection.commit()
#         return redirect('/vols')
#     return render_template('ajouter_vol.html')

# # Route pour modifier un vol
# @routes.route('/vols/modifier/<string:NUMVOL>', methods=['GET', 'POST'])
# def modifier_vol(NUMVOL):
#     if request.method == 'POST':
#         try:
#             vildep = request.form['VILDEP']
#             vilarr = request.form['VILARR']
#             hdep = request.form['HDEP']
#             durvol = request.form['DURVOL']
#             statutvol = request.form['STATUTVOL']
#             numav = request.form['NUMAV']
#             with connection.cursor() as cursor:
#                 query = """
#                     UPDATE vol
#                     SET VILDEP = %s, VILARR = %s, HDEP = %s, DURVOL = %s, STATUTVOL = %s, NUMAV = %s
#                     WHERE NUMVOL = %s
#                 """
#                 cursor.execute(query, (vildep, vilarr, hdep, durvol, statutvol, numav, NUMVOL))
#                 connection.commit()
#             return redirect(url_for('routes.gestion_vols'))
#         except Exception as e:
#             print("Erreur :", e)
#             return "Erreur lors de la mise à jour du vol.", 400
#     else:
#         with connection.cursor(pymysql.cursors.DictCursor) as cursor:
#             query = "SELECT * FROM vol WHERE NUMVOL = %s"
#             cursor.execute(query, (NUMVOL,))
#             vol = cursor.fetchone()
#         if not vol:
#             return "Vol introuvable.", 404
#         return render_template('modifier_vol.html', vol=vol)

# # Route pour supprimer un vol
# @routes.route('/vols/supprimer/<NUMVOL>', methods=['POST'])
# def supprimer_vol(NUMVOL):
#     with connection.cursor() as cursor:
#         cursor.execute("DELETE FROM vol WHERE NUMVOL = %s", (NUMVOL,))
#         connection.commit()
#     flash("Vol supprimé avec succès !")
#     return redirect(url_for('routes.gestion_vols'))
