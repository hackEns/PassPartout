// Generated by CoffeeScript 1.9.0
(function() {
  var input, _i, _len, _ref;

  console.log("test");

  _ref = document.querySelectorAll(".grid-form input[type=checkbox]");
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    input = _ref[_i];
    input.addEventListener("click", function() {
      return this.parentNode.submit();
    });
    console.log("bbb");
  }

}).call(this);
