from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('input.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Get user input from form
    index = request.form.get('index')
    description = request.form.get('description')

    # Placeholder for ChatGPT API call (to be replaced with API logic)
    professional_version = f"Processed: {description}"  # Mock result

    return render_template('output.html', index=index, result=professional_version)

if __name__ == '__main__':
    app.run(debug=True)
