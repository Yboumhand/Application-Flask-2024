from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

#--------------------------------------------------Initialisation de l'application Flask-------------------------------------------------

app = Flask(__name__)
app.secret_key = 'password123'

#--------------------------------------------------Importer la configuration--------------------------------------------------

import config


#--------------------------------------------------Connexion à la base de données--------------------------------------------------

connection = pymysql.connect(
    host=config.MYSQL_HOST,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    database=config.MYSQL_DB
)


#--------------------------------------------------Route pour la page d'accueil--------------------------------------------------

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

#--------------------------------------------------Route pour afficher les avions enregistrés--------------------------------------------------


@app.route('/avions', methods=['GET'])
def gestion_avions():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "SELECT NUMAV, TYPAV, DATE_FORMAT(DATMS, '%Y-%m-%d') AS DATMS, NBHDDREV, STATUTAVION FROM AVION"
            cursor.execute(query)
            avions = cursor.fetchall()
        return render_template('avion.html', avions=avions)
    except Exception as e:
        flash("Erreur lors de la récupération des données : " + str(e), "danger")
        return render_template('avion.html', avions=[])


#--------------------------------------------------Route pour ajouter un avion--------------------------------------------------


@app.route('/ajouter_avion', methods=['GET', 'POST'])
def ajouter_avion():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        numav = request.form.get('NUMAV')
        typav = request.form.get('TYPAV')
        datms = request.form.get('DATMS')
        nbhddrev = request.form.get('NBHDDREV')
        statutavion = request.form.get('STATUTAVION')

        # Validation des données côté serveur
        if not (numav and typav and datms and nbhddrev and statutavion):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template('ajouter_avion.html', data=request.form)

        try:
            nbhddrev = int(nbhddrev)  # Vérification que NBHDDREV est un entier
            if nbhddrev < 0:
                raise ValueError("Le nombre d'heures depuis la dernière révision doit être positif.")
        except ValueError as ve:
            flash(str(ve), "danger")
            return render_template('ajouter_avion.html', data=request.form)

        try:
            with connection.cursor() as cursor:
                # Insertion des données dans la table AVION
                query = """
                INSERT INTO AVION (NUMAV, TYPAV, DATMS, NBHDDREV, STATUTAVION)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (numav, typav, datms, nbhddrev, statutavion))
                connection.commit() 
                flash(f"L'avion {numav} est ajouté avec succès !", "success")
                return redirect('/avions')  # Redirige vers la liste des avions
        except Exception as e:
            connection.rollback()  # Annuler la transaction en cas d'erreur
            flash("Erreur lors de l'ajout de l'avion : " + str(e), "danger")
            return render_template('ajouter_avion.html', data=request.form)
    else:
        # Affichage du formulaire pour ajouter un avion
        return render_template('ajouter_avion.html', data={})


#--------------------------------------------------Route pour modifier un avion--------------------------------------------------


@app.route('/avions/modifier/<numav>', methods=['GET', 'POST'])
def modifier_avion(numav):
    if request.method == 'POST':
        nbhddrev = request.form['nbhddrev']
        statutavion = request.form['statutavion']

        try:
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE AVION SET NBHDDREV = %s, STATUTAVION = %s WHERE NUMAV = %s",
                    (nbhddrev, statutavion, numav)
                )
                connection.commit()
                flash("Avion modifié avec succès!", 'success')
                return redirect(url_for('list_avions'))
        except Exception as e:
            flash(f"Erreur: {e}", 'danger')
        finally:
            connection.close()

    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AVION WHERE NUMAV = %s", (numav,))
            avion = cursor.fetchone()
        return render_template('modifier_avion.html', avion=avion)
    except Exception as e:
        flash(f"Erreur: {e}", 'danger')
        return redirect(url_for('list_avions'))
    finally:
        connection.close()

#--------------------------------------------------Route pour supprimer un avion--------------------------------------------------


@app.route('/avions/supprimer/<NUMAV>', methods=['POST'])
def supprimer_avion(NUMAV):
    try:
        with connection.cursor() as cursor:
            # Exécuter la suppression
            rows_affected = cursor.execute("DELETE FROM avion WHERE NUMAV = %s", (NUMAV,))
            connection.commit()
        
        # Vérifier si la suppression a eu lieu
        if rows_affected > 0:
            flash(f"L'avion {NUMAV} est supprimé avec succès !", "success")
        else:
            flash(f"L'avion {NUMAV} à supprimer n'existe pas.", "warning")
    except pymysql.MySQLError as e:
        # En cas d'erreur SQL
        flash(f"Erreur lors de la suppression de l'avion {NUMAV} : {str(e)}", "danger")
    return redirect(url_for('gestion_avions'))



#--------------------------------------------------Route pour afficher les vols enregistrés--------------------------------------------------


@app.route('/vols', methods=['GET'])
def gestion_vols():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "SELECT NUMVOL, VILDEP, VILARR, HDEP, DURVOL, STATUTVOL FROM vol"
            cursor.execute(query)
            vols = cursor.fetchall()
        return render_template('vol.html', vols=vols)
    except Exception as e:
        flash("Erreur lors de la récupération des données : " + str(e), "danger")
        return render_template('vol.html', vols=[])

#--------------------------------------------------Route pour ajouter un vol--------------------------------------------------


@app.route('/ajouter_vol', methods=['GET', 'POST'])
def ajouter_vol():
    if request.method == 'POST':
        try:
            num_vol = request.form['NUMVOL']
            depart = request.form['VILDEP']
            arrivee = request.form['VILARR']
            heure_depart = request.form['HDEP']
            duree_vol = request.form['DURVOL']
            statut_vol = request.form['STATUTVOL']
            num_avion = request.form['NUMAV']

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO vol (NUMVOL, VILDEP, VILARR, HDEP, DURVOL, STATUTVOL, NUMAV)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (num_vol, depart, arrivee, heure_depart, duree_vol, statut_vol, num_avion))
                connection.commit()

            flash(f"Le vol {num_vol} est ajouté avec succès !", "success")
            return redirect('/vols')
        except Exception as e:
            flash(f"Erreur lors de l'ajout du vol {num_vol} : {str(e)}", "danger")
            return redirect('/ajouter_vol')
    
    return render_template('ajouter_vol.html')


#--------------------------------------------------Route pour modifier un vol--------------------------------------------------

@app.route('/vols/modifier/<int:NUMVOL>', methods=['GET', 'POST'])
def modifier_vol(NUMVOL):
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                # Récupérer les données du formulaire
                ville_depart = request.form['VILDEP']
                ville_arrivee = request.form['VILARR']
                heure_depart = request.form['HDEP']
                duree_vol = request.form['DURVOL']
                statut_vol = request.form['STATUTVOL']
                num_avion = request.form['NUMAV']

                # Exécuter la mise à jour
                rows_affected = cursor.execute("""
                    UPDATE vol
                    SET VILDEP = %s, VILARR = %s, HDEP = %s, DURVOL = %s, STATUTVOL = %s, NUMAV = %s
                    WHERE NUMVOL = %s
                """, (ville_depart, ville_arrivee, heure_depart, duree_vol, statut_vol, num_avion, NUMVOL))
                connection.commit()

                # Vérifier si la mise à jour a eu lieu
                if rows_affected > 0:
                    flash(f"Le vol {NUMVOL} a été modifié avec succès !", "success")
                else:
                    flash(f"Le vol {NUMVOL} à modifier n'existe pas.", "warning")
                return redirect(url_for('gestion_vols'))
            else:
                # Récupérer les informations du vol à modifier
                cursor.execute("SELECT * FROM vol WHERE NUMVOL = %s", (NUMVOL,))
                vol = cursor.fetchone()
                if vol is None:
                    flash("Vol introuvable", "danger")
                    return redirect(url_for('gestion_vols'))
                return render_template('modifier_vol.html', vol=vol)
    except pymysql.MySQLError as e:
        # En cas d'erreur SQL
        flash(f"Erreur lors de la modification du vol : {str(e)}", "danger")
        return redirect(url_for('gestion_vols'))



#--------------------------------------------------Route pour supprimer un vol--------------------------------------------------

@app.route('/vols/supprimer/<NUMVOL>', methods=['POST'])
def supprimer_vol(NUMVOL):
    try:
        with connection.cursor() as cursor:
            # Exécuter la suppression
            rows_affected = cursor.execute("DELETE FROM vol WHERE NUMVOL = %s", (NUMVOL,))
            connection.commit()
        
        # Vérifier si la suppression a eu lieu
        if rows_affected > 0:
            flash(f"Le vol {NUMVOL} est supprimé avec succès !", "success")
        else:
            flash(f"Le vol {NUMVOL} à supprimer n'existe pas.", "warning")
    except pymysql.MySQLError as e:
        # En cas d'erreur SQL
        flash(f"Erreur lors de la suppression du vol : {str(e)}", "danger")
    return redirect(url_for('gestion_vols'))


#--------------------------------------------------Lancement de l'application Web--------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)


