var db_url = "db.txt";
var raw_database = undefined;
var database = undefined;

// Immediately start random number generator collector.
sjcl.random.startCollectors();

/**
 * Compress a message (deflate compression). Returns base64 encoded data.
 */
function compress(message) {
    return Base64.toBase64( RawDeflate.deflate( Base64.utob(message) ) );
}

/**
 * Decompress a message compressed with compress().
 */
function decompress(data) {
    return Base64.btou( RawDeflate.inflate( Base64.fromBase64(data) ) );
}

/**
 * JSON stringify, then encrypt a message with key.
 */
function cipher(key, message) {
    return sjcl.encrypt(key, JSON.stringify(message));
}

/**
 * Decrypt message with key, then JSON parse
 */
function decipher(key, data) {
    return JSON.parse(sjcl.decrypt(key, data));
}


/**
 * Empty the main tag
 */
function emptyMain() {
    var myNode = document.getElementsByTagName("main")[0];
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
}


/**
 * Build the main table view
 */
function buildTableView() {
    emptyMain();

    var html = "<p><a href=\"\" id=\"add-a\">New password</a></p>\
                <table>\
                    <tr>\
                        <th>Site</th>\
                        <th>Password</th>\
                        <th>Edit</th>\
                        <th>Delete</th>\
                    </tr>";
    for(var i = 0; i < window.database.length; i++) {
        html += "<tr>\
                    <td>TODO</td>\
                    <td>" + window.database[i].password + "</td>\
                    <td><a class=\"edit-a\" href=\"\">Edit</a></td>\
                    <td><a class=\"delete-a\" href=\"\">Delete</a></td>\
                </tr>";
    }
    html += "</table>";
    document.getElementsByTagName("main")[0].innerHTML = html;

    // Bind events
    document.getElementById("add-a").addEventListener("click", function (evt) {
        evt.preventDefault();
        buildAddView();
    });
}


/**
 * Build the add a new password view
 */
function buildAddView() {
    emptyMain();

    var html = "<form>";
    html += "</form>";

    document.getElementsByTagName("main")[0].innerHTML = html;
}


// Download the passwords database
var req = new XMLHttpRequest();
req.open('GET', db_url, true);
req.onreadystatechange = function (aEvt) {
    if (req.readyState == 4) {
        if(req.status == 200) {
            window.raw_database = req.responseText;
            document.getElementById("info-p").innerHTML = "";
            document.querySelector("#main-pass-form input[type=submit]").removeAttribute("disabled");
        }
        else {
            console.log("Erreur pendant le chargement de la base de données.\n");
            document.getElementById("info-p").innerHTML = "Unable to load the database";
        }
    }
};
req.send(null);


document.getElementById("main-pass-form").addEventListener("submit", function (evt) {
    evt.preventDefault();

    if (window.raw_database === undefined) {
        return;
    }

    try {
        window.database = decipher(document.getElementById("main-pass-input").value, window.raw_database);
    } catch(err) {
        console.log(err);
        document.getElementById("info-p").innerHTML = "Invalid main password!";
        return;
    }

    buildTableView();
});
