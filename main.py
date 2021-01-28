from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
import datetime
import os, csv, uuid
import re
from optimize import bipartite_optimize_iterated 

# 
#########
# Links #
#########
app = Flask(__name__)
@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory('output', filename)
@app.route('/playback')
def play_wav():
    uuid_str = request.args.get('uuid')
    return render_template("playback.html", uuid=uuid_str)
@app.route('/names', methods=['GET', 'POST'])
def names():
    return render_template("names.html") 
@app.route('/compatibility', methods=['GET', 'POST'])
def compat():
    males, females = extract_names(dict(request.form))
    return render_template("compatibility.html", males=males, females=females) 
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        type_str = request.form.get('type')
        print(type_str)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            uuid_str = uuid.uuid1().hex
            filename = secure_filename(uuid_str + '.csv')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            input_data = parse_input('uploads/' + uuid_str + '.csv')
            output_file = 'output/' + uuid_str + '.midi'
            write_midi(input_data, output_file, mode=type_str)
            process_midi(output_file, play=False, output_wav='output/' + uuid_str + '.wav')
            return redirect('/playback?uuid=' + uuid_str)
    return render_template("home.html")


def extract_names(form_dict):
    N = int(len(form_dict) / 2)
    males = [""] * N
    females = [""] * N

    for key, value in form_dict.items():
        index = int(re.search(r"\[([0-9]+)\]", key).group(1))
        if key.startswith("female"):
            females[index] = value
        else:
            males[index] = value
    return males, females
if __name__ == '__main__':
    app.run(debug=True)
