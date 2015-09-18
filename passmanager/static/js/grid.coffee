console.log("test")
for input in document.querySelectorAll(".grid-form input[type=checkbox]")
	input.addEventListener "click", () ->
		this.parentNode.submit()
	console.log("bbb")
