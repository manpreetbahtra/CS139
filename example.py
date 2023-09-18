from flask import Flask, request, render_template_string
app = Flask(__name__)


@app.route("/")
@app.route("/example", methods=['POST', 'GET'])
def example():
    output = "No output"
    method = None
    if request.method == "POST":
        output = request.form['user_input']
        method = int(request.form['method'])
    return render_template_string(webpage, output=output, method=method)

webpage = """

<!DOCTYPE html>
<html>
<head>
	
</head>
<body>
	<h1>XSS Testbed</h1>
	<p>This testbed is designed to demonstrate the usage of Flask's functions for preventing XSS attacks.</p>
	
	<form action='/example' method='post'>
		<label for="user_input">User Input</label><br>
		<textarea name='user_input' cols='80' rows='10'>
My name is BETTE. 
<script>
	alert("This should not run!");
	alert("Seriously!");	
</script>
{% raw %}
{{ variables go here in Flask/Jinja templates }}
{% endraw %}
Goodbye.
		</textarea>
		<br>
		<label>Flask Method</label><br>
		<input type="radio" name="method" value = 1 id="strip">Using <a href = "https://jinja.palletsprojects.com/en/3.0.x/templates/#jinja-filters.striptags"> striptags</a> filter</input><br>
		<input type="radio" name="method"  value = 2 id="escape">Using <a href = "https://jinja.palletsprojects.com/en/3.0.x/templates/#jinja-filters.escape"> escape</a> filter</input><br>
		<input type="radio" name="method" value = 3 id="normal">normal autoescape</input><br>
		<input type="radio" name="method" value = 4 id="disabled">disabled autoescape (using <a href="https://jinja.palletsprojects.com/en/3.0.x/templates/#autoescape-overrides">override</a>) </input><br>
		<input type="radio" name="method" value = 5 id="none" checked>No XSS Protection</input><br>
		<input type="submit" name="Submit" value="Submit Data" id="Submit">
	</form>

            
	
	
    {% if method %}
	    <h2>Flask Output</h2>
        {% if method == 1 %}
            Using <a href = "https://jinja.palletsprojects.com/en/3.0.x/templates/#jinja-filters.striptags"> striptags</a> filter<br>
            {{ output | striptags }}
        {% elif method == 2 %}
            Using <a href = "https://jinja.palletsprojects.com/en/3.0.x/templates/#jinja-filters.escape"> escape</a> filter<br>
            {{ output | escape }}
        {% elif method == 3 %}
            Normal autoescape<br>
            {{ output }}
        {% elif method == 4 %}
            No autoescaping (using <a href="https://jinja.palletsprojects.com/en/3.0.x/templates/#autoescape-overrides">override</a>) <br>
            {% autoescape false %}
            {{ output}}
            {% endautoescape %}
        {% elif method == 5 %}
            No XSS Protection<br>
            {{ output | safe }}
        {% endif %}
    {% endif %}



	
</body>
</html>

"""
