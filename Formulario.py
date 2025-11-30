import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Formulario.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    email = request.form['email']
    return f'Nome: {nome}, E-mail: {email}'


if __name__ == '__main__':
    app.run(debug=True)



