db_url = "static/db.txt"
raw_database = undefined
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


# Empty the main tag
emptyMain = () ->
	myNode = document.getElementsByTagName("main")[0]
	myNode.removeChild c for c in myNode.children

# Build the main table view
buildTableView = () ->
	emptyMain()

	html = "<p><a href=\"\" id=\"add-a\">New password</a></p>\
				<table>\
					<tr>\
						<th>Site</th>\
						<th>Password</th>\
						<th>Edit</th>\
						<th>Delete</th>\
					</tr>"
	html += "<tr>\
				<td>TODO</td>\
				<td>" + e.password + "</td>\
				<td><a class=\"edit-a\" href=\"\">Edit</a></td>\
				<td><a class=\"delete-a\" href=\"\">Delete</a></td>\
			</tr>" for e in window.database
	html += "</table>"
	document.getElementsByTagName("main")[0].innerHTML = html

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


# Download the passwords database
req = new XMLHttpRequest()
req.open('GET', db_url, true)
req.onreadystatechange = (aEvt) ->
	if req.readyState = 4
		if req.status = 200
			window.raw_database = req.responseText
			document.getElementById("info-p").innerHTML = ""
			document.querySelector("#main-pass-form input[type=submit]").removeAttribute("disabled")
		else
			console.log("Erreur pendant le chargement de la base de données.\n")
			document.getElementById("info-p").innerHTML = "Unable to load the database"
req.send(null)


document.getElementById("main-pass-form").addEventListener "submit", (evt) ->
	evt.preventDefault()

	if (window.raw_database == undefined)
		return

	try
		window.database = decipher(document.getElementById("main-pass-input").value, window.raw_database)
	catch err
		console.log(err)
		document.getElementById("info-p").innerHTML = "Invalid main password!"
		return

	buildTableView()
