from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    graph = None
    if request.method == 'POST':
        data = request.form.get('data')
        values = [int(x) for x in data.split(',')]

        plt.bar(range(len(values)), values)
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Bar Chart')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        graph = f'<img src="data:image/png;base64,{image_base64}" />'

    return render_template('homepage.html', graph=graph)


if __name__ == '__main__':
    app.run()
