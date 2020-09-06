from .config import url_api, server_api
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, escape
)
from flask import render_template, flash, redirect, url_for
#from flask_login import current_user, login_user, logout_user, login_required
#from flask_login import current_user, login_required, login_user, logout_user
from .forms import LoginForm, UploadGmlForm, VerifyGmlForm, VerifyAttributeForm, VerifyPhotoForm, VerifyVideoForm
#from .decorator import from login_verifikator_required
from werkzeug import secure_filename
#from .models import User
#from app import login_manager

import requests, os, subprocess

bp = Blueprint('home', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/data/uploads')
UPLOAD_PHOTO_FOLDER = os.path.join(APP_ROOT, 'static/data/photos')
UPLOAD_VIDEO_FOLDER = os.path.join(APP_ROOT, 'static/data/videos')
VERIFIED_FOLDER = os.path.join(APP_ROOT, 'static/data/verified')

ALLOWED_PHOTO_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4'])

def allowed_photo_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS

def allowed_video_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

@bp.route('/')
@bp.route('/home')
def welcome():
    return render_template('welcome.html', url_api=url_api)
	
@bp.route('/about')
def about():
    return render_template('about.html', url_api=url_api)

@bp.route('/login',methods=['GET', 'POST'])
def login():
	if 'username' in session:
		return redirect(url_for('home.contributor'))
	
	form = LoginForm()
	if form.validate_on_submit():
		#print(form.username.data)
		#print(type(form.username.data))
		#print(form.password.data)
		data = {
			"username":form.username.data, 
			"password":form.password.data
		}
		# sending post request and saving response as response object 
		r = requests.post(url = server_api+'auth/login', json = data)
		#print(r.json())
		#print(r.status_code)
		#print(r.text)
		a = r.json()
		#print(a["status"])
		if r is not None:
			if r.status_code == 200:
				session['Authorization'] = a["Authorization"]
				session['username'] = a["username"]
				session['public_id'] = a["public_id"]
				session['type_id'] = a["type_id"]
				session['area_id'] = a["area_id"]
				if (a["type_id"] < 3):
					return redirect(url_for('home.contributor'))
				else:
					return redirect(url_for('home.validator'))
				
				'''user = User(a["username"], a["id"])
				print(user)
				if login_user(user):
					#flash("Logged in!")
					return redirect(url_for('home.contributor'))
					#return redirect(url_for('home.login'))
				else:
					flash("Sorry, but you could not log in.")
					return redirect(url_for('home.login'))
				'''
			else:
				flash('User/password is not valid')
				return redirect(url_for('home.login'))
		else:
			flash('User/password is not valid')
			return redirect(url_for('home.login'))
	return render_template('login.html', form=form)
'''
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.login'))
'''
@bp.route('/logout')
def logout():
    # remove the username from the session if it's there
	headers = {'Authorization': session['Authorization']}
	r = requests.post(url = server_api+'auth/logout', headers=headers)
	print(r)
	session.pop('Authorization', None)
	session.pop('username', None)
	session.pop('public_id', None)
	session.pop('type_id', None)
	session.pop('area_id', None)
	#send to logout API to set Authorization as expired
	#eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1OTUxOTk5MTUsImlhdCI6MTU5NTExMzUxMCwic3ViIjoiMTk4YTllZTItOGE4Ny00N2I1LTkwNzYtMzU5MTVkMGQ4MDAxIn0.cGe-K7qbpxBZXiRN2VfnK2t_Qv0Bh59GU-CnR0vrbuM
	return redirect(url_for('home.login'))
	
@bp.route('/forgot')
def forgot():
    return render_template('forgot.html', url_api=url_api)

@bp.route('/register')
def register():
    return render_template('register.html', url_api=url_api)

@bp.route('/contributor')
#@login_required
def contributor():
	#print(current_user.is_authenticated)
	if 'username' in session:
		if session['type_id'] < 3:
			return render_template('contributor.html', url_api=url_api)
	else:
		return redirect(url_for('home.login'))	


@bp.route('/upload_gml', methods=['GET', 'POST'])
#@login_required
def upload_gml():
	#print(current_user.is_authenticated)
	if 'username' in session:
		form = UploadGmlForm()
		if request.method == 'POST':
			if form.validate_on_submit():
				print(form.file)
				print(form.file.data)
				filename = secure_filename(form.file.data.filename)
				print(type(filename))
				filename = session['username'] + "_" + filename
				
				#send to database
				data = {
					"contributor":session['username'], 
					"city_gml_file":filename,
					"area_id":session['area_id']
				}
				headers = {'Authorization': session['Authorization']}
				# sending post request and saving response as response object 
				r = requests.post(url = server_api+'city_gml/', json = data, headers=headers)
				print(r.json())
				#print(r.status_code)
				print(r.text)
				a = r.json()
				#print(a["status"])
				if r is not None:
					if r.status_code == 201:
						flash('Your file has been uploaded successfully')
						form.file.data.save(UPLOAD_FOLDER + "/" + filename)
						return redirect(url_for('home.upload_gml'))
					else:
						flash("Status: " + a["status"] + ' : ' + a["message"])
						return redirect(url_for('home.upload_gml'))
				else:
					flash('Can not connect to API')
					return redirect(url_for('home.upload_gml'))
				#print(form.password.data)
				#data = {
				#	"building":form.username.data, 
				#	"password":form.password.data
				#}
		return render_template('upload_gml.html', url_api=url_api, form=form)
	else:
		return redirect(url_for('home.login'))	

def login_validator():
	if 'username' in session:
		if session['type_id'] == 3:
			return True
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))
		
@bp.route('/validator')
#@login_verifikator_required
def validator():
	#print(current_user.is_authenticated)
	#if login_validator():
	#	return render_template('validator.html', url_api=url_api)
	
	if 'username' in session:
		if session['type_id'] == 3:
			return render_template('validator.html', url_api=url_api)
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))	

@bp.route('/test_validate')
def test_validate():
	#/impexp/bin/3DCityDB-Importer-Exporter -shell –config /share/config/config_export_kml.xml -validate /opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-validate', '/opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml'], stdout=subprocess.PIPE)
	#return "test_export " + result.stdout.decode('utf-8')
	return validate_gml("muhammad.hasannudin_3dbldglod2_itb_labtek.gml")

def validate_gml(filename):
	result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-validate', '/opt/code/app/static/data/verified/'+filename], stdout=subprocess.PIPE)
	return result.stdout.decode('utf-8')
	
@bp.route('/test_import')
def test_import():
	#/impexp/bin/3DCityDB-Importer-Exporter -shell –config /share/config/config_export_kml.xml -validate /opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-validate', '/opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml'], stdout=subprocess.PIPE)
	#return "test_export " + result.stdout.decode('utf-8')
	#filename = "muhammad.hasannudin_3dbldglod2_itb_labtek.gml"
	filename = "muhammad.hasannudin_3dbldglod2_itb_octagon.gml"
	v = validate_gml(filename)
	if "is valid" in v:
		#trigger export import to 3dcitydb
		print(v)
		print("imported")
		r = import_gml(filename)
		if "ERROR" in r:
			print("error imported")
			return("error imported")
		else:
			return r
	else:
		print("not valid")
		return("not valid")
	#return import_gml("muhammad.hasannudin_3dbldglod2_itb_labtek.gml")

def import_gml(filename):
	result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-import', '/opt/code/app/static/data/verified/'+filename], stdout=subprocess.PIPE)
	return result.stdout.decode('utf-8')

@bp.route('/test_export')
def test_export():
	#/impexp/bin/3DCityDB-Importer-Exporter -shell –config /share/config/config_export_kml.xml -validate /opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-version'], stdout=subprocess.PIPE)
	#result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/config_export_kml.xml', '-validate', '/opt/code/app/static/data/verified/muhammad.hasannudin_3dbldglod2_itb_labtek.gml'], stdout=subprocess.PIPE)
	#return "test_export " + result.stdout.decode('utf-8')
	#generate config_file to dinamically change
	#return export_gml("config_export_kml.xml", "muhammad.hasannudin_3dbldglod2_itb_labtek.gml")
	#return export_gml("config_export_kml.xml", "yusa.tuberlin_3DBuildingSchemaLOD2_itb_sabuga.gml")
	#return export_gml("config_export_kml.xml", "muhammad.hasannudin_3dbldglod2_itb_octagon.gml")
	#generate config?
	filename = "yusa.tuberlin_3DBuildingSchemaLOD2_itb_geologi.gml";
	base = os.path.splitext(filename)[0]
	file_xml = '/share/config/' + base + '.xml'
	file_xml_up = '/share/config/config_export_kml_up.txt'
	file_xml_down = '/share/config/config_export_kml_down.txt'
	#print(file_xml)
	
	r = requests.get(url = server_api+'cityobject/limit/' + str(21))
	d = r.json()
	if r is not None:
		if r.status_code == 200:
			c=open(file_xml_up,"r")
			g=open(file_xml_down,"r")
			f=open(file_xml,"w+")
			f.write(c.read())
			for i in d['data']:
				#print(str(i.gmlid))
				f.write("                <id>" + str(i["gmlid"]) + "</id>\n")
				#list_gml_id.append(str(i["gmlid"])
			f.write(g.read())
			f.close()
	arr = os.listdir('/share/config/')
	print(arr)
	return export_gml(base + '.xml')

def export_gml(config):
	#filename = filename.replace("bananas", "apples");
	base = os.path.splitext(config)[0]
	file_kml = base + '.kml'
	print(file_kml)
	#/impexp/bin/3DCityDB-Importer-Exporter -shell -config /share/config/config_export_kml.xml -kmlExport /opt/code/app/static/data/export/kml/bbox2.kml
	result = subprocess.run(['/impexp/bin/3DCityDB-Importer-Exporter', '-shell', '-config', '/share/config/'+config, '-kmlExport', '/opt/code/app/static/data/export/kml/'+file_kml], stdout=subprocess.PIPE)
	#result = subprocess.run(['whoami'], stdout=subprocess.PIPE)
	return result.stdout.decode('utf-8')

@bp.route('/test')
def test():
	gml_id = 1
	r = requests.get(url = server_api+'cityobject/limit/' + str(21))
	d = r.json()
	if r is not None:
		if r.status_code == 200:
			list_gml_id = []
			for i in d['data']:
				#print(str(i.gmlid))
				list_gml_id.append(str(i["gmlid"]))
			data = {
					"list_gml_id":list_gml_id, 
					"city_gml_id":gml_id
				}
			print(data)
			headers = {'Authorization': session['Authorization']}
			r = requests.post(url = server_api+'buildings/', json = data, headers=headers)
			e = r.json()
			if r is not None:
				if r.status_code == 202:
					print('Your review has been saved successfully')
	return "A"
#-kmlExport /share/data/export/kml/bbox.kml	
@bp.route('/check_gml', methods=['GET', 'POST'])
#@login_required
def check_gml():
	id = request.args.get('id')
	#print(request.args)
	#return request.args.get('id')
	
	if 'username' in session:
		if session['type_id'] == 3:
			form = VerifyGmlForm()
			if request.method == 'POST':
				if form.validate_on_submit():
					##user = request.form['nm']
					#flash('Your file has been uploaded successfully')
					#return redirect(url_for('home.check_gml')+"?id="+id)
					#return "POST"
					#send to database
					if int(form.respons.data)+1 == 3: #approved
						#move file city gml to verified
						print("moved")
						filename = form.filename.data
						if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
							os.rename(os.path.join(UPLOAD_FOLDER, filename), os.path.join(VERIFIED_FOLDER, filename))
						#check validitas gml
						#print(type(validate_gml(filename)))
						#if "is valid" in validate_gml(filename):
						#	#trigger export import to 3dcitydb
						#	print("imported")
						#	import_gml(filename)
						v = validate_gml(filename)
						print(v)
						if "is valid" in v:
							#trigger export import to 3dcitydb
							print("imported")
							r = import_gml(filename)
							print(r)
							if "ERROR" in r:
								flash("error imported")
							else:
								#sp = r.split("gen:GenericCityObject: ", 1)
								sp = r.split("bldg:Building: ", 1)
								#print(sp[1])
								number = sp[1].split("\n", 1)
								#print(len(number[0]))
								print(number[0])
								#print(type(number[0]))
								#jumlah = int(number[0])
								#print("jumlah : " + jumlah)
								#return "Okay"
								
								data = {
									"validator":session['username'], 
									"status_id":int(form.respons.data)+1, 
									"reason":form.reason.data,
									"id":int(id)
								}
								headers = {'Authorization': session['Authorization']}
								# sending post request and saving response as response object 
								r = requests.post(url = server_api+'city_gml/verify/', json = data, headers=headers)
								#print(r.json())
								#print(r.status_code)
								print(r.text)
								a = r.json()
								#print(a["status"])
								if r is not None:
									if r.status_code == 202:
										gml_id = form.city_gml_id.data
										r = requests.get(url = server_api+'cityobject/last/'+ number[0])
										d = r.json()
										if r is not None:
											if r.status_code == 200:
												list_gml_id = []
												#filename = "yusa.tuberlin_3DBuildingSchemaLOD2_itb_geologi.gml";
												base = os.path.splitext(filename)[0]
												file_xml = '/share/config/' + base + '.xml'
												file_xml_up = '/share/config/config_export_kml_up.txt'
												file_xml_down = '/share/config/config_export_kml_down.txt'
												#print(file_xml)
												c=open(file_xml_up,"r")
												g=open(file_xml_down,"r")
												f=open(file_xml,"w+")
												f.write(c.read())														
												
												for i in d['data']:
													#print(str(i.gmlid))
													list_gml_id.append(str(i["gmlid"]))
													f.write("                <id>" + str(i["gmlid"]) + "</id>\n")
												f.write(g.read())
												f.close()
												zz = export_gml(base + '.xml')
												print(zz)
												if "ERROR" in zz:
													flash("error generating kml")
												else:
													print("hola")
													data = {
															"list_gml_id":list_gml_id, 
															"city_gml_id":int(gml_id)
														}
													headers = {'Authorization': session['Authorization']}
													r = requests.post(url = server_api+'buildings/', json = data, headers=headers)
													e = r.json()
													#print(e)
													if r is not None:
														if r.status_code == 201:
															#m = requests.get(url = server_api+'/monitoring/attribute/last/'+ sp[1])
															#w = r.json()
															#if m is not None:
															#insert into monitoring?
															print(e)
															flash('Your review has been saved successfully')
										return redirect(url_for('home.check_gml')+"?id="+id)
									else:
										flash("Status: " + a["status"] + ' : ' + a["message"])
										return redirect(url_for('home.check_gml')+"?id="+id)
								else:
									flash('Can not connect to API')
									return redirect(url_for('home.check_gml')+"?id="+id)
								
						else:
							print("not valid")
							flash("not valid")
						return redirect(url_for('home.check_gml')+"?id="+id)
					else:
						#rejected
						data = {
							"validator":session['username'], 
							"status_id":int(form.respons.data)+1, 
							"reason":form.reason.data,
							"id":int(id)
						}
						headers = {'Authorization': session['Authorization']}
						# sending post request and saving response as response object 
						r = requests.post(url = server_api+'city_gml/verify/', json = data, headers=headers)
						#print(r.json())
						#print(r.status_code)
						print(r.text)
						a = r.json()
						#print(a["status"])
						if r is not None:
							if r.status_code == 202:
								flash('Your review has been saved successfully')
								return redirect(url_for('home.check_gml')+"?id="+id)
							else:
								flash("Status: " + a["status"] + ' : ' + a["message"])
								return redirect(url_for('home.check_gml')+"?id="+id)
						else:
							flash('Can not connect to API')
							return redirect(url_for('home.check_gml')+"?id="+id)
			#return "GET"
			print("GET")
			
			return render_template('check_gml.html', id=id, url_api=url_api, form=form)
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))
	#return "test" #render_template('validator.html', url_api=url_api)
	#print(current_user.is_authenticated)

@bp.route('/check_attribute', methods=['GET', 'POST'])
#@login_required
def check_attribute():
	id = request.args.get('id')
	#print(request.args)
	#return request.args.get('id')
	
	if 'username' in session:
		if session['type_id'] == 3:
			form = VerifyAttributeForm()
			if request.method == 'POST':
				if form.validate_on_submit():
					
						data = {
							"validator":session['username'], 
							"status_id":int(form.respons.data)+1, 
							"reason":form.reason.data,
							"id":int(id)
						}
						headers = {'Authorization': session['Authorization']}
						# sending post request and saving response as response object 
						r = requests.post(url = server_api+'monitoring/attribute/verify/', json = data, headers=headers)
						#print(r.json())
						#print(r.status_code)
						print(r.text)
						a = r.json()
						#print(a["status"])
						if r is not None:
							if r.status_code == 202:
								flash('Your review has been saved successfully')
								return redirect(url_for('home.check_attribute')+"?id="+id)
							else:
								flash("Status: " + a["status"] + ' : ' + a["message"])
								return redirect(url_for('home.check_attribute')+"?id="+id)
						else:
							flash('Can not connect to API')
							return redirect(url_for('home.check_attribute')+"?id="+id)			
			return render_template('check_attribute.html', id=id, url_api=url_api, form=form)
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))
	
@bp.route('/check_photo', methods=['GET', 'POST'])
#@login_required
def check_photo():
	id = request.args.get('id')
	#print(request.args)
	#return request.args.get('id')
	
	if 'username' in session:
		if session['type_id'] == 3:
			form = VerifyPhotoForm()
			if request.method == 'POST':
				if form.validate_on_submit():
					
						data = {
							"validator":session['username'], 
							"status_id":int(form.respons.data)+1, 
							"reason":form.reason.data,
							"id":int(id)
						}
						headers = {'Authorization': session['Authorization']}
						# sending post request and saving response as response object 
						r = requests.post(url = server_api+'monitoring/photo/verify/', json = data, headers=headers)
						#print(r.json())
						#print(r.status_code)
						print(r.text)
						a = r.json()
						#print(a["status"])
						if r is not None:
							if r.status_code == 202:
								flash('Your review has been saved successfully')
								return redirect(url_for('home.check_photo')+"?id="+id)
							else:
								flash("Status: " + a["status"] + ' : ' + a["message"])
								return redirect(url_for('home.check_photo')+"?id="+id)
						else:
							flash('Can not connect to API')
							return redirect(url_for('home.check_photo')+"?id="+id)			
			return render_template('check_photo.html', id=id, url_api=url_api, form=form)
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))
		
@bp.route('/check_video', methods=['GET', 'POST'])
#@login_required
def check_video():
	id = request.args.get('id')
	#print(request.args)
	#return request.args.get('id')
	
	if 'username' in session:
		if session['type_id'] == 3:
			form = VerifyVideoForm()
			if request.method == 'POST':
				if form.validate_on_submit():
					
						data = {
							"validator":session['username'], 
							"status_id":int(form.respons.data)+1, 
							"reason":form.reason.data,
							"id":int(id)
						}
						headers = {'Authorization': session['Authorization']}
						# sending post request and saving response as response object 
						r = requests.post(url = server_api+'monitoring/video/verify/', json = data, headers=headers)
						#print(r.json())
						#print(r.status_code)
						print(r.text)
						a = r.json()
						#print(a["status"])
						if r is not None:
							if r.status_code == 202:
								flash('Your review has been saved successfully')
								return redirect(url_for('home.check_video')+"?id="+id)
							else:
								flash("Status: " + a["status"] + ' : ' + a["message"])
								return redirect(url_for('home.check_video')+"?id="+id)
						else:
							flash('Can not connect to API')
							return redirect(url_for('home.check_video')+"?id="+id)			
			return render_template('check_video.html', id=id, url_api=url_api, form=form)
		else:
			return redirect(url_for('home.contributor'))
	else:
		return redirect(url_for('home.login'))
		

@bp.route('/upload_photo', methods=['POST'])
#@login_required
def upload_photo():
	#print(current_user.is_authenticated)
	if 'username' in session:
		if request.method == 'POST':
			#print(request)
			#print(request.files)
			if 'photo_file' not in request.files:
				response_object = {
					'status': 'Fail',
					'message': 'No file part in request.',
				}
				return response_object, 400
	
			files = request.files.getlist('photo_file')
			print(files)
			file = files[0]
			print(file)
			if file and allowed_photo_file(file.filename):
				filename = secure_filename(file.filename)
				print(filename)
				#send to database
				data = {
					"user_id":session['public_id'], 
					"photo_file":filename,
					"gml_id":request.form['gml_id']
				}
				headers = {'Authorization': session['Authorization']}
				# sending post request and saving response as response object 
				r = requests.post(url = server_api+'monitoring/photo', json = data, headers=headers)
				#print(r.status_code)
				print(r.text)
				a = r.json()
				#print(a["status"])
				if r is not None:
					if r.status_code == 201:
						file.save(UPLOAD_PHOTO_FOLDER + "/" + filename)
						response_object = {
								'status': 'Success',
								'message': 'Photo successfully uploaded. It will be verified soon. Check contributor page.',
						}
						return response_object, 201
					else:
						response_object = {
								'status': a["status"],
								'message': a["message"],
						}
						return response_object, 400	
			else:
				response_object = {
								'status': 'Fail',
								'message': 'File type is not allowed',
						}
				return response_object, 400
			
								
	else:
		return redirect(url_for('home.login'))
		

@bp.route('/upload_video', methods=['POST'])
#@login_required
def upload_video():
	#print(current_user.is_authenticated)
	if 'username' in session:
		if request.method == 'POST':
			#print(request)
			#print(request.files)
			if 'video_file' not in request.files:
				response_object = {
					'status': 'Fail',
					'message': 'No file part in request.',
				}
				return response_object, 400
	
			files = request.files.getlist('video_file')
			print(files)
			file = files[0]
			print(file)
			if file and allowed_video_file(file.filename):
				filename = secure_filename(file.filename)
				print(filename)
				#send to database
				data = {
					"user_id":session['public_id'], 
					"video_file":filename,
					"gml_id":request.form['gml_id']
				}
				headers = {'Authorization': session['Authorization']}
				# sending post request and saving response as response object 
				r = requests.post(url = server_api+'monitoring/video', json = data, headers=headers)
				#print(r.status_code)
				print(r.text)
				a = r.json()
				#print(a["status"])
				if r is not None:
					if r.status_code == 201:
						file.save(UPLOAD_VIDEO_FOLDER + "/" + filename)
						response_object = {
								'status': 'Success',
								'message': 'Video successfully uploaded. It will be verified soon. Check contributor page.',
						}
						return response_object, 201
					else:
						response_object = {
								'status': a["status"],
								'message': a["message"],
						}
						return response_object, 400	
			else:
				response_object = {
								'status': 'Fail',
								'message': 'File type is not allowed',
						}
				return response_object, 400
			
								
	else:
		return redirect(url_for('home.login'))