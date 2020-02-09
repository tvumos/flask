from flask import Flask, render_template, request
import model
from parsing import create_cash_files, get_result
from os import path
import json
from flask_wtf import Form
from wtforms import SelectField
import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = model.UII

class FormRegionsUiks(Form):
    regions = SelectField(u'Выберите регион: ')
    uiks = SelectField(u'Выберите УИК:')

    def __init__(self, *args, **kwargs):
        super(FormRegionsUiks, self).__init__(*args, **kwargs)
        with open(model.FILE_NAME_REGION, "r") as read_file:
            regions_list = json.load(read_file)

        self.regions.choices = [(name, u"%s" % name) for name, url in regions_list.items()]
        #  выбранное поле по умолчанию
        self.regions.choices.insert(0, (u"None", u"Не выбрано"))

        self.uiks.choices = list()
        #  выбранное поле по умолчанию
        self.uiks.choices.insert(0, (u"None", u"Не выбрано"))


@app.route("/")
@app.route('/index')
def index():
    if not path.isfile(model.FILE_NAME_REGION) or not path.isfile(model.FILE_NAME_UIK):
        create_cash_files()
    # return render_template('index.html', user=user, url_msk=url_msk, **context)
    return render_template('index.html', url_msk=model.URL_MSK, uii=model.UII, uii_url=model.UII_URL)


@app.route('/contacts/')
def contacts():
    return render_template('contact.html', creation_date=model.DATA_CREATION,
                           fio=model.FIO, email=model.EMAIL, city=model.CITY,
                           uii=model.UII, uii_url=model.UII_URL)


@app.route('/form/')
def forms():
    form = FormRegionsUiks()
    return render_template('form.html', form=form, uii=model.UII, uii_url=model.UII_URL)


@app.route('/result/', methods=['GET', 'POST'])
def results():
    region_key = request.form['regions']
    uik_key = request.form['uiks']
    with open(model.FILE_NAME_UIK, "r") as read_file:
        uiks = json.load(read_file)
    uik_list = uiks[region_key]
    url = ""
    for temp_uik in uik_list:
        if temp_uik[0] == uik_key:
            url = temp_uik[1]
            break
    list_result = get_result(url)
    # pprint.pprint(list_result)
    return render_template('result.html', list_result=list_result, region=region_key, uik=uik_key,
                           uii=model.UII, uii_url=model.UII_URL)


@app.route('/get_uik', methods=('GET', 'POST'))
def get_uiks():
    region_key = request.form['regions']
    with open(model.FILE_NAME_UIK, "r") as read_file:
        uiks = json.load(read_file)
    dict_uiks = {}
    list_uik = uiks[region_key]
    for uik in list_uik:
        dict_uiks[uik[0]] = uik[0]
    return json.dumps(dict_uiks)


if __name__ == "__main__":
    app.run(debug=True)