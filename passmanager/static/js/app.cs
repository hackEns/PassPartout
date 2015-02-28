db_url = "/get/" + keyring
db_push = "/save/" + keyring
database = undefined

sjcl.random.startCollectors()

# Compress a message (deflate compression). Returns base64 encoded data.
compress = (message) ->
	Base64.toBase64 (RawDeflate.deflate( Base64.utob(message) ) )

# Compress a message (deflate compression). Returns base64 encoded data.
decompress = (data) ->
	Base64.btou( RawDeflate.inflate( Base64.fromBase64(data)))

# JSON stringify, then encrypt a message with 
cipher = (key, message) ->
	sjcl.encrypt(key, JSON.stringify(message))

# Decrypt message with key, then JSON parse
decipher = (key, data) ->
	JSON.parse(sjcl.decrypt(key, data))


get_url  = (url, feedback, error) ->
	req = new XMLHttpRequest()
	req.open('GET', url, true)
	req.onreadystatechange = (aEvt) ->
		if req.readyState == 4
			if req.status == 200
				feedback req.responseText
			else
				error()
	req.send(null)

random_password = () ->
	Math.random().toString(36).slice(2, 12) + Math.random().toString(36).slice(2, 12)

send_via_post  = (url, data, feedback, error) ->
	req = new XMLHttpRequest()
	req.open('POST', url, true)
	data = "data=" + encodeURIComponent(data)
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.setRequestHeader("Content-length", data.length)
	req.setRequestHeader("Connection", "close")

	req.onreadystatechange = (aEvt) ->
		if req.readyState == 4
			if req.status == 200
				feedback req.responseText
			else
				error()
	req.send(data)

save = (cb) ->
	data = cipher password, window.database
	console.log window.database
	send_via_post db_push, data, (success) ->
			console.log "ok"
			if cb
				cb()
		,
		() ->
			console.log ":("


# Empty the main tag
emptyMain = () ->
	myNode = document.getElementsByTagName("main")[0]
	myNode.removeChild c for c in myNode.children

# Build the main table view
buildTableView = () ->
	main = document.getElementsByTagName("main")[0]
	main.innerHTML = ""

	main.innerHTML += "<p><a href=\"\" id=\"add-a\">New password</a></p>\
				<table>\
					<tr>\
						<th>Site</th>\
						<th>Username</th>\
						<th>Password</th>\
						<th>Edit</th>\
						<th>Delete</th>\
					</tr>
				</table>"
	table = document.querySelector "main table"

	for e in window.database
		l = document.createElement "tr"
		l.innerHTML = "<tr>\
					<td><input readonly name='website' type=\"text\" value=\"" + e.website + "\" /></td>\
					<td><input readonly name='username' type=\"text\" value=\"" + e.username + "\" /></td>\
					<td><input readonly name='password' class='text-hidden' type=\"text\" value=\"" + e.password + "\" /></td>\
					<td><button class=\"edit-a\">Edit</button></td>\
					<td><button class=\"delete-a\">Delete</button></td>\
				</tr>"
		l.edited = false
		for input_element in l.getElementsByTagName("input")
			input_element.addEventListener "keypress", do (l) -> (evt) ->
				if evt.keyCode == 13
					l.getElementsByClassName("edit-a")[0].click()
		l.getElementsByClassName("edit-a")[0].addEventListener "click", do (l,e) -> (evt) ->
			if l.edited
				element.setAttribute("readonly", null) for element in l.getElementsByTagName("input")
				for input in l.getElementsByTagName("input")
					# FIXME: I'm sure there is a way to do this automatically
					if input.name == "website"
						e.website = input.value
					if input.name == "password"
						e.password = input.value
					if input.name == "username"
						e.username = input.value
				btn = this
				save () ->
					btn.innerHTML = "Saved"
					console.log "done"
			else
				element.removeAttribute("readonly") for element in l.getElementsByTagName("input")
				this.innerHTML = "Ok"
			l.edited = !l.edited

		l.getElementsByClassName("delete-a")[0].addEventListener "click", do (l, e) -> (evt) ->
			window.database.splice(window.database.indexOf(e), 1)
			save () ->
				buildTableView()

		table.appendChild l
	
	# New password area
	newpass = document.createElement("tr")
	newpass.innerHTML = "<form>\
			<td><input name='website' type='text' placeholder='Website' /></td>\
			<td><input name='username' type='text' placeholder='Username' /></td>\
			<td><input name='password' type='text' value='" + random_password() + "' /></td>\
			<td><button class=\"add\">Add</button></td>\
		</form>"
	table.appendChild newpass
	newpass.getElementsByClassName("add")[0].addEventListener "click", (evt) ->
		e = {}
		for input in newpass.getElementsByTagName("input")
			if input.name == "website"
				e.website = input.value
			if input.name == "username"
				e.username = input.value
			if input.name == "password"
				e.password = input.value
		console.log(window.database)
		window.database.push(e)
		console.log(window.database)
		save () ->
			buildTableView()
	
	for el in table.getElementsByClassName('text-hidden')
		el.addEventListener 'click', (evt) ->
			this.select()
		el.addEventListener 'dbclick', (evt) ->
			this.select()


	# Bind events
	document.getElementById("add-a").addEventListener "click", (evt) ->
		evt.preventDefault()
		buildAddView()


# Build the add a new password view
buildAddView = () ->
	emptyMain()

	html = "<form>"
	html += "</form>"

	document.getElementsByTagName("main")[0].innerHTML = html



password = null

document.getElementById("main-pass-form").addEventListener "submit", (evt) ->
	evt.preventDefault()

	# Download the passwords database
	get_url db_url, (data) ->
			try
				console.log window.database
				window.database = decipher(document.getElementById("main-pass-input").value, data)
				password = document.getElementById("main-pass-input").value
				buildTableView()
			catch err
				console.log(err)
				document.getElementById("info-p").innerHTML = "Invalid main password!"
		, () ->
			console.log("Erreur pendant le chargement de la base de données.\n")
			document.getElementById("info-p").innerHTML = "Unable to load the database"


