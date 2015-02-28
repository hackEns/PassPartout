cipher = (key, message) ->
	sjcl.encrypt(key, JSON.stringify(message))

document.getElementById("new-form").addEventListener "submit", () ->
	password_input = document.getElementById("main-pass-input")
	data_input = document.getElementById("data-hidden")
	data_input.value = cipher password_input.value, []
	password_input.value = ""
	this.submit()
