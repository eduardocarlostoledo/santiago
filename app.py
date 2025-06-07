from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encuesta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_frecuente = db.Column(db.String(100))
    valoracion = db.Column(db.Integer)
    tipo_contenido = db.Column(db.String(50))
    frecuencia = db.Column(db.String(50))


from flask import redirect, url_for

@app.route('/borrar-datos', methods=['POST'])
def borrar_datos():
    clave = request.form.get('clave')
    if clave != 'toledo123':
        return "Clave incorrecta", 403
    db.session.query(Respuesta).delete()
    db.session.commit()
    return redirect(url_for('encuesta'))  # 👈 redirige al componente de encuesta




@app.route('/respuestas')
def ver_respuestas():
    respuestas = Respuesta.query.all()

    apps = [r.app_frecuente for r in respuestas]
    valoraciones = [r.valoracion for r in respuestas]

    conteo_apps = Counter(apps)
    
    # Ordenar de mayor a menor directamente acá
    ranking_apps = dict(sorted(conteo_apps.items(), key=lambda x: x[1], reverse=True))

    app_mas_votada = next(iter(ranking_apps), None)
    promedio_valoracion = round(sum(valoraciones) / len(valoraciones), 2) if valoraciones else 0

    return render_template(
        'respuestas.html',
        respuestas=respuestas,
        app_mas_votada=app_mas_votada,
        promedio_valoracion=promedio_valoracion,
        ranking_apps=ranking_apps
    )

@app.route('/', methods=['GET', 'POST'])
def encuesta():
    if request.method == 'POST':
        nueva_respuesta = Respuesta(
            app_frecuente=request.form['app_frecuente'],
            valoracion=int(request.form['valoracion']),
            tipo_contenido=request.form['tipo_contenido'],
            frecuencia=request.form['frecuencia']
        )
        db.session.add(nueva_respuesta)
        db.session.commit()
        recomendacion = recomendar_app(
            nueva_respuesta.tipo_contenido,
            nueva_respuesta.frecuencia
        )
        return render_template('gracias.html', 
                               app=nueva_respuesta.app_frecuente,
                               recomendacion=recomendacion)
    
    return render_template('encuesta.html')
def recomendar_app(tipo_contenido, frecuencia):
    if tipo_contenido == 'Videos':
        if frecuencia in ['Varias veces al día', 'Una vez al día']:
            return 'TikTok o YouTube'
        else:
            return 'YouTube'
    elif tipo_contenido == 'Imágenes':
        return 'Instagram o Pinterest'
    elif tipo_contenido == 'Texto':
        return 'Twitter (ahora X) o Reddit'
    elif tipo_contenido == 'Combinado':
        return 'Facebook o Instagram'
    else:
        return 'Explorá nuevas apps como BeReal o Threads'

if __name__ == '__main__':
    with app.app_context():  # Agrega esta línea
        if not os.path.exists('encuesta.db'):
            db.create_all()
    app.run(debug=True)
